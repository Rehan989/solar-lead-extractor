from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
from datetime import datetime
import os, csv
from captcha_answer import get_number

def get_session_csv_filepath():
    """
    Creates a unique CSV filename based on current datetime and ensures data directory exists
    """
    data_dir = 'data'
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return os.path.join(data_dir, f'bill_details_{timestamp}.csv')

def read_scn_numbers(filename="SERVICE.txt"):
    """
    Reads SCN numbers from a file where each number is on a new line
    """
    with open(filename, 'r') as file:
        return [line.strip() for line in file if line.strip()]


def solve_captcha(driver):
    """
    Finds and solves the simple math captcha on the page
    Returns the solution as an integer
    """
    try:
        captcha_element = driver.find_element(By.XPATH, "/html/body/div[10]/div/div/div[1]/div/div/div/div[1]/div[1]/div[1]/div/div[1]/p")
        captcha_text = captcha_element.text.strip()
        
        numbers = captcha_text.replace("=", "").split("+")
        num1 = int(numbers[0].strip())
        num2 = int(numbers[1].strip())
        print(f"Solving captcha: {num1} + {num2}")
        return num1 + num2
    except Exception as e:
        print(f"Error solving captcha: {e}")
        return None

def extract_bill_details(driver, scn_number, filter_unit):
    """
    Extracts all bill details from the page and returns them as a dictionary
    """
    bill_details = {}
    
    fields = {
        'service_number': '/html/body/div[10]/div/div/div[2]/div[1]/div/div/div/div[1]/div/div/div[3]/div[1]/table/tbody/tr[1]/td[2]',
        'consumer_name': '/html/body/div[10]/div/div/div[2]/div[1]/div/div/div/div[1]/div/div/div[3]/div[1]/table/tbody/tr[2]/td[2]',
        'section_office': '//td[text()="Section Office"]/following-sibling::td[1]',
        'service_release_date': '//td[text()="Service Release Date"]/following-sibling::td[1]',
        'due_date': '//td[text()="Due Date"]/following-sibling::td[1]',
        'category': '//td[text()="Category"]/following-sibling::td[1]',
        'address': '//td[text()="Address"]/following-sibling::td[1]',
        'ero': '//td[text()="ERO"]/following-sibling::td[1]',
        'bill_date': '//td[text()="Bill Date"]/following-sibling::td[1]',
        'date_of_disconnection': '//td[text()="Date of Disconnection"]/following-sibling::td[1]',
        'reconnection_amount': '//td[text()="Reconnection Amount"]/following-sibling::td[1]',
        'acd_amount': '/html/body/div[10]/div/div/div[2]/div[1]/div/div/div/div[1]/div/div/div[3]/div[1]/table/tbody/tr[8]/td[2]/span',
        'present_bill_amount': '//td[text()="Total Amount (to be paid)"]/following-sibling::td[1]',
        'total_amount': '//td[text()="Total Amount (to be paid)"]/following-sibling::td[1]'
    }
    
    for field, xpath in fields.items():
        try:
            element = driver.find_element(By.XPATH, xpath)
            bill_details[field] = element.text.strip()
        except Exception as e:
            bill_details[field] = "N/A"
            print(f"Error extracting {field}: {e}")
    

    results = get_number(scn_number)

    bill_details.update(results)
        

    # Add filter columns based on total_amount
    try:
        total_amount = float(''.join(filter(str.isdigit, bill_details['total_amount'])))
        bill_details['all_bills'] = 'Yes'
        bill_details['above_500'] = 'Yes' if total_amount > 500 else 'No'
        bill_details['above_1000'] = 'Yes' if total_amount > 1000 else 'No'
    except:
        bill_details['all_bills'] = 'Yes'
        bill_details['above_500'] = 'No'
        bill_details['above_1000'] = 'No'
        
    return bill_details

def save_to_csv(bill_details, csv_filepath):
    """
    Saves the bill details to a CSV file
    """
    file_exists = os.path.isfile(csv_filepath)
    
    with open(csv_filepath, 'a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=bill_details.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(bill_details)

def check_bill_details_for_scn(driver, scn_number, wait, delay, filter_unit, csv_filepath):
    """
    Checks bill details for a single SCN number
    """
    try:
        # Navigate to the website in current tab
        driver.get("https://www.apeasternpower.com/viewBillDetailsMain")
        
        # Wait for the SCN input field and enter SCN number
        scn_input = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//input[contains(@placeholder, 'Enter SCNO/Mobile Number')]")
        ))
        scn_input.send_keys(scn_number)
        
        # Solve and enter captcha
        captcha_solution = solve_captcha(driver)
        if captcha_solution is None:
            print(f"Failed to solve captcha for SCN: {scn_number}")
            return
            
        captcha_input = driver.find_element(By.XPATH, "//input[contains(@placeholder, 'Enter answer')]")
        captcha_input.send_keys(str(captcha_solution))
        
        # Submit and wait for results
        time.sleep(3)
        submit_button = driver.find_element(By.XPATH, "/html/body/div[10]/div/div/div[1]/div/div/div/div[1]/div[1]/div[2]/button")
        submit_button.click()
        
        # Wait for results and extract details
        wait.until(EC.presence_of_element_located((By.XPATH, "//td[contains(text(), 'Service Number')]")))
        time.sleep(delay)
        
        bill_details = extract_bill_details(driver, scn_number, filter_unit)
        total_amount = int(bill_details['total_amount'])
        if total_amount >= filter_unit :
            save_to_csv(bill_details, csv_filepath)
            print(f"Successfully processed SCN: {scn_number}")
        else:
            print(f"Skipped for {scn_number}, total_amount: {total_amount}")
        
        
    except TimeoutException:
        print(f"Page took too long to load for SCN: {scn_number}")
    except Exception as e:
        print(f"Error processing SCN {scn_number}: {e}")

def process_all_scn_numbers():
    """
    Main function to process all SCN numbers from the file
    """
    try:
        # Read SCN numbers from file
        scn_numbers = read_scn_numbers()
        if not scn_numbers:
            print("No SCN numbers found in SERVICE.txt")
            return
            
        # Initialize webdriver once for all SCN numbers
        driver = webdriver.Chrome()
        wait = WebDriverWait(driver, 10)
        
        # Create one CSV file for the entire session
        csv_filepath = get_session_csv_filepath()
        
        # Process each SCN number
        for i, scn_number in enumerate(scn_numbers, 1):
            print(f"\nProcessing SCN {i} of {len(scn_numbers)}: {scn_number}")
            check_bill_details_for_scn(driver, scn_number, wait, 3, csv_filepath)
            
    except Exception as e:
        print(f"An error occurred during processing: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    process_all_scn_numbers()