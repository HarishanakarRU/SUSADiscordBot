import discord
from core.command import BaseCommand
from services.db_service import DatabaseService

class SubmitCodeCommand(BaseCommand):
    """
    Command to validate the code sent to the user's email.
    """
    def __init__(self, db_service: DatabaseService, verified_role_id: int):
        self.db_service = db_service
        self.verified_role_id = verified_role_id

    async def execute(self, interaction: discord.Interaction, code: str) -> None:
        await interaction.response.defer(ephemeral=True)

        user = interaction.user
        result = self.db_service.check_and_verify_code(user.id, code)

        if result["success"]:
            try:
                # 1. Assign Role
                role = interaction.guild.get_role(self.verified_role_id)
                await user.add_roles(role)
                
                # 2. Change Nickname
                first_name = result["first_name"]
                await user.edit(nick=first_name)
                
                await interaction.followup.send(f"✅ Verification successful! Welcome, {first_name}.")
            except discord.Forbidden:
                await interaction.followup.send(
                    "✅ Code correct, but I lack permissions to assign roles or change nicknames. "
                    "Make sure the Bot role is highest in the role list and has 'Manage Nicknames' permission."
                )
        else:
            await interaction.followup.send("❌ Invalid code or no pending verification found.")