import os
import base64
from email.message import EmailMessage
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

class EmailService:
    """
    Service class responsible for handling all outgoing emails via the Gmail API.
    """
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']

    def __init__(self, credentials_path: str = 'credentials.json', token_path: str = 'token.json'):
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service = self._authenticate()

    def _authenticate(self):
        """Authenticates and returns the Gmail API service instance."""
        creds = None
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, self.SCOPES)
            
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path, self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())
                
        return build('gmail', 'v1', credentials=creds)

    def send_verification_email(self, target_email: str, code: str) -> bool:
        """Constructs and sends a verification email."""
        try:
            message = EmailMessage()
            message.set_content(f"Welcome to SUSA! Your Discord verification code is: {code}\n\n"
                                f"Please provide this code to the bot to complete your verification.")
            message['To'] = target_email
            message['From'] = "berkeley.susa@gmail.com" # Update with actual authenticated email
            message['Subject'] = "SUSA Discord Verification Code"

            encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            create_message = {'raw': encoded_message}

            self.service.users().messages().send(userId="me", body=create_message).execute()
            return True
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False