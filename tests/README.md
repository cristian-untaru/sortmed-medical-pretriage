# SortMed Test Suite

This folder contains the automated tests used to validate the SortMed application.

The tests are split into three levels:

- `pytest` tests for backend logic, including input validation, model configuration, prediction helpers, MedQuAD retrieval and database persistence.
- `Streamlit AppTest` tests for the main Streamlit page, without opening a real browser.
- `Playwright` tests for the real browser flow. These are end-to-end tests and require the app to be running locally.

## 1. Install test dependencies

Activate the local virtual environment, then install the test dependencies once inside the project folder:

```powershell
.\venv\Scripts\Activate.ps1
```

```powershell
python -m pip install -r requirements-dev.txt
```

Playwright also needs a local Chromium browser. Install it once with:

```powershell
python -m playwright install chromium
```

## 2. Run the regular test suite

These tests cover the backend and Streamlit AppTest layer. They do not require the app to be started manually.

```powershell
python -m pytest
```

Expected result:

```text
All regular tests should pass.
```

The skipped test is the Playwright end-to-end suite, which is run separately.

## 3. Run the browser end-to-end tests

Use two terminals.

In the first terminal, start the Streamlit app:

```powershell
streamlit run app.py --server.port 8501
```

Leave this terminal open.

In the second terminal, set the app URL and run only the end-to-end tests:

```powershell
$env:SORTMED_E2E_BASE_URL="http://localhost:8501"
python -m pytest -m e2e
```

Expected result:

```text
All selected end-to-end tests should pass.
```

If Streamlit starts on another port, update `SORTMED_E2E_BASE_URL` accordingly. For example:

```powershell
$env:SORTMED_E2E_BASE_URL="http://localhost:8502"
```
