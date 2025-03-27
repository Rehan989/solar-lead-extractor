import streamlit as st
import pandas as pd
import os
import yaml
import streamlit_authenticator as stauth
from yaml.loader import SafeLoader

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bill_scraper import check_bill_details_for_scn, WebDriverWait, get_session_csv_filepath

# Load authentication credentials
with open("config.yaml") as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"],
    config["preauthorized"],
)

# Authentication
name, authentication_status, username = authenticator.login(
    location='main',
    fields={'Form name': 'Login'}
)

if authentication_status:
    st.sidebar.title(f"Welcome {name}")
    authenticator.logout("Logout", "sidebar")

    def generate_service_numbers(start_number, count):
        """Generate a list of service numbers starting from the given number"""
        try:
            start = int(start_number)
            return [str(start + i) for i in range(count)]
        except ValueError:
            st.error("Invalid service number format")
            return []

    def main():
        st.title("Bill Details Scraper")
        st.write("Upload a file with service numbers or generate them from a starting point")

        # Create two tabs
        tab1, tab2 = st.tabs(["Generate Service Numbers", "File Upload"])

        with tab1:
            st.header("Generate Service Numbers")
            start_number = st.text_input("Enter starting service number")
            count = st.number_input("Number of service numbers to generate", 
                                  min_value=1, max_value=1000, value=100)
            if start_number:
                service_numbers = generate_service_numbers(start_number, count)
                st.write(f"Will generate {count} service numbers starting from {start_number}")

        with tab2:
            st.header("Upload Service Numbers File")
            uploaded_file = st.file_uploader("Choose a SERVICE.txt file", type="txt")
            if uploaded_file:
                service_numbers = [line.decode("utf-8").strip() for line in uploaded_file]
                st.write(f"Found {len(service_numbers)} service numbers")

        delay = st.number_input("Delay in seconds", min_value=1, max_value=1000, value=3)
        filter_unit = st.number_input("Filter Total bill amount", min_value=1, max_value=1000*100000000, value=100)

        if st.button("Start Processing"):
            if 'service_numbers' not in locals():
                st.error("Please either upload a file or provide a starting service number")
                return

            progress_bar = st.progress(0)
            status_text = st.empty()

            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")

            try:
                driver = webdriver.Chrome(options=chrome_options)
                wait = WebDriverWait(driver, 10)

                csv_filepath = get_session_csv_filepath()

                for idx, scn in enumerate(service_numbers):
                    status_text.text(f"Processing service number {scn} ({idx + 1}/{len(service_numbers)})")
                    check_bill_details_for_scn(driver, scn, wait, delay, filter_unit, csv_filepath)
                    progress_bar.progress((idx + 1) / len(service_numbers))

                driver.quit()
                st.success("Processing completed!")

                if os.path.exists(csv_filepath):
                    df = pd.read_csv(csv_filepath)
                    st.write("Latest Results:")
                    st.dataframe(df)

                    st.download_button(
                        label="Download Results CSV",
                        data=df.to_csv(index=False).encode('utf-8'),
                        file_name=os.path.basename(csv_filepath),
                        mime='text/csv',
                    )

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                if 'driver' in locals():
                    driver.quit()

    if __name__ == "__main__":
        main()

elif authentication_status is False:
    st.error("Username/password is incorrect")
elif authentication_status is None:
    st.warning("Please enter your username and password")
