import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import pyrebase
from humanfriendly import format_timespan
from enkanetwork import EnkaNetworkAPI
from enkanetwork.model.stats import Stats
import asyncio
from enkanetwork import Assets

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
enclnt = EnkaNetworkAPI()
assets = Assets()

class SelectCharacter(discord.ui.Select):
    def __init__(self, character_list, nickname):
        self.character_list = character_list
        self.nickname = nickname
        option_list = []
        for character in character_list:
            option_list.append(discord.SelectOption(label=f"{character['Index'] + 1} {character['Name']}"))

        super().__init__(placeholder="Select character", max_values=1, min_values=1, options=option_list)
    async def callback(self, interaction: discord.Interaction):
        selected = int(self.values[0][0]) - 1
        print(self.character_list)
        embed = discord.Embed(title=f"{self.nickname}'s Profile", description=f"**{self.character_list[selected]['Name']}**\n**Level:** {self.character_list[selected]['Level']}\n<:critrate:1076738384560660520> {self.character_list[selected]['Crit']}\n<:critdmg:1076738380206973020> {self.character_list[selected]['CritDMG']}")
        embed.set_thumbnail(url=self.character_list[selected]['Icon'])
        await interaction.response.edit_message(embed=embed)

class SelectCharacterView(discord.ui.View):
    def __init__(self, *, timeout=100, character_list, nickname):
        super().__init__(timeout=timeout)
        self.add_item(SelectCharacter(character_list=character_list, nickname=nickname))

class enkapy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("enkapy cog is online.")

    @commands.command()
    async def enkaIndex(self,ctx):
        async with enclnt:
            # data = await enclnt.fetch_user_by_uid(813180074)
            # character_list = []
            # index = 0
            # for character_raw in data.characters:
                
            #     # print(f"======={character_raw.name}=======")
            #     character_list.append({"Name": character_raw.name,
            #                             "Element": character_raw.element,
            #                             "Icon": character_raw.image.icon.url,
            #                             "Level": character_raw.level,
            #                             "Index": index})
                

            #     for stat in character_raw.stats:
            #         if stat[0] == 'FIGHT_PROP_CRITICAL':
            #             crit_data = {'Crit': stat[1].to_percentage_symbol()}
            #             character_list[index].update(crit_data)
            #         if stat[0] == 'FIGHT_PROP_CRITICAL_HURT':
            #             critDMG_data = {'CritDMG': stat[1].to_percentage_symbol()}
            #             character_list[index].update(critDMG_data)
            #             # print(f"- {stat[0]}: {stat[1].to_rounded() if isinstance(stat[1], Stats) else stat[1].to_percentage_symbol()}")
            
            #     index += 1
            # print(character_list)
            
            # embed = discord.Embed(title=f"{data.player.nickname}'s Profile", description=f"**{character_list[0]['Name']}**\n**Level:** {character_list[0]['Level']}\n<:critrate:1076738384560660520> {character_list[0]['Crit']}\n<:critdmg:1076738380206973020> {character_list[0]['CritDMG']}")
            # embed.set_thumbnail(url=character_list[0]['Icon'])
            # await ctx.reply(embed=embed, view=SelectCharacterView(character_list=character_list, nickname=data.player.nickname))

            try:
                users = database.child('boon').child('notes').child('users').get().val()
                for user in users:
                    uid = users[user]['uid']
                    print(uid)
                    data = await enclnt.fetch_user_by_uid(uid)
                    for character_raw in data.characters:
                        record = {character_raw.name:{'level': character_raw.level}}
                        database.child('boon').child('characters').child(user).update(record)
                        for stat in character_raw.stats:
                            if stat[0] == 'FIGHT_PROP_CRITICAL':
                                crit_data = {'Crit': stat[1].to_percentage_symbol()}
                                database.child('boon').child('characters').child(user).child(character_raw.name).update(crit_data)
                            elif stat[0] == 'FIGHT_PROP_CRITICAL_HURT':
                                critDMG_data = {'CritDMG': stat[1].to_percentage_symbol()}
                                database.child('boon').child('characters').child(user).child(character_raw.name).update(critDMG_data)

            except Exception as e:
                print(e)

    @commands.command()
    async def cvlb(self, ctx):
        data = database.child('boon').child('characters').get().val()
        print(data)
        for users in data:
            print(f'======={users}=======')
            for character in data[users]:
                print(character)
                print(f"Crit Rate: {data[users][character]['Crit']}")
                print(f"Crit DMG: {data[users][character]['CritDMG']}")
                print(f"CV: {float(data[users][character]['Crit'][:-1])*2 + float(data[users][character]['CritDMG'][:-1])}")
        
async def setup(bot):
    await bot.add_cog(enkapy(bot))