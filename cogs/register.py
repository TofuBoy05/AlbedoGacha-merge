import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
load_dotenv()
import pyrebase
from discord import app_commands
from discord.ext import commands
import genshin

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

genshinUIDs = []
honkaiUIDs = []
honkaiUID = []

class SelectAccGen(discord.ui.Select):
    def __init__(self):
        option_list = []
        if genshinUIDs:
            for uid in genshinUIDs:
                option_list.append(discord.SelectOption(label=f"{uid}"))
        elif not genshinUIDs:
            option_list.append(discord.SelectOption(label=f"You have no Genshin Accounts"))
        options = option_list
        super().__init__(placeholder="Select a Genshin UID", max_values=1, min_values=1, options=options)
    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "You have no Genshin Accounts":
            await interaction.response.send_message("Stop trying bitch", ephemeral=True)
            return
        await interaction.response.send_message(f"Successfully set your Genshin UID to {self.values[0]}. Your Daily check-in for Genshin will be automatically be claimed, and you can check your resin amount using `.n`", ephemeral=True)
        data = {"uid": int(self.values[0])}
        database.child("boon").child("notes").child("users").child(interaction.user.id).update(data)

class SelectAccHon(discord.ui.Select):
    def __init__(self):
        option_list = []
        if honkaiUIDs:
            for uid in honkaiUIDs:
                option_list.append(discord.SelectOption(label=f"{uid}"))
        elif not honkaiUIDs:
            option_list.append(discord.SelectOption(label="You have no Honkai Accounts"))
        options = option_list
        super().__init__(placeholder="Select a Honkai ID", max_values=1, min_values=1, options=options)
    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "You have no Honkai Accounts":
            await interaction.response.send_message("Stop trying bitch", ephemeral=True)
            return
        await interaction.response.send_message(f"Successfully set your Honkai UID to {self.values[0]}. Your Daily check-in for Honkai will be automatically be claimed, and you can now use </honkai:1059362301360230400>.", ephemeral=True)
        data = {"huid": int(self.values[0])}
        database.child("boon").child("notes").child("users").child(interaction.user.id).update(data)

class SelectAccGenView(discord.ui.View):
    def __init__(self, *, timeout=100):
        super().__init__(timeout=timeout)
        self.add_item(SelectAccGen())
        self.add_item(SelectAccHon())


class registerModal(discord.ui.Modal, title="Registration"):
    ltoken = discord.ui.TextInput(label = "Paste ltoken here", placeholder="ltoken=XXXXXXX;", style=discord.TextStyle.short)
    ltuid = discord.ui.TextInput(label= "Paste ltuid here", placeholder= "ltuid=12345;", style= discord.TextStyle.short)
    cookie_token = discord.ui.TextInput(label= "Paste cookie_token here", placeholder= "cookie_token=XXXXXX;", style= discord.TextStyle.short)
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await interaction.edit_original_response(content="Getting your game accounts...", embed=None, view=None)
        try:
            if self.ltoken.value.startswith('ltoken=') and self.ltoken.value.endswith(";"):
                data = {"ltoken": self.ltoken.value[7:-1], "ltuid": int(self.ltuid.value[6:-1]), "cookie_token": self.cookie_token.value[13:-1]}
                database.child("boon").child("notes").child("users").child(interaction.user.id).update(data)
            else:
                embed = discord.Embed(title="Error", description="Error. Please make sure you put the correct information.")
                await interaction.edit_original_response(content="", embed=embed, view=buttonRegister())
        except Exception as e:
            embed = discord.Embed(title="Error", description="Error. Please make sure you put the correct information.")
            await interaction.edit_original_response(content="", embed=embed, view=buttonRegister())
        
        try:
            ltuid = int(self.ltuid.value[6:-1])
            ltoken = self.ltoken.value[7:-1]
            gc = genshin.Client(f"ltoken={ltoken}; ltuid={ltuid}")
            gameAccounts = await gc.get_game_accounts()
            for accounts in gameAccounts:
                if str(accounts.game_biz) == "bh3_global":
                    honkaiUIDs.append(accounts.uid)
                elif str(accounts.game_biz) == "hk4e_global":
                    genshinUIDs.append(accounts.uid)
            await interaction.edit_original_response(content=f"Please select Your UIDs. If you don't want to connect a game, just don't pick a UID bbg <333", view=SelectAccGenView())
        except Exception as e:
            embed = discord.Embed(title="Error", description="Error. Please make sure you put the correct information.")
            await interaction.edit_original_response(content="", embed=embed, view=buttonRegister())
        



