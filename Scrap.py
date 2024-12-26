import time
import csv
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# Use headless mode for faster execution
chrome_options = Options()
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920x1080")

driver_path = '/usr/local/bin/chromedriver'
service = Service(driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# Get the current timestamp for the CSV file
timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

driver.get('https://portal-gadekalb.tylertech.cloud/portal/')

# Login steps
dropDown_menu = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'dropdownMenu1')))
dropDown_menu.click()

sign_in_link = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, 'Sign In')))
sign_in_link.click()

# Wait for login page to load and fill the login form
email_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'UserName')))
password_field = driver.find_element(By.ID, 'Password')

email_field.send_keys('dexsteruser0@gmail.com')
password_field.send_keys('Welcome123!q')

checkbox = driver.find_element(By.ID, 'TOSCheckBox')
checkbox.click()

signIn = driver.find_element(By.ID, 'btnSignIn')
signIn.click()

# Smart search
smart_search_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'portlet-29')))
smart_search_button.click()

# Create file to write the results
directory_path = '/Users/kevinkang/data'
file_name = f"{directory_path}/evictions_dekalb_{timestamp}.csv"
error_counter = 0
failed_claims = []  # List to store failed claim IDs for retrying

# Open the CSV file early to ensure it's created and flushed properly
with open(file_name, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Claim Number', 'Case Type', 'Claim Date', 'Claim Status', 'Plaintiff', 'Plaintiff Address', 'Defendant', 'Defendant Address'])  # Write the header row

    try:
        # Loop through claim numbers starting from 41372 and decrementing by 1 to 35000
        for i in range(29455, 25000, -1):  # Starts at 41372 and goes down to 35000
            claim_id = f'24D{str(i).zfill(5)}'
            search = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'caseCriteria_SearchCriteria')))
            search.clear()
            search.send_keys(claim_id)

            submit_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'btnSSSubmit')))
            submit_button.click()

            time.sleep(2)  # Wait for search results to load

            try:
                # Find case type result
                # result = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'party-case-type')))
                # case_type_text = result.text

                print(f"Claim ID: {claim_id} is Dispossessory")

                # if it's dispossessory, click the claim number to go to the claim detail page
                claim_detail_link = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, 'caseLink')))

                print('claim_detail_link', claim_detail_link)
                claim_detail_link.click()

                time.sleep(2)

                # Extract the claim date
                file_date_element = driver.find_element(By.XPATH, "//span[text()='File Date']/parent::p")
                file_date_text = file_date_element.text.strip()
                claim_date = file_date_text.split("\n")[1].strip()

                # Extract the claim status
                case_status_element = driver.find_element(By.XPATH, "//span[text()='Case Status']/parent::p")
                case_status_text = case_status_element.text.strip()
                claim_status = case_status_text.split("\n")[1].strip()

                # Find all elements with class 'text-primary' (Plaintiff, Active Attorneys, Defendant, etc.)
                elements = driver.find_elements(By.CLASS_NAME, 'text-primary')
                plaintiff_name = ''
                attorney_name = ''
                defendant_name = ''

                for element in elements:
                    if element.text == 'Plaintiff':
                        plaintiff_name = driver.execute_script("return arguments[0].nextSibling.textContent;",
                                                               element).strip()
                    elif element.text == 'Defendant':
                        defendant_name += defendant_name + ' ' + driver.execute_script(
                            "return arguments[0].nextSibling.textContent;", element).strip()

                address_label = driver.find_elements(By.XPATH, "//span[text()='Address']")
                plaintiff_address_element = address_label[0].find_element(By.XPATH, "./following-sibling::p")
                plaintiff_address_text = plaintiff_address_element.text.strip()
                plaintiff_cleaned_address = ' '.join(plaintiff_address_text.splitlines())

                defendant_address_element = address_label[1].find_element(By.XPATH, "./following-sibling::p")
                defendant_address_text = defendant_address_element.text.strip()
                defendant_cleaned_address = ' '.join(defendant_address_text.splitlines())

                writer.writerow(
                    [claim_id, 'Dispossessory', claim_date, claim_status, plaintiff_name, plaintiff_cleaned_address,
                     defendant_name.strip(), defendant_cleaned_address])
                file.flush()  # Flush to ensure it's saved

            except Exception as e:
                print(f"Error processing claim ID: {claim_id} ")
                error_counter += 1
                failed_claims.append(claim_id)  # Save failed claim to retry later

            driver.back()  # Go back to the search page
            time.sleep(3)  # Adjust delay based on website speed

            # Break the loop if too many errors occur
            if error_counter >= 4:
                print("Too many errors. Pausing for 10 seconds.")
                time.sleep(10)
                error_counter = 0

        # Retry the failed claims
        print(f"Retrying failed claims: {failed_claims}")
        for claim_id in failed_claims:
            try:
                search = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'caseCriteria_SearchCriteria')))
                search.clear()
                search.send_keys(claim_id)

                submit_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'btnSSSubmit')))
                submit_button.click()

                time.sleep(2)  # Wait for search results to load

                # Find case type result
                result = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'party-case-type')))
                case_type_text = result.text

                if 'Dispossessory*' in case_type_text:
                    print(f"Claim ID: {claim_id} is Dispossessory")

                    # if it's dispossessory, click the claim number to go to the claim detail page
                    claim_detail_link = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, claim_id)))
                    claim_detail_link.click()

                    time.sleep(2)

                    # Extract the claim date
                    file_date_element = driver.find_element(By.XPATH, "//span[text()='File Date']/parent::p")
                    file_date_text = file_date_element.text.strip()
                    claim_date = file_date_text.split("\n")[1].strip()

                    # Extract the claim status
                    case_status_element = driver.find_element(By.XPATH, "//span[text()='Case Status']/parent::p")
                    case_status_text = case_status_element.text.strip()
                    claim_status = case_status_text.split("\n")[1].strip()

                    # Find all elements with class 'text-primary' (Plaintiff, Active Attorneys, Defendant, etc.)
                    elements = driver.find_elements(By.CLASS_NAME, 'text-primary')
                    plaintiff_name = ''
                    attorney_name = ''
                    defendant_name = ''

                    for element in elements:
                        print(element.text)
                        if element.text == 'Plaintiff':
                            plaintiff_name = driver.execute_script("return arguments[0].nextSibling.textContent;",element).strip()
                        elif element.text == 'Defendant':
                            defendant_name += defendant_name + ' ' + driver.execute_script("return arguments[0].nextSibling.textContent;",element).strip()

                    address_label = driver.find_elements(By.XPATH, "//span[text()='Address']")
                    plaintiff_address_element = address_label[0].find_element(By.XPATH, "./following-sibling::p")
                    plaintiff_address_text = plaintiff_address_element.text.strip()
                    plaintiff_cleaned_address = ' '.join(plaintiff_address_text.splitlines())

                    defendant_address_element = address_label[1].find_element(By.XPATH, "./following-sibling::p")
                    defendant_address_text = defendant_address_element.text.strip()
                    defendant_cleaned_address = ' '.join(defendant_address_text.splitlines())

                    writer.writerow([claim_id, case_type_text, claim_date, claim_status, plaintiff_name, plaintiff_cleaned_address, defendant_name.strip(), defendant_cleaned_address])
                    file.flush()  # Flush to ensure it's saved

                else:
                    print(f"Claim ID: {claim_id} is NOT Dispossessory ")

            except Exception as e:
                print(f"Retry failed for claim ID: {claim_id} - {e}")
                writer.writerow([claim_id, 'ERROR', '', ''])
                file.flush()  # Mark the failed claim in the CSV

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    finally:
        driver.quit()  # Ensure driver is always quit properly
        print(f"File '{file_name}' has been saved.")
