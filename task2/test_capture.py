import os
import time
import subprocess
import requests
from playwright.sync_api import sync_playwright

def main():
    print("Testing Playwright with Swagger UI...")
    # Clean previous database if exists
    if os.path.exists("events.db"):
        os.remove("events.db")

    # Start uvicorn server
    proc = subprocess.Popen(
        ["python", "-m", "uvicorn", "main:app", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    try:
        # Wait for server to be ready
        for _ in range(30):
            try:
                r = requests.get("http://127.0.0.1:8000/docs", timeout=1)
                if r.status_code == 200:
                    print("Server is up and /docs responded 200!")
                    break
            except Exception:
                time.sleep(0.5)
        else:
            raise RuntimeError("Server failed to start")

        os.makedirs("screenshots", exist_ok=True)

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(viewport={"width": 1280, "height": 900})
            page = context.new_page()

            page.goto("http://127.0.0.1:8000/docs", wait_until="networkidle")
            page.screenshot(path="screenshots/swagger_overview.png")
            print("Captured swagger_overview.png")

            browser.close()

    finally:
        proc.terminate()
        proc.wait()
        print("Server stopped.")

if __name__ == "__main__":
    main()
