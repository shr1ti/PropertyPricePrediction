from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)


driver.get('https://www.magicbricks.com')


WebDriverWait(driver, 15).until(
    EC.presence_of_all_elements_located((By.CLASS_NAME, "mb-home__owner-prop__card--price"))
)


html_content = driver.page_source
print(html_content)  


with open("page_source.html", "w", encoding="utf-8") as f:
    f.write(html_content)


driver.quit()
