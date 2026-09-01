import discord
from discord.ext import commands
from discord import app_commands

from services.email_service import EmailService
from services.db_service import DatabaseService
from commands.verify import VerifyCommand
from commands.submit_code import SubmitCodeCommand

class SUSABot(commands.Bot):
    def __init__(self, verified_role_id: int):
        super().__init__(command_prefix="!", intents=discord.Intents.default())
        
        # 1. Initialize Receivers/Services
        self.email_service = EmailService()
        self.db_service = DatabaseService()
        
        # 2. Initialize Commands (Injecting Dependencies)
        self.verify_cmd = VerifyCommand(self.email_service, self.db_service)
        self.submit_cmd = SubmitCodeCommand(self.db_service, verified_role_id)

    async def setup_hook(self):
        """Map the OOP commands to the Discord app command tree and sync."""
        
        @self.tree.command(name="verify", description="Verify your UC Berkeley student status.")
        @app_commands.describe(email="Your @berkeley.edu email address", first_name="Your real first name")
        async def verify(interaction: discord.Interaction, email: str, first_name: str):
            await self.verify_cmd.execute(interaction, email=email, first_name=first_name)

        @self.tree.command(name="code", description="Submit the verification code sent to your email.")
        @app_commands.describe(code="The 6-digit code")
        async def code(interaction: discord.Interaction, code: str):
            await self.submit_cmd.execute(interaction, code=code)

        # Sync the command tree to Discord
        await self.tree.sync()
        print("SUSA Bot is online and slash commands are synced.")