# scrape-sync

Scrape events from a [website](https://reservas.estetical.es) using Playwright 
and use google sheets to store the data.

## Quickstart

1. Create virtual environment

    ```console
    python3 -m venv .venv && source .venv/bin/activate
    ```

2. Install requirements

    ```console
    pip install -r requirements.txt
    ```

3. Install playwright dependencies

    ```console
    playwright install --with-deps
    ```

4. Create google project
5. Create google spread sheet and copy id from url
6. Create `.env` file using as an example[.env.example ](src/.env.example)
7. Run script:

    ```console
    python src/main.py --help
    ```


## References

- [google sheets quickstart](https://developers.google.com/workspace/sheets/api/quickstart/python?hl=es-419)
- [create google project](https://console.cloud.google.com/projectcreate?hl=es-419)
- [configure project public](https://console.cloud.google.com/auth/audience?hl=es-419)
- [create clients](https://console.cloud.google.com/auth/clients) Select "Desktop App"
- [playwright](https://playwright.dev/python/docs/intro)
