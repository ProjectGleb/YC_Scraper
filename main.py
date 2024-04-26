from playwright.sync_api import sync_playwright
import time
import csv

def scrape_founder_page(page):
    linkedin_links = page.query_selector_all('a[href*="linkedin.com/in/"]')
    linkedin_urls = [link.get_attribute('href') for link in linkedin_links]
    return linkedin_urls

def login(playwright):
    browser = playwright.chromium.launch(headless=False)
    page = browser.new_page()

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

    page.wait_for_selector('text=1 - 10 people', state='visible')
    # Click the desired option from the expanded dropdown.
    company_dropdown = page.query_selector('text=1 - 10 people')
    if company_dropdown:
        company_dropdown.click()
        time.sleep(3)


    #out of x amount of fields, click on the one with the current count. increment the count by one. 
    
import time

#COMPANY NAME PRINTER
# def comany_names(page):
#     companys = page.query_selector_all('.company-name.hover\:underline')
#     for company in companys:
#         title = company.inner_text()
#         print(title)

def collect_all_company_links(page):
    collected_dictionaries = []  # Using a list to store dictionaries for each company
    base_url = "https://www.workatastartup.com"
    previous_length = 0  # To keep track of the previous iteration company count

    while True:
        # Scroll to the bottom of the page to trigger loading of new content
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        # Wait for the page to load new content. This time may need to be adjusted.
        time.sleep(5)  # Adjust this time based on the network speed and site response time

        # Grab the company elements again after new content loads
        company_elements = page.query_selector_all('.company-name.hover\\:underline')

        # Check if new companies were loaded by comparing lengths
        current_length = len(company_elements)
        if current_length == previous_length:
            # No new companies were loaded, so we can break the loop
            break
        previous_length = current_length

        # Collect the new links and add them to the list of dictionaries
        for company_element in company_elements:
            relative_path = page.evaluate('element => element.closest("a").getAttribute("href")', company_element)
            full_url = f"{base_url}{relative_path}"
            company_dict = {"url": full_url}  # Create a dictionary for the company
            collected_dictionaries.append(company_dict)


            #GOES TO URL TO SCRAPE LINKED
            page.goto(f"{full_url}", wait_until='networkidle')
            # Use the correct contains selector for LinkedIn URLs and set a timeout
            try:
                page.wait_for_selector('a[href*="linkedin.com/in/"]', timeout=30000) # Adjust the timeout as needed
            except Exception as e:
                print(f"LinkedIn link not found on page {full_url}: {e}")
                continue  # Skip to the next URL if LinkedIn link is not found within the timeout


            linkedin_links = page.query_selector_all('a[href*="linkedin.com/in/"]')
            linkedin_urls = [link.get_attribute('href') for link in linkedin_links]
            print(linkedin_urls)
            break

        # Print how many unique links have been collected so far
        print(f"Collected {len(collected_dictionaries)} unique company links so far.")
        print()
        break

    return (collected_dictionaries)



def collect_linkedins(url_list, page, collected_dictionaries):
    for url in url_list:
        page.goto(f"{url}", wait_until='networkidle')

        # Use the correct contains selector for LinkedIn URLs and set a timeout
        try:
            page.wait_for_selector('a[href*="linkedin.com/in/"]', timeout=30000) # Adjust the timeout as needed
        except Exception as e:
            print(f"LinkedIn link not found on page {url}: {e}")
            continue  # Skip to the next URL if LinkedIn link is not found within the timeout

        linkedin_links = page.query_selector_all('a[href*="linkedin.com/in/"]')
        linkedin_urls = [link.get_attribute('href') for link in linkedin_links]
        print(linkedin_urls)



        #open url
        #scraaaaaape

url_list = [ "https://www.workatastartup.com/companies/nimble","https://www.workatastartup.com/companies/curri" ]


def main():
    with sync_playwright() as playwright:
        page = login(playwright)  # This now holds the page object
        filtering(page)           # Pass the page object to the filtering function

        collected_dictionaries = collect_all_company_links(page)  # Collect all company links

        print(collected_dictionaries)      # Print the collected company links
        collect_linkedins(url_list, page)

main()




#im getting the company link. the founder link. 
#i need: 
#startup name √ 
# founder name 1, 2, 3 

#EVERY COMPANY NAME SHOULD HAVE A COUNTER. after the loop is complete, counter should go up

#SOOOOOOORT


#####for every company create a dictionary. append company name to it. append company link to it. append founders names to it. append founders linke in 

# # Write data to CSV
# csv_columns = ['company_url', 'linkedin_urls', 'company_name', 'founder_names']
# csv_file = "Companies_and_Founders.csv"
# try:
#     with open(csv_file, 'w', newline='') as csvfile:
#         writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
#         writer.writeheader()
#         for data in companies_data:
#             writer.writerow(data)
# except IOError:
#     print("I/O error writing to CSV")
