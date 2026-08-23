from pathlib import Path
from time import sleep

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

OUT = Path(__file__).parent / "screenshots"
URL = "http://localhost:8501"


def main() -> None:
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1440,1100")
    options.add_argument("--hide-scrollbars")
    drv = webdriver.Chrome(options=options)
    try:
        drv.get(URL)
        WebDriverWait(drv, 50).until(lambda d: "phone-screen" in d.page_source or "HIGH" in d.page_source or "notes" in d.page_source and "card" in d.page_source)
        sleep(8)
        drv.save_screenshot(str(OUT / "01-feedback-pulse.png"))
        for el in drv.find_elements(By.XPATH, "//*[normalize-space()='Copy']"):
            if el.is_displayed():
                el.click()
                break
        sleep(2)
        drv.save_screenshot(str(OUT / "02-copy-studio.png"))
        for el in drv.find_elements(By.XPATH, "//*[normalize-space()='Layouts']"):
            if el.is_displayed():
                el.click()
                break
        sleep(2)
        drv.save_screenshot(str(OUT / "03-layout-lab.png"))
        print("ok")
    finally:
        drv.quit()


if __name__ == "__main__":
    main()
