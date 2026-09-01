import os
from dotenv import load_dotenv
from core.bot import SUSABot

def main():
    load_dotenv()
    token = os.getenv('DISCORD_TOKEN')
    
    # Replace with the actual Role ID you want the bot to assign
    verified_role_id = int(os.getenv('VERIFIED_ROLE_ID', 0)) 

    if not token:
        raise ValueError("DISCORD_TOKEN environment variable is missing.")
    if not verified_role_id:
        print("WARNING: VERIFIED_ROLE_ID is missing. Role assignment will fail.")

    bot = SUSABot(verified_role_id=verified_role_id)
    bot.run(token)

if __name__ == "__main__":
    main()