class buttonRegister(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=100)
    
    @discord.ui.button(label="Register", style=discord.ButtonStyle.blurple)
    async def registerbutton(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(registerModal())
    
    @discord.ui.button(label="PC Script", style=discord.ButtonStyle.gray, emoji="💻")
    async def scriptbutton(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed2 = discord.Embed(description="```js\nscript:check = document.cookie.includes('account_id') && document.cookie.includes('cookie_token') || alert('Please logout and log back in before trying again, cookie expired.'); a=document.cookie.match(/(ltoken)=(.*?);/gm); b=document.cookie.match(/(ltuid)=(.*?);/gm); c=document.cookie.match(/(cookie_token)=(.*?);/gm); check && document.write(`<br><br><button onclick=\"navigator.clipboard.writeText('${a}')\">Copy ltoken</button><br><br><button onclick=\"navigator.clipboard.writeText('${b}'); \">Copy ltuid</button><br><br><button onclick=\"navigator.clipboard.writeText('${c}')\">Copy cookie_token</button>`)```")
        await interaction.response.send_message(embed=embed2, ephemeral=True)

    @discord.ui.button(label="Mobile Script", style=discord.ButtonStyle.gray, emoji="📱")
    async def scriptbuttonmobile(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed2 = discord.Embed(description="script:check = document.cookie.includes('account_id') && document.cookie.includes('cookie_token') || alert('Please logout and log back in before trying again, cookie expired.'); a=document.cookie.match(/(ltoken)=(.*?);/gm); b=document.cookie.match(/(ltuid)=(.*?);/gm); c=document.cookie.match(/(cookie_token)=(.*?);/gm); check && document.write(`<br><br><button onclick=\"navigator.clipboard.writeText('${a}')\">Copy ltoken</button><br><br><button onclick=\"navigator.clipboard.writeText('${b}'); \">Copy ltuid</button><br><br><button onclick=\"navigator.clipboard.writeText('${c}')\">Copy cookie_token</button>`)")
        await interaction.response.send_message(embed=embed2, ephemeral=True)

    @discord.ui.button(label="Video Tutorial", style=discord.ButtonStyle.gray, emoji="🎥")
    async def video(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("https://media.discordapp.net/attachments/1038687174654173184/1056956420601434142/Screen_Recording_20221226-232300_Discord.mp4", ephemeral=True)
    

class register(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print ('Register cog is online.')

    @commands.command()
    async def sync(self, ctx) -> None:
        try:
            if ctx.author.id == 459655669889630209:
                fmt = await ctx.bot.tree.sync()
                await ctx.send(f'synced {len(fmt)} commands.')
            else:
                await ctx.reply("Only the bot owner can use this command.")
        except Exception as e:
            print(e)

    @commands.command()
    async def syncg(self, ctx) -> None:
        try:
            if ctx.author.id == 459655669889630209:
                fmt = await ctx.bot.tree.sync(guild=ctx.guild)
                await ctx.send(f'synced {len(fmt)} commands.')
            else:
                await ctx.reply("Only the bot owner can use this command.")
        except Exception as e:
            print(e)

    @app_commands.command(name="register", description="Register for autoclaim and live notes")
    async def register(self, interaction: discord.Interaction):
        embed = discord.Embed(title="BoonBot Genshin HoYoLAB Registration", description="**1.** Go to HoYoLAB's website and log in.\n**2.** Type `java` on the url bar and then paste the script from below.\n **3.** Click the Register button in this message.\n**4.** One by one, copy and paste each field.", color=3092790)
        
        await interaction.response.send_message(content="", embed=embed, view=buttonRegister(), ephemeral=True)

    @app_commands.command(name="apology", description="Corn's apology letter")
    async def apology(self, interaction: discord.Interaction):
        embed = discord.Embed(color=3092790)
        embed.set_image(url="https://media.discordapp.net/attachments/1008333194271129600/1059149324975616030/unknown-6.png")
        await interaction.response.send_message(embed=embed)
            
async def setup(bot):
    await bot.add_cog(register(bot))

# async def setup(bot):
#     await bot.add_cog(register(bot), guilds=[discord.Object(id=980092176488886383)])
