import csv
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

def setup_chrome():
    """Setup Chrome with custom options"""
    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-features=UseSkiaRenderer,UseOzonePlatform")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.maximize_window()
    return driver

def scroll_page(driver):
    """Scroll the page to load more results"""
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    for _ in range(3):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def search_properties(locality, csv_writer):
    """Search and extract property details for a given locality and save to CSV"""
    try:
        print(f"\nSearching for properties in {locality}...")
        driver = setup_chrome()
        wait = WebDriverWait(driver, 20)
        
        url = f"https://www.magicbricks.com/flats-for-rent-in-gurgaon-pppfr"
        driver.get(url)
        time.sleep(5)
        
        scroll_page(driver)
        
        try:
            property_cards = wait.until(EC.presence_of_all_elements_located(
                (By.XPATH, "//div[contains(@class, 'mb-srp__card')]")))
            
            if property_cards:
                properties_found = 0
                for card in property_cards:
                    try:
                        title = card.find_element(By.XPATH, ".//h2[contains(@class, 'mb-srp__card--title')]").text.lower()
                        bhk_match = re.search(r'(\d+)\s*bhk', title)
                        price = card.find_element(By.XPATH, ".//div[contains(@class, 'mb-srp__card__price--amount')]").text
                        furnishing = card.find_element(By.XPATH, ".//div[@data-summary='furnishing']/div[@class='mb-srp__card__summary--value']").text
                        
                        if bhk_match and 'lac' not in price.lower():
                            bhk_num = bhk_match.group(1)
                            price = price.replace("₹", "").replace(",", "").strip()
                            furnishing = furnishing.strip()
                            
                            csv_writer.writerow([locality, bhk_num, price, furnishing])
                            properties_found += 1
                            
                            if properties_found >= 10:
                                break
                    
                    except (NoSuchElementException, AttributeError):
                        continue
            
        except TimeoutException:
            print(f"Timeout while loading properties for {locality}")
            
    except Exception as e:
        print(f"Error while processing {locality}: {str(e)}")
    
    finally:
        try:
            driver.quit()
        except:
            pass

def main():
    localities = ["sector 31" ,"sector 38" ,"sector 39" ,"sector 43" ,"sector 47" ,"sector 48" ,"sector 49" ,"sector 51" ,"sector 52"]
    
    with open("rental_gurg.csv", "w", newline="", encoding="utf-8") as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(["Locality", "BHK", "Price (INR)", "Furnishing"])
        
        for locality in localities:
            search_properties(locality, csv_writer)
            time.sleep(3)

if __name__ == "__main__":
    main()
