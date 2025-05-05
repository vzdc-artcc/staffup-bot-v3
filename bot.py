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
    print(f"Online: {bot.user}")
    await check_online_controllers.start()


@tasks.loop(seconds=15.0)
async def check_online_controllers():
    try:
        staffup_channel = bot.get_channel(1023762177569603694)

        raw_data = requests.get("https://data.vatsim.net/v3/vatsim-data.json")

        if raw_data.status_code == 200:
            data = json.loads(raw_data.text)
            all_controllers = data["controllers"]
            zdc_controllers = []

            for controller in all_controllers:
                if controller['callsign'].startswith(tuple(watched_positions)):
                    zdc_controllers.append(dict(list(controller.items())[:7]))

            for controller in online_zdc_controllers.copy():
                if controller not in zdc_controllers and controller['frequency'] != "199.998":
                    embed = Embed()
                    embed.title = f"{controller['callsign']} - {controller['frequency']} - Offline"
                    embed.add_field(name="Name:", value=f"{controller['name']} ({rating_map[controller['rating']]})")
                    embed.set_footer(text="vZDC Controller Status")
                    embed.colour = discord.Color.red()
                    await staffup_channel.send(embed=embed)
                    online_zdc_controllers.remove(controller)

            for controller in zdc_controllers:
                if controller not in online_zdc_controllers.copy() and controller['frequency'] != "199.998":
                    embed = Embed()
                    embed.title = f"{controller['callsign']} - {controller['frequency']} - Online"
                    embed.add_field(name="Name:", value=f"{controller['name']} ({rating_map[controller['rating']]})")
                    embed.set_footer(text="vZDC Controller Status")
                    embed.colour = discord.Color.green()
                    await staffup_channel.send(embed=embed)
                    online_zdc_controllers.append(controller)
        else:
            print("Could not fetch VATSIM Data.")
    except:
        print("An Error Occurred.")



@check_online_controllers.before_loop
async def before_check():
    print("Awaiting Ready Status")
    await bot.wait_until_ready()
    print("200: Bot Ready")


bot.run(TOKEN)
