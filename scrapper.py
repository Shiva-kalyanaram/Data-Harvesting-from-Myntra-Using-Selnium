import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import re
import pandas as pd
from selenium.common.exceptions import NoSuchElementException

# Function to collect hyperlinks from a page
def collect_hyperlinks(main_url, num_pages=1):
    driver = webdriver.Chrome()
    driver.get(main_url)
    time.sleep(5)

    url_list = []

    for _ in range(num_pages):
        elements = driver.find_elements(By.XPATH, '//ul[@class="results-base"]/li//a[@href]')
        url_list.extend([element.get_attribute('href') for element in elements])

        # Navigate to the next page if available
        next_button = driver.find_element(By.CLASS_NAME, 'pagination-next')
        if next_button.is_enabled():
            next_button.click()
            time.sleep(5)
        else:
            break

    driver.quit()
    return url_list

# Function to gather details from a hyperlink
def get_details(url):
    driver = webdriver.Chrome()
    driver.get(url)
    time.sleep(5)

    data_dict = {}

    try:
        element = driver.find_element(By.XPATH, '//div[@class="pdp-price-info"]')

        data_dict['Product Name'] = element.find_element(By.XPATH, './/h1').text
        data_dict['Product Description'] = element.find_element(By.XPATH, '//*[@id="mountRoot"]/div/div[1]/main/div[2]/div[2]/div[1]/h1[2]').text
        data_dict['Discounted Price'] = element.find_element(By.XPATH, '//*[@id="mountRoot"]/div/div[1]/main/div[2]/div[2]/div[1]/div/p[1]/span[1]/strong').text
        data_dict['Original Price'] = element.find_element(By.XPATH, '//*[@id="mountRoot"]/div/div[1]/main/div[2]/div[2]/div[1]/div/p[1]/span[2]/s').text
        data_dict['Discount Percentage'] = element.find_element(By.XPATH, '//*[@id="mountRoot"]/div/div[1]/main/div[2]/div[2]/div[1]/div/p[1]/span[3]').text
        elements_rating = element.find_elements(By.XPATH, '//div[@class="user-review-userReviewWrapper "]')
        user_ratings = []
        for element_rating in elements_rating:
            user_rating = int(element_rating.find_element(By.CLASS_NAME, 'user-review-starRating').text)
            user_ratings.append(user_rating)
        data_dict['Customer Rated Rating'] = user_ratings
        elements_text = element.find_elements(By.XPATH, '//div[@class="user-review-reviewTextWrapper"]')
        reviews_list = [i.text for i in elements_text]
        data_dict['Customer Review Test'] = reviews_list

        names_list = []
        review_posted_dates = []

        elements_Name = element.find_elements(By.XPATH, '//div[@class="user-review-left"]/span[1]')
        names_list = [review_element.text for review_element in elements_Name]
        data_dict['Reviewers Name'] = names_list

        elements_date = element.find_elements(By.XPATH, '//div[@class="user-review-left"]/span[2]')
        review_posted_dates = [date_element.text for date_element in elements_date]
        data_dict['Review_posted_dates'] = review_posted_dates

    except NoSuchElementException as e:
        print(f"Element not found: {e}")

    finally:
        driver.quit()

    return data_dict

# Main program
main_url = 'https://www.myntra.com/men-tshirts'
num_pages_to_collect = 10  # Set the number of pages to collect hyperlinks

hyperlinks = collect_hyperlinks(main_url, num_pages=num_pages_to_collect)

all_data = []
for link in hyperlinks:
    details = get_details(link)
    all_data.append(details)

# Create a DataFrame from the collected data
df = pd.DataFrame(all_data)
print(df)
