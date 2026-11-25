from app import app


if __name__ == "__main__":
    app.config["TESTING"] = True
    print("Servidor Playwright: TESTING=True; CAPTCHA de prueba: AB12CD")
    app.run(port=5000)
# & ".\.venv\Scripts\python.exe" .\run_playwright_server.py