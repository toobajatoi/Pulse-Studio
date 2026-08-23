from pathlib import Path
from time import sleep

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

OUT = Path(__file__).parent / "screenshots"


def main():
    o = Options()
    o.add_argument("--headless=new")
    o.add_argument("--window-size=1440,1100")
    o.add_argument("--hide-scrollbars")
    b = webdriver.Chrome(options=o)
    try:
        b.get("http://localhost:8787/index.html?v=3")
        WebDriverWait(b, 15).until(lambda d: "Careem Studio" in d.page_source)
        sleep(1)
        b.save_screenshot(str(OUT / "studio-home.png"))

        b.get("http://localhost:8787/canvas.html?v=3")
        WebDriverWait(b, 15).until(lambda d: "Ask the canvas" in d.page_source)
        sleep(1.2)
        b.save_screenshot(str(OUT / "studio-understand.png"))

        b.find_element(By.CSS_SELECTOR, "[data-dir='transparency']").click()
        sleep(1)
        b.save_screenshot(str(OUT / "studio-canvas.png"))

        b.find_element(By.CSS_SELECTOR, "[data-lang='ar']").click()
        sleep(0.6)
        b.save_screenshot(str(OUT / "studio-ar.png"))
        print("ok")
    finally:
        b.quit()


if __name__ == "__main__":
    main()
