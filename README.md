# Bill Details Scraper with Authentication

This Streamlit application scrapes bill details using service numbers and now includes user authentication.

## Setup

1. Install required packages:
   ```
   pip install -r requirements.txt
   ```

2. Authentication:
   - The application uses `streamlit-authenticator` for user authentication
   - Default credentials are stored in `config.yaml`:
     - Username: `admin` / Password: `admin123`
     - Username: `user1` / Password: `password123`
   - User Registration:
     - New users can register via the Register tab
     - Only emails listed in the `preauthorized` section of `config.yaml` can register
     - To add more preauthorized emails, update the `config.yaml` file
   - To add users manually, use the `generate_password.py` script:
     ```
     python generate_password.py
     ```
   - Then add the user details to `config.yaml`

3. Run the application:
   ```
   streamlit run main.py
   ```

## Usage

1. Log in with your credentials
2. Choose one of the two methods to input service numbers:
   - Generate a sequence of service numbers from a starting point
   - Upload a SERVICE.txt file containing service numbers
3. Set the delay between requests and filter threshold
4. Click "Start Processing" to begin scraping
5. Results will be displayed and can be downloaded as a CSV file

## Security Note

For production use, please:
- Change default passwords
- Use a more secure cookie key
- Consider implementing additional security measures 