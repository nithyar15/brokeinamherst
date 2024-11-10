'''
A few steps to use this webscraping tool! This webscraper uses AgentQL, an AI-powered
DOM selection tool. It uses context rather than fixed values to select fields.

This makes the tool super versatile and can be used on various websites with little
changes!

You need to get the api-key from 
https://www.agentql.com/?utm_source=YouTube&utm_medium=Creator&utm_id=Unconv_102024

You will also need to run these commands and input the obtained api-key!
It's fairly straightforward

pip3 install agentql
agentql init

Once that's done you can run this like an ordinary python file!
'''

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import agentql
import csv

def getProducts(url, headless=False) -> list[dict]:
    product_list = []
    max_unstable_attempts = 3
    unstable_attempts = 0

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        page = agentql.wrap(browser.new_page())
        
        page.goto(url)
        page_number = 0

        while True:
            page_number += 1
            
            # Query product data
            try:
                response = page.query_data(""" 
                {
                    products[] {
                        name
                        price_per_count
                        price
                        website_name
                    }
                }
                """)
                product_list += response['products']
            except PlaywrightTimeoutError:
                print(f"Timeout error when querying products on page {page_number}. Breaking loop.")
                break

            # Stop scraping after 3 pages
            if page_number >= 3:
                break

            # Query for the next page link
            try:
                response = page.query_data("""
                {
                    page_selector {
                        next_page_link
                    }
                }
                """)
            except PlaywrightTimeoutError:
                print(f"Timeout error when querying for next page link on page {page_number}. Breaking loop.")
                break

            # Check for and close any popup if present
            try:
                close_popup = page.query_selector("button[aria-label='Close']")
                if close_popup:
                    close_popup.click()
                    page.wait_for_timeout(3000)
            except PlaywrightTimeoutError:
                print("Timeout error when trying to close popup.")

            # Access the next page link
            next_page = response.get("page_selector", {}).get("next_page_link")
            if not next_page:
                print(f"No next page link found on page {page_number}. Ending scraping.")
                break

            # Attempt to click the next page link
            try:
                next_page_element = page.locator(f"a[href='{next_page}']")
                if next_page_element:
                    next_page_element.click()
                    page.wait_for_timeout(2000)
                    unstable_attempts = 0  # Reset if successful
                else:
                    print(f"Next page link not clickable on page {page_number}. Ending scraping.")
                    break
            except (PlaywrightTimeoutError, Exception) as e:
                print(f"Error on page {page_number}: {e}")
                unstable_attempts += 1
                if unstable_attempts >= max_unstable_attempts:
                    print(f"Too many unstable attempts ({unstable_attempts}). Breaking loop.")
                    break

        browser.close()
    
    return product_list

# You can add any URL and the scraper should give you the name, price per count, price and website name
data = getProducts("https://new.aldi.us/results?q=coffee")

csv_file = "products.csv"
with open(csv_file, mode='w', newline='') as file:
    if(len(data) != 0):
        writer = csv.DictWriter(file, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

        print(f"Data successfully saved to {csv_file}")
    else:
        print("Sorry there was an error")
