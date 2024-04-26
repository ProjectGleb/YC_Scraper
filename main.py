from playwright.sync_api import sync_playwright
import time
import csv


def login(playwright):
    browser = playwright.firefox.launch(headless=False)  # Use Firefox instead of Chromium
    page = browser.new_page()

    # Navigate to the main page and wait for it to be fully loaded
    page.goto("https://account.ycombinator.com/authenticate?continue=https%3A%2F%2Fwww.workatastartup.com%2F", wait_until='networkidle')
    
    # Proceed with the rest of your login steps...


    # Navigate to the main page and wait for it to be fully loaded
    page.goto("https://account.ycombinator.com/authenticate?continue=https%3A%2F%2Fwww.workatastartup.com%2F", wait_until='networkidle')
 
    # Wait for the username input to appear and type the username
    page.wait_for_selector('#ycid-input')
    page.fill('#ycid-input', '')  # Fill the username

    # Press Tab to switch to the password field or you can directly select it
    page.keyboard.press('Tab')

    # Wait for the password input to appear and type the password
    page.wait_for_selector('#password-input')
    page.fill('#password-input', '')  # Fill the password

    # Optionally, you can find and click the submit button
    login_button = page.query_selector("button.MuiButton-root")  # Use a part of the class name that's unique
    if login_button:
        with page.expect_navigation(wait_until='networkidle'): #nework idle in web is an attribute used to infer that the page finished loading
            login_button.click()

    return page

def filtering(page):
    #POSITION DROPDOWN
    position_dropdown = page.query_selector('.css-yk16xz-control')
    if position_dropdown:
        position_dropdown.click()
        # If clicking the dropdown does not automatically open it, you may need to wait
        # for the options to become visible or for an animation to complete.
    
    # Wait for the option to appear in the DOM and be visible to the user.
    page.wait_for_selector('text=Engineering', state='visible')
    # Click the desired option from the expanded dropdown.
    engineering_option = page.query_selector('text=Engineering')
    if engineering_option:
        engineering_option.click()
        page.keyboard.press('Enter')
        page.keyboard.press('Tab')
        page.keyboard.press('Tab')
        page.keyboard.press('Tab')
        page.keyboard.press('Enter')

    #COMPANY SIZE DROPDOWN
    company_dropdown = page.query_selector('.css-1pahdxg-control')
    if company_dropdown:
        company_dropdown.click()    

    page.wait_for_selector('text=11 - 50 people', state='visible')
    # Click the desired option from the expanded dropdown.
    company_dropdown = page.query_selector('text=11 - 50 people')
    if company_dropdown:
        company_dropdown.click()
        time.sleep(3)

import time

def collect_all_company_links(page):
    collected_dictionaries = []
    base_url = "https://www.workatastartup.com"
    previous_length = 0
    retries = 3  # Number of retries to scroll and check for new content

    while retries > 0:
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(5)  # Wait for the page to load content

        company_elements = page.query_selector_all('.company-name.hover\\:underline')
        current_length = len(company_elements)
        if current_length == previous_length:
            retries -= 1  # Reduce the retries as no new companies were found
        else:
            retries = 3  # Reset retries if new companies are found
        previous_length = current_length

        # Collect data from current set of elements
        for company_element in company_elements:
            title = company_element.inner_text()
            relative_path = page.evaluate('element => element.closest("a").getAttribute("href")', company_element)
            full_url = f"{base_url}{relative_path}"
            if not any(d['url'] == full_url for d in collected_dictionaries):  # Check if URL is already collected
                collected_dictionaries.append({"company_name": title, "url": full_url})

    # Separate loop to visit each company page for founder details
    for company_dict in collected_dictionaries:
        page.goto(company_dict["url"], wait_until='networkidle')
        founder_elements = page.query_selector_all('.mb-1.font-medium')
        linkedin_links = page.query_selector_all('a[href*="linkedin.com/in/"]')

        # Extract and assign founder details
        for index, (founder, link) in enumerate(zip(founder_elements, linkedin_links), start=1):
            full_name = founder.inner_text().split()  # This will split the name into parts
            first_name = full_name[0] if len(full_name) > 0 else ""
            last_name = " ".join(full_name[1:]) if len(full_name) > 1 else ""
            linkedin_url = link.get_attribute('href')
            company_dict[f"founder{index}_first_name"] = first_name
            company_dict[f"founder{index}_last_name"] = last_name
            company_dict[f"founder{index}_linkedin"] = linkedin_url


        print(f"Collected {len(collected_dictionaries)} unique company links so far.")
        print()

    return collected_dictionaries



def main():
    with sync_playwright() as playwright:
        page = login(playwright)
        filtering(page)
        collected_dictionaries = collect_all_company_links(page)

        # Determine the maximum number of founders based on the data collected
        max_founders = max((len([k for k in d if k.startswith("founder")]) // 3) for d in collected_dictionaries)

        # Define the CSV header with separate columns for first and last names
        csv_header = ['company_name', 'url']
        for i in range(1, max_founders + 1):
            csv_header.extend([f'founder{i}_first_name', f'founder{i}_last_name', f'founder{i}_linkedin'])

        # Write the dictionaries to a CSV file
        with open('companies.csv', mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=csv_header)
            writer.writeheader()
            for company in collected_dictionaries:
                row = {key: company.get(key, None) for key in csv_header}
                writer.writerow(row)

        print("CSV file has been created.")


main()

