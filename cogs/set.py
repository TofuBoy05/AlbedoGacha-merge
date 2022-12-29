import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
load_dotenv()
import pyrebase
from discord import app_commands
from discord.ext import commands
import time
from datetime import date
from humanfriendly import format_timespan
import pytz
import datetime as dt

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

main_timezones_list = []

class Select(discord.ui.Select):
    def __init__(self):
        option_list = []
        for timezones in main_timezones_list:
            option_list.append(discord.SelectOption(label=f"{timezones}"))
        options = option_list
        super().__init__(placeholder="Choose a timezone", max_values=1, min_values=1, options=options)
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"Successfully set your timezone to f{self.values[0]}")
        data = {"timezone": self.values[0]}
        database.child("boon").child("playtime").child(interaction.user.id).child("settings").update(data)

class SelectView(discord.ui.View):
    def __init__(self, *, timeout=100):
        super().__init__(timeout=timeout)
        self.add_item(Select())



class setTZ(commands.GroupCog, name="set"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        super().__init__()


    def possible_timezones(self, tz_offset):
        # pick one of the timezone collections
        timezones = pytz.common_timezones

        # convert the float hours offset to a timedelta
        offset_days, offset_seconds = 0, int(tz_offset * 3600)
        if offset_seconds < 0:
            offset_days = -1
            offset_seconds += 24 * 3600
        desired_delta = dt.timedelta(offset_days, offset_seconds)

        # Loop through the timezones and find any with matching offsets
        null_delta = dt.timedelta(0, 0)
        results = []
        for tz_name in timezones:
            tz = pytz.timezone(tz_name)
            non_dst_offset = getattr(tz, '_transition_info', [[null_delta]])[-1]
            if desired_delta == non_dst_offset[0]:
                main_timezones_list.append(tz_name)

    @commands.Cog.listener()
    async def on_ready(self):
        print ('playtime cog is online.')

    @app_commands.command(name="timezone", description="Set your timezone to check your day specific play time.")
    async def setTZ(self, interaction: discord.Interaction, gmt: int):
        # await interaction.response.defer()
        try:
            print(self.possible_timezones(tz_offset=gmt))
            await interaction.response.send_message(view=SelectView())
            # data = {"timezone": tz}
            # database.child("boon").child("playtime").child(interaction.user.id).child("settings").update(data)
        except Exception as e:
            print(e)

   

# async def setup(bot):
#     await bot.add_cog(playtimeStat(bot))

async def setup(bot):
    await bot.add_cog(setTZ(bot), guilds=[discord.Object(id=991361510263767080)])