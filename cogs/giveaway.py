import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import pyrebase
from humanfriendly import format_timespan
import random

load_dotenv()

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


class buttonRegister(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=100)
    
    @discord.ui.button(style=discord.ButtonStyle.blurple, emoji='🎉', custom_id='giveaway')
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            if not database.child('giveaway').child(interaction.user.id).get().val():
                database.child('giveaway').update({interaction.user.id: True})
                counter = database.child('giveawaycount').get().val()
                database.update({"giveawaycount": counter + 1})
                embed = discord.Embed(title="Welkin Giveaway", description=f"Click the 🎉 button to join.\n\nDouble your chances of winning by answering the form and sending a screenshot in <#1084016282250268742>!\n\n**Participants:** {counter + 1}", color=3092790)
                await interaction.response.edit_message(embed=embed)
            else:
                await interaction.response.send_message(ephemeral=True, content="You are already in the giveaway.")
        except Exception as e:
            print(e)

class giveawayClass(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    async def setup_hook(self) -> None:
        self.bot.add_view(buttonRegister())

    @commands.Cog.listener()
    async def on_ready(self):
        print("giveaway cog is online.")
        

    @commands.command()
    async def giveawayxxx(self,ctx):
        embed = discord.Embed(title="Welkin Giveaway", description="Click the 🎉 button to join.\n\nDouble your chances of winning by answering the form and sending a screenshot in <#1084016282250268742>!", color=3092790)
        channel = self.bot.get_channel(1008333194271129600)
        await channel.send(embed=embed, view=buttonRegister())

    @commands.command()
    async def welkin(self,ctx):
        try:
            if not database.child('giveaway').child(ctx.author.id).get().val():
                database.child('giveaway').update({ctx.author.id: True})
                counter = database.child('giveawaycount').get().val()
                database.update({"giveawaycount": counter + 1})
                embed = discord.Embed(title="Welkin Giveaway", description=f"Thank you for joining the giveaway!\n\n**Participants:** {counter + 1}", color=3092790)
                await ctx.reply(embed=embed)
            else:
                await ctx.reply("You are already in the giveaway.")
        except Exception as e:
            print(e)

    @commands.command()
    async def rollwelkin(self,ctx):
        try:
            participants = database.child('giveaway').shallow().get().val()
            length = len(participants)
            random_number = random.randint(0, length) - 1
            chosen = list(participants)[random_number]
            await ctx.reply(f"The winner is: <@{chosen}>")
        except Exception as e:
            print(e)
        
async def setup(bot):
    await bot.add_cog(giveawayClass(bot))