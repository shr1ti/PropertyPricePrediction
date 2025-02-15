import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Configure Selenium WebDriver
options = Options()
options.add_argument("--disable-gpu")  # Disable GPU acceleration
options.add_argument("--disable-software-rasterizer")  # Disable software rasterizer
options.add_argument("--no-sandbox")  # Run without sandbox mode
options.add_argument("--disable-features=UseSkiaRenderer,UseOzonePlatform")  # Extra stability options
#options.add_argument("--headless=new")  # Run headless for stability

# Start WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# Open the website
url = "https://www.magicbricks.com/flats-for-rent-in-bangalore-pppfr"
driver.get(url)

# Initialize WebDriverWait
wait = WebDriverWait(driver, 20)

try:
    # Step 1: Click on the BHK filter dropdown
    print("Opening the BHK filter dropdown...")
    bhk_dropdown = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//div[@class='title-ellipsis' and contains(text(), 'BHK')]"))
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", bhk_dropdown)
    bhk_dropdown.click()
    time.sleep(2)  # Wait for UI to update
    print("BHK filter dropdown opened successfully!")

    # Step 2: Apply the "1 BHK" filter
    print("Applying the '1 BHK' filter...")
    bhk_filter = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//label[contains(text(), '1 BHK')]"))
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", bhk_filter)
    bhk_filter.click()
    time.sleep(2)  # Allow results to update
    print("1 BHK filter applied successfully!")

    # Wait for the results to load
    wait.until(EC.presence_of_element_located((By.XPATH, "//h2[@class='mb-srp__card--title']")))

    # Step 3: Open "More Filters"
    print("Opening 'More Filters'...")
    more_filters = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'more-title') and contains(text(), 'More Filters')]"))
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", more_filters)
    more_filters.click()
    time.sleep(2)  # Allow modal to load
    print("'More Filters' opened successfully!")

    # Step 4: Apply the "Furnished" filter
    print("Applying the 'Furnished' filter...")
    furnished_filter = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//label[contains(text(), 'Furnished')]"))
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", furnished_filter)
    furnished_filter.click()
    time.sleep(2)  # Allow results to update
    print("'Furnished' filter applied successfully!")

    # Wait for the filtered results to load
    wait.until(EC.presence_of_element_located((By.XPATH, "//h2[@class='mb-srp__card--title']")))

    # Step 5: Scrape both Titles (Localities) and Prices
    print("Scraping filtered property titles and prices...")
    property_data = []

    # Re-fetch elements after filtering
    titles = wait.until(
        EC.presence_of_all_elements_located((By.XPATH, "//h2[@class='mb-srp__card--title']"))
    )
    
    prices = wait.until(
        EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'mb-srp__card__price--amount')]"))
    )

    # Ensure equal number of titles and prices before pairing
    if len(titles) == len(prices):
        for title, price in zip(titles, prices):
            try:
                property_title = title.get_attribute("title").strip()
                property_price = price.text.strip()
                property_data.append(f"{property_title}: {property_price}")
            except:
                continue  # Skip any elements that fail to load
    else:
        print("Warning: Number of titles and prices do not match!")

    # Print formatted results
    print("\nFiltered Properties with Prices:")
    for property_info in property_data:
        print(property_info)

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # Close the WebDriver
    driver.quit()
