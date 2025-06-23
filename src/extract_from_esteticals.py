# pylint: disable=redefined-builtin
# pylint: disable=import-error
import re

from playwright.sync_api import TimeoutError, sync_playwright

from settings import EMAIL, PASSWORD

extracted_events = []


def extract_from_esteticals():

    with sync_playwright() as playwright:

        browser = playwright.chromium.launch(headless=False)

        context = browser.new_context()

        page = context.new_page()

        print("🌎 Ir al sitio...")

        page.goto("https://reservas.estetical.es/login")

        print("⏳ Esperando a que cargue la página...")

        attempts = 0
        loaded_form = False
        while not loaded_form and attempts < 5:
            try:
                page.wait_for_selector("input[type='email']")
                loaded_form = True
            except TimeoutError:
                print("⏳ Esperando a que cargue la página...")
                attempts += 1
                page.reload()

        if not loaded_form:
            print("❌ No se pudo cargar la página")
            return

        print("✅ Página cargada")

        page.query_selector("input[type='email']").fill(EMAIL)
        page.query_selector("input[type='password']").fill(PASSWORD)
        page.get_by_role("button", name="Continuar").click()

        print("✅ Sesión iniciada")

        page.get_by_text("Semana").click()

        print("✅ Vista semanal activada")

        for week in range(1, 13):

            print(f"Semana {week}")

            page.wait_for_selector(".mbsc-schedule-time-cont-inner")

            try:
                page.wait_for_selector(".mbsc-schedule-event")
            except TimeoutError:
                print("❌ No se encontraron citas en esta semana")
                page.get_by_role("button", name="Next page").click()
                continue

            events = page.query_selector_all(".mbsc-schedule-event")

            print(f"🔍 Citas detectadas: {len(events)}")

            for index, event in enumerate(events, start=1):

                try:

                    event.click()

                    service = (
                        page.locator(".modal-body")
                        .get_by_text(re.compile(r"Servicio:.*"))
                        .text_content()
                        .removeprefix("Servicio:")
                        .strip()
                    )

                    date_raw = (
                        page.locator(".modal-body")
                        .get_by_text("Hora")
                        .locator("..")
                        .text_content()
                        .removeprefix("Hora")
                        .split(",")
                    )

                    date = date_raw[0].strip()

                    start_time = date_raw[1].split("-")[0].strip()

                    therapist = (
                        page.locator(".modal-body")
                        .get_by_text("Emplead@", exact=True)
                        .locator("..")
                        .text_content()
                        .removeprefix("Emplead@")
                    )
                    patient = (
                        page.locator(".modal-body")
                        .get_by_text("Usuari@", exact=True)
                        .locator("..")
                        .text_content()
                        .removeprefix("Usuari@")
                    )

                    phone = (
                        page.locator(".modal-body")
                        .get_by_text("Teléfono")
                        .locator("..")
                        .text_content()
                        .removeprefix("Teléfono")
                    )

                    new_event = {
                        "id": f"{date}-{therapist}",
                        "date": date,
                        "start_time": start_time,
                        "service": service,
                        "patient": patient,
                        "therapist": therapist,
                        "phone": phone,
                    }

                    if new_event not in extracted_events:

                        print(f"✅ Cita {index} extraída: {new_event}")
                        extracted_events.append(new_event)

                    page.locator(
                        ".modal-content > div > .modal-header > .btn"
                    ).dispatch_event("click")

                except TimeoutError as exc:
                    print(f"⚠️ No se pudo extraer la cita {index}: {exc.message} ")

            page.get_by_role("button", name="Next page").click()

        context.close()

    return extracted_events
