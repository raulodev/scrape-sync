# pylint: disable=redefined-builtin
# pylint: disable=import-error
import re

from playwright.sync_api import TimeoutError, sync_playwright

from settings import EMAIL, PASSWORD

citas_extraidas = []


def extract_from_esteticals():

    with sync_playwright() as playwright:

        browser = playwright.chromium.launch(headless=False)

        context = browser.new_context()

        context.set_default_timeout(60 * 1000)

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

        page.wait_for_selector(".mbsc-schedule-time-cont-inner")
        page.wait_for_selector(".mbsc-schedule-event")

        events = page.query_selector_all(".mbsc-schedule-event")

        print(f"🔍 Citas detectadas: {len(events)}")

        for event in events:

            event.click()

            servicio = (
                page.locator(".modal-body")
                .get_by_text(re.compile(r"Servicio:.*"))
                .text_content()
                .removeprefix("Servicio:")
                .strip()
            )

            if servicio.lower() in ["", "bloqueado"]:
                continue

            fecha = (
                page.locator(".modal-body")
                .get_by_text("Hora")
                .locator("..")
                .text_content()
                .removeprefix("Hora")
            )

            terapeuta = (
                page.locator(".modal-body")
                .get_by_text("Emplead@", exact=True)
                .locator("..")
                .text_content()
                .removeprefix("Emplead@")
            )
            paciente = (
                page.locator(".modal-body")
                .get_by_text("Usuari@", exact=True)
                .locator("..")
                .text_content()
                .removeprefix("Usuari@")
            )

            telefono = (
                page.locator(".modal-body")
                .get_by_text("Teléfono")
                .locator("..")
                .text_content()
                .removeprefix("Teléfono")
            )

            citas_extraidas.append(
                {
                    "id": f"{fecha}-{terapeuta}",
                    "date": fecha,
                    "service": servicio,
                    "patient": paciente,
                    "therapist": terapeuta,
                    "phone": telefono,
                }
            )

            page.locator(".modal-content > div > .modal-header > .btn").click()

        context.close()

    return citas_extraidas
