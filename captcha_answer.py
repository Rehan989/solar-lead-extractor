import requests
import time
import ddddocr
from PIL import Image
import io
from bs4 import BeautifulSoup

def create_session_and_get_captcha():
    """
    Creates a new session and fetches CAPTCHA using the automatically generated session ID.
    Returns the CAPTCHA text, session ID, and session object.
    """
    session = requests.Session()
    try:
        # Make initial request to get JSESSIONID
        initial_response = session.get("https://onlineapp.apeasternpower.com")
        initial_response.raise_for_status()

        # Get the JSESSIONID from session cookies
        jsessionid = session.cookies.get('JSESSIONID')
        
        # Fetch CAPTCHA
        current_time = int(time.time() * 1000)
        captcha_url = f"https://onlineapp.apeasternpower.com/captchaimage?time={current_time}"
        headers = {'Cookie': f'JSESSIONID={jsessionid}'}
        captcha_response = session.get(captcha_url, headers=headers)
        captcha_response.raise_for_status()

        # Save and process the CAPTCHA image
        img = Image.open(io.BytesIO(captcha_response.content))
        img.save('captcha.png')
        ocr = ddddocr.DdddOcr()
        captcha_text = ocr.classification(captcha_response.content)

        return captcha_text, jsessionid, session

    except requests.RequestException as e:
        print(f"Error during request: {e}")
        return None, None, None
    except Exception as e:
        print(f"Error processing request: {e}")
        return None, None, None

def make_post_request(jsessionid, captcha_text, session, scn_number):
    """
    Makes a POST request with the JSESSIONID, CAPTCHA text, and SCN number.
    Extracts the mobile number if available.
    """
    url = "https://onlineapp.apeasternpower.com/nameChangeRegistrationNew"
    headers = {'Cookie': f'JSESSIONID={jsessionid}'}
    data = {'scNumber': scn_number, 'captchatext': captcha_text}

    try:
        response = session.post(url, headers=headers, data=data)
        response.raise_for_status()

        # Parse the HTML response to extract the mobile number
        soup = BeautifulSoup(response.text, "html.parser")
        mobile_td = soup.find("td", string=lambda text: text and "Mobile No." in text)
        if mobile_td:
            mobile_number = mobile_td.find_next("td").get_text(strip=True) if mobile_td else None

            # Extract Pincode
            pincode_td = soup.find("td", string=lambda text: text and "Pincode" in text)
            pincode = pincode_td.find_next("td").get_text(strip=True) if pincode_td else None

            # Extract Door No.
            door_no_td = soup.find("td", string=lambda text: text and "Door No." in text)
            door_no = door_no_td.find_next("td").get_text(strip=True) if door_no_td else None

            # Extract Street
            street_td = soup.find("td", string=lambda text: text and "Street" in text)
            street = street_td.find_next("td").get_text(strip=True) if street_td else None

            # Extract Location
            location_td = soup.find("td", string=lambda text: text and "Location" in text)
            location = location_td.find_next("td").get_text(strip=True) if location_td else None

            # Extract Circle
            circle_td = soup.find("td", string=lambda text: text and "Circle" in text)
            circle = circle_td.find_next("td").get_text(strip=True) if circle_td else None

            # Extract Division
            division_td = soup.find("td", string=lambda text: text and "Division" in text)
            division = division_td.find_next("td").get_text(strip=True) if division_td else None

            # Extract Sub Division
            sub_division_td = soup.find("td", string=lambda text: text and "Sub Division" in text)
            sub_division = sub_division_td.find_next("td").get_text(strip=True) if sub_division_td else None

            # Extract Section
            section_td = soup.find("td", string=lambda text: text and "Section" in text)
            section = section_td.find_next("td").get_text(strip=True) if section_td else None

            # Combine results into a dictionary
            results = {
                "Mobile No.": mobile_number,
                "Pincode": pincode,
                "Door No.": door_no,
                "Street": street,
                "Location": location,
                "Circle": circle,
                "Division": division,
                "Sub Division": sub_division,
                "Section": section,
            }

            return results
        else:
            return None

    except requests.RequestException as e:
        print(f"Error during POST request: {e}")
        return None

def get_number(scn_number):
    """
    Orchestrates the process of creating a session, solving the CAPTCHA, and extracting the mobile number.
    Retries up to 3 times if the mobile number is not found.
    """
    for attempt in range(3):
        print(f"Attempt {attempt + 1} to fetch mobile number...")
        captcha_text, session_id, session = create_session_and_get_captcha()
        if captcha_text and session_id and session:
            print(f"Extracted CAPTCHA text: {captcha_text}")
            print(f"Using session ID: {session_id}")
            results = make_post_request(session_id, captcha_text, session, scn_number)
            if results:
                print(f"Extracted data Number: {results}")
                return results
        else:
            print("Failed to fetch CAPTCHA or session. Retrying...")

    print("Mobile number not found after 3 attempts.")
    return "Not found"

# Example usage:
if __name__ == "__main__":
    scn_number = "1164932172002007"  # Replace with the actual SCN number
    result = get_number(scn_number)
    print(f"Final result: {result}")
