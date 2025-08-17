from playwright.sync_api import sync_playwright
import time
import os
from dotenv import load_dotenv

load_dotenv()
EMAIL = os.getenv("SPEECHIFYUSER", "")
PASSWORD = os.getenv("SPEECHIFYPASS", "")


from urllib.parse import urlparse

def log_request(request):
    parsed = urlparse(request.url)
    if "speechify.com" not in parsed.netloc or "/v3/" not in parsed.path:
        return  # ❌ Skip non-API or non-speechify requests


    auth_header = request.headers.get("authorization")
    with open("bearer.txt", "w") as file:
        file.write(auth_header)
    print('bearer added')
    


def getBearer():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        context.on("request", log_request)

        page = context.new_page()

        page.goto("https://app.speechify.com/?page=1", timeout=60000)

        page.wait_for_selector("input#email")
        time.sleep(2)

        page.click("input#email")
        page.type("input#email", EMAIL, delay=100)
        page.click("input#password")
        page.type("input#password", PASSWORD, delay=100)

        page.click("button:has-text('Log In')")

        page.wait_for_timeout(10000) 

        print("Current URL:", page.url)


        page.goto("https://app.speechify.com/item/14900b5d-ed85-41c6-87b4-f1fcab098c51", timeout=60000)

        time.sleep(5)

        browser.close()


if __name__=='__main__':
    getBearer()