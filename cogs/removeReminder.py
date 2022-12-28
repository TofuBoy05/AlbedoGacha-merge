import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
load_dotenv()
import pyrebase
from discord import app_commands
from discord.ext import commands

TOKEN = os.getenv('TOKEN')


service = {
    
  "type": "service_account",
  "project_id": os.getenv('project_id'),
  "private_key_id": os.getenv('private_key_id'),
  "private_key": os.getenv('private_key'),
  "client_email": os.getenv('client_email'),
  "client_id": os.getenv('client_id'),
  "auth_uri": os.getenv('auth_uri'),
  "token_uri": os.getenv('token_uri'),
  "auth_provider_x509_cert_url": os.getenv('auth_provider_x509_cert_url'),
  "client_x509_cert_url": os.getenv('client_x509_cert_url')
}

config = {
    'apiKey': os.getenv('apiKey'),
    'authDomain': os.getenv('authDomain'),
    'projectId': os.getenv('projectId'),
    'storageBucket': os.getenv('storageBucket'),
    'messagingSenderId': os.getenv('messagingSenderId'),
    'appId': os.getenv('appId'),
    'measurementId': os.getenv('measurementId'),
    'databaseURL': os.getenv('databaseURL'),
    "serviceAccount": service

} 

firebase = pyrebase.initialize_app(config)
database = firebase.database()


    

class removeReminderCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print ('Register cog is online.')

    @app_commands.command(name="cancelreminder", description="Cancels resin reminder.")
    async def removeReminder(self, interaction: discord.Interaction):
        
        if not database.child("boon").child("notes").child("reminders").child(interaction.user.id).get().val():
            await interaction.response.send_message("You do not have a resin reminder set.")
        else:
            await interaction.response.send_message("Successfully cancelled your resin reminder.")
            database.child("boon").child("notes").child("reminders").child(interaction.user.id).remove()

    @app_commands.command(name="hidebuttons", description="Hides live notes buttons")
    async def hideButtons(self, interaction: discord.Interaction):
        
        if database.child("boon").child("notes").child("users").child(interaction.user.id).get().val():
            data = {"show_note_buttons": False}
            database.child("boon").child("notes").child("users").child(interaction.user.id).child("settings").update(data)

    @app_commands.command(name="showbuttons", description="Shows live notes buttons")
    async def showButtons(self, interaction: discord.Interaction):
        
        if database.child("boon").child("notes").child("users").child(interaction.user.id).get().val():
            data = {"show_note_buttons": True}
            database.child("boon").child("notes").child("users").child(interaction.user.id).child("settings").update(data)
    
            
async def setup(bot):
    await bot.add_cog(removeReminderCommand(bot))

# async def setup(bot):
#     await bot.add_cog(removeReminderCommand(bot), guilds=[discord.Object(id=980092176488886383)])