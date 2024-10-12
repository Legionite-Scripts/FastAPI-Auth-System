import requests
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Your Sendinblue API key from the .env file
BREVO_API_KEY = os.getenv("BREVO_API_KEY")


def send_reset_email(to_email: str, reset_link: str):
    url = "https://api.brevo.com/v3/smtp/email"

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "api-key": BREVO_API_KEY,
    }

    payload = {
        "sender": {
            "email": "samuelonwuka88@gmail.com"
        },  # Use your verified sender email
        "to": [{"email": to_email}],
        "subject": "Password Reset Request",
        "htmlContent": f"<p>Click the link to reset your password: <a href='{reset_link}'>{reset_link}</a></p>",
    }

    # Send the request to the BREVO API
    response = requests.post(url, headers=headers, json=payload)

    # Handle response
    if response.status_code == 201:
        print("Email sent successfully!")
    else:
        print("Error sending email:", response.json())


# Example usage
# send_reset_email("recipient@example.com", "https://your-reset-link.com")
