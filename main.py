from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
from webdriver_manager.chrome import ChromeDriverManager



def main():
    # a list of URLs to scrape
    urls = [
        'https://www.skf.com/in/products/rolling-bearings/ball-bearings/self-aligning-ball-bearings',
        'https://www.skf.com/in/products/rolling-bearings/ball-bearings/thrust-ball-bearings'
        # Add more URLs here
    ]
    # Loop through the URLs and scrape each one
    for url in urls:
        df = scrape_all_pages(url)

        # Save the data to a file
        saveData(df, url)


def get_table_data(driver):
    """Function to scrape table data from the current page."""
    # Wait for the JavaScript to render the table
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'table')))
    # Get the page source and parse with BeautifulSoup
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table', {'class': 'table-sm table-striped table-bordered'})
    rows = table.find_all('tr')
    data = []
    for row in rows:
        cols = row.find_all(['th', 'td'])
        cols = [ele.text.strip() for ele in cols]
        data.append(cols)
    return data

def navigate_to_next_page(driver):
    """Function to click the next page button."""
    try:
        # Scroll to the element and wait for it to be clickable
        next_button_selector = "div[rel='next']"
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, next_button_selector)))

        # Scroll into view (optional, if necessary)
        next_button = driver.find_element(By.CSS_SELECTOR, next_button_selector)
        driver.execute_script("arguments[0].scrollIntoView(true);", next_button)

        # Wait a bit for scrolling to finish and any possible overlays to disappear
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, next_button_selector)))

        next_button.click()
        return True
    except Exception as e:
        try:
            # If the above method fails, try clicking the next button using JavaScript
            driver.execute_script("arguments[0].click();", next_button)
            return True
        except:
            return False
        return False

def scrape_all_pages(url):
    """Main function to scrape tables from all pages."""
    # Setup WebDriver
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    driver.get(url)

    all_data = []  # List to hold data from all pages
    i = 0
    while True:
        # Scrape data from the current page
        data = get_table_data(driver)
        if i == 0:
            # drop row 0 and 1
            data = data[2:]
        else:
            #drop row 0, 1 and 2
            data = data[3:]
        all_data.extend(data)  # Add data from the current page
        i += 1
        if not navigate_to_next_page(driver):
            break  # Exit loop if no next page

    driver.quit()  # Close the browser

    # Convert all collected data into a DataFrame
    df = pd.DataFrame(all_data)

    #make the first row as header
    df.columns = df.iloc[0]

    #drop the first row
    df = df.drop([0])

    # Process 'df' as needed (e.g., setting headers)
    return df


def saveData(df, url):
    #rename first df column to 'Product'
    df.rename(columns={df.columns[0]: 'Product'}, inplace=True)

    # create file path and name based on last 3 parts of url
    file_path = url.split('/')[-3:]

    #dump data to csv
    df.to_csv(f'{"_".join(file_path)}.csv', index=False)


if __name__ == '__main__':
    main()



