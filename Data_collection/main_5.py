import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time

driver = webdriver.Chrome()
driver.maximize_window()

url = "https://www.airlinequality.com/airline-reviews/british-airways/page/1/?sortby=post_date%3ADesc&pagesize=100"
num_pages = 30  # Number of pages to scrape

review_stats_list = []

for page_num in range(num_pages):
    driver.get(url)
    time.sleep(2)  # Add a small delay to allow the page to load

    soup = BeautifulSoup(driver.page_source, "html.parser")
    category_container = soup.find_all('article', {'itemprop': 'review'})

    for text_container in category_container:
        review_stats = text_container.find('div', {'class': 'review-stats'}).find('table', {'class': 'review-ratings'})
        stats_rows = review_stats.find_all('tr')
        stats_data = {}
        for row in stats_rows:
            category_elem = row.find('td', {'class': 'review-rating-header'})
            rating_elems = row.find_all('span', {'class': 'star fill'})
            if category_elem and rating_elems:
                category = category_elem.text.strip()
                rating_count = len(rating_elems)
                stats_data[category] = rating_count
        review_stats_list.append(stats_data)

    next_page_element = driver.find_element(By.XPATH, '//a[contains(@href, "/airline-reviews/british-airways/page/{}/?sortby=post_date%3ADesc&pagesize=100")]'.format(page_num + 2))
    driver.execute_script("arguments[0].click();", next_page_element)  # Simulate clicking on the next page link

    # Wait for the next page to load
    time.sleep(2)

    url = driver.current_url

driver.quit()

df = pd.DataFrame(review_stats_list)

# Save the DataFrame to a CSV file
df.to_csv('review_stats.csv', index=False)


