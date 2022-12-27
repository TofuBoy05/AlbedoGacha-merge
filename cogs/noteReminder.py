import os
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
load_dotenv()
import pyrebase
TOKEN = os.getenv('TOKEN')
import time

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


class resinReminder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.resinReminderCheck.start()

    @commands.Cog.listener()
    async def on_ready(self):
        print("pulladd cog is online.")

    @tasks.loop(minutes=1)
    async def resinReminderCheck(self):
        
        print("looping through resin reminders")
        all_reminders = database.child("boon").child("notes").child("reminders").shallow().get().val()
        if all_reminders:
            for reminder in all_reminders:
                channel_id = database.child("boon").child("notes").child("reminders").child(reminder).child("channel").get().val()
                channel = self.bot.get_channel(channel_id)
                remind_time = database.child("boon").child("notes").child("reminders").child(reminder).child("time").get().val()
                current_time = int(time.time())

                if current_time >= remind_time:
                    print("reminding and deleting!")
                    await channel.send(f"<@{reminder}>! Resin reminder")
                    database.child("boon").child("notes").child("reminders").child(reminder).remove()

        

    @resinReminderCheck.before_loop
    async def before_printer(self):
        print('Waiting resin loop')
        await self.bot.wait_until_ready()
        
async def setup(bot):
    await bot.add_cog(resinReminder(bot))