import re
import random
import discord
from core.command import BaseCommand
from services.email_service import EmailService
from services.db_service import DatabaseService

class VerifyCommand(BaseCommand):
    """
    Command to initiate the verification process for a user.
    """
    # Regex to ensure valid formatting and the specific domain
    BERKELEY_EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9_.+-]+@berkeley\.edu$")

    def __init__(self, email_service: EmailService, db_service: DatabaseService):
        self.email_service = email_service
        self.db_service = db_service

    async def execute(self, interaction: discord.Interaction, email: str, first_name: str) -> None:
        """
        Validates the email, generates a code, and triggers the email service.
        """
        # 1. Validation
        if not self.BERKELEY_EMAIL_PATTERN.match(email):
            await interaction.response.send_message(
                "❌ Invalid email format. You must use a valid `@berkeley.edu` email address.", 
                ephemeral=True
            )
            return

        # 2. Acknowledge interaction (Gmail API can be slow, avoid Discord timeout)
        await interaction.response.defer(ephemeral=True)

        # 3. Generate Code
        verification_code = str(random.randint(100000, 999999))
        user_id = interaction.user.id
        
        # 4. Execute Receiver Logic
        success = self.email_service.send_verification_email(email, verification_code)

        # 5. Handle State and Feedback
        if success:
            # Pass the first_name to the database
            self.db_service.store_pending_verification(user_id, email, first_name, verification_code)
            
            await interaction.followup.send(
                f"✅ A verification code has been sent to **{email}**. "
                f"Please check your inbox (and spam folder) and submit the code using the `/code` command."
            )
        else:
            await interaction.followup.send(
                "❌ There was an internal error sending the email. Please contact an administrator."
            )