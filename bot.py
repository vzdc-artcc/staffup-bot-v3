import os

import discord
import requests
import json
from typing import Final

from discord import Intents, Embed
from discord.ext import commands, tasks
from dotenv import load_dotenv

load_dotenv()
TOKEN: Final[str] = os.getenv("TOKEN")

intents: Intents = Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

online_zdc_controllers = []

watched_positions = ['DCA_', 'IAD_', 'BWI_', 'PCT_', 'ADW_', 'RIC_', 'ROA_', 'ORF_', 'ACY_', 'NGU_',
                    'NTU_', 'NHK_', 'RDU_', 'CHO_', 'HGR_', 'LYH_', 'EWN_', 'LWB_', 'ISO_', 'MTN_', 'HEF_',
                    'MRB_', 'PHF_', 'SBY_', 'NUI_', 'FAY_', 'ILM_', 'NKT_', 'NCA_', 'NYG_', 'DAA_', 'DOV_',
                    'POB_', 'GSB_', 'WAL_', 'CVN_', 'JYO_', 'DC_']

rating_map = {1: "OBS", 2: "S1", 3: "S2", 4: "S3", 5: "C1", 7: "C3", 8: "I1", 10: "I3", 11: "SUP", 12: "ADM"}



@bot.event
async def on_ready():
    staffup_channel = bot.get_channel(1198323590165176480)
    #CHANGE_THIS_CHANNEL_ID

    print(f"Online: {bot.user}")

    embed = Embed()
    embed.title = "ZDC Online Controllers"
    embed.colour = discord.Colour.red()

    global controller_list
    controller_list = await staffup_channel.send(embed=embed)

    await check_online_controllers.start()


@tasks.loop(seconds=10.0)
async def check_online_controllers():
    try:

        raw_data = requests.get("https://data.vatsim.net/v3/vatsim-data.json")

        if raw_data.status_code == 200:
            data = json.loads(raw_data.text)
            all_controllers = data["controllers"]
            zdc_controllers = []

            for controller in all_controllers:
                if controller['callsign'].startswith(tuple(watched_positions)):
                    zdc_controllers.append(dict(list(controller.items())[:7]))

            for controller in online_zdc_controllers.copy():
                if controller not in zdc_controllers:
                    online_zdc_controllers.remove(controller)

            for controller in zdc_controllers:
                if controller not in online_zdc_controllers.copy():
                    online_zdc_controllers.append(controller)

            embed = Embed()
            embed.title = "ZDC Online Controllers"
            embed.colour = discord.Colour.red() if len(online_zdc_controllers) == 0 else discord.Colour.green()

            embed.add_field(name="Position:", value="", inline=True)
            embed.add_field(name="Frequency:", value="", inline=True)
            embed.add_field(name="Name:", value="", inline=True)

            for controller in online_zdc_controllers:
                embed.add_field(name="", value=controller['callsign'], inline=True)
                embed.add_field(name="", value=controller['frequency'], inline=True)
                embed.add_field(name="", value=f"{controller['name']} ({(rating_map[controller['rating']])})", inline=True)
                embed.add_field(name="", value="", inline=False)

            embed.set_footer(text="vZDC Controller Status")

            await controller_list.edit(embed=embed)
        else:
            print("Could not fetch VATSIM Data.")
    except:
        print("An Error Occurred. Aneesh is bad.")


@check_online_controllers.before_loop
async def before_check():
    print("Awaiting Ready Status")
    await bot.wait_until_ready()
    print("200: Bot Ready")


bot.run(TOKEN)
