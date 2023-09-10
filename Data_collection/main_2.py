import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time

driver = webdriver.Chrome()
driver.maximize_window()

url = "https://www.airlinequality.com/airline-reviews/british-airways/page/1/?sortby=post_date%3ADesc&pagesize=100"
num_pages = 30  # Number of pages to scrape

header_texts = []
sub_header_texts = []
brief_texts = []
review_stats_list = []

rating_categories = set()  # To store unique rating categories

for page_num in range(num_pages):
    driver.get(url)
    time.sleep(2)  # Add a small delay to allow the page to load

    soup = BeautifulSoup(driver.page_source, "html.parser")
    category_container = soup.find_all('article', {'itemprop': 'review'})

    for text_container in category_container:
        header_text = text_container.find('div', {'class': 'body'}).find('h2', {'class': 'text_header'}).text
        header_texts.append(header_text)

        sub_header_text = text_container.find('div', {'class': 'body'}).find('h3', {'class': 'text_sub_header userStatusWrapper'})
        sub_header_texts.append(sub_header_text.text if sub_header_text else "")  # Use empty string if subheader text is not found

        brief_text = text_container.find('div', {'class': 'tc_mobile'}).find('div', {'itemprop': 'reviewBody'}).text
        brief_texts.append(brief_text)

        review_stats = text_container.find('div', {'class': 'review-stats'}).find('table', {'class': 'review-ratings'})
        stats_rows = review_stats.find_all('tr')
        stats_data = {}
        for row in stats_rows:
            category_elem = row.find('td', {'class': 'review-rating-header'})
            rating_elem = row.find('td', {'class': 'review-value'})
            if category_elem and rating_elem:
                category = category_elem.text.strip()
                rating = rating_elem.text.strip()
                stats_data[category] = rating
                rating_categories.add(category)
        review_stats_list.append(stats_data)

    next_page_element = driver.find_element(By.XPATH, '//a[contains(@href, "/airline-reviews/british-airways/page/{}/?sortby=post_date%3ADesc&pagesize=100")]'.format(page_num + 2))
    driver.execute_script("arguments[0].click();", next_page_element)  # Simulate clicking on the next page link

    # Wait for the next page to load
    time.sleep(2)

    url = driver.current_url

driver.quit()

# Create a dictionary to store data for DataFrame
data = {
    'Header Text': header_texts,
    'Subheader Text': sub_header_texts,
    'Brief Text': brief_texts,
}

# Add columns for each unique rating category
for category in rating_categories:
    data[category] = [review_stats.get(category, "") for review_stats in review_stats_list]

df = pd.DataFrame(data)
df.to_csv('airline_reviews_oo1.csv', index=False)
