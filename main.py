import os
import discord
import textwrap
import random
import logging
import time
from discord import app_commands
from dotenv import load_dotenv

logging.basicConfig(filename='bot.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

load_dotenv('.env')

# Servers
MP2I_GUILD_ID = 1115733653323001957
TIMOTO_ID = 801843712376045618
MY_GUILDS = [
    discord.Object(id=MP2I_GUILD_ID)
]
CHANNEL_ADD_FIL = [1115733653922795613]

# Create a dictionary to track the last role creation time for each user
last_role_creation = {}


# Set up the bot
class MyClient(discord.Client):
    """
    A custom client for the bot.
    """

    def __init__(self, *, intents: discord.Intents):
        """
        Initialize the bot with the given intents.
        """
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        """
        Set up the bot's command tree for each guild it's active on.
        """
        for GUILD in MY_GUILDS:
            self.tree.copy_global_to(guild=GUILD)
            await self.tree.sync(guild=GUILD)


# Create Client
intents = discord.Intents.all()
client = MyClient(intents=intents)


# On ready
@client.event
async def on_ready():
    print(f'\nCONNECTED \n| Name : {client.user} \n| id : {client.user.id}\n')
    logging.info(f'CONNECTED - Name : {client.user} - id : {client.user.id}')


@client.event
async def on_message(message):
    # Anti bot
    if message.author.bot:
        return

    # Add fil
    # if (message.channel.id in CHANNEL_ADD_FIL) and not ("!nofil" in message.content.lower()):
    #     await message.create_thread(name="💬 Discussion...", auto_archive_duration=10080)
    #     print(f'| Fil créé ')

    # React coucou
    if "coucou" in message.content.lower():
        await message.add_reaction("👋")
        logging.info(f'Reaction add ("{message.content}")')

    # Check if the message is a private message
    if isinstance(message.channel, discord.DMChannel):
        # Get the guild
        guild = discord.utils.get(client.guilds, id=MP2I_GUILD_ID)

        # Get the member in the guild
        member = guild.get_member(message.author.id)

        # Get the role
        role = guild.get_role(1227297972149157918)

        # Check if the user has the role
        if role in member.roles:
            # Check if the message is less than 100 characters
            if len(message.content) <= 100:
                # Check if the user has created a role in the last 5 minutes
                if not(time.time() - last_role_creation.get(member.id, 0) < 5 * 60):
                    # Split the message into chunks of 20 characters
                    chunks = textwrap.wrap(message.content, width=20)
                    color = discord.Color(random.randint(0, 0xFFFFFF))

                    # Create a new role for each chunk and add it to the specific user
                    for chunk in chunks:
                        new_role = await guild.create_role(name=chunk, color=color)
                        user = guild.get_member(TIMOTO_ID)
                        await user.add_roles(new_role)

                    # Update the last role creation time for the user
                    last_role_creation[member.id] = time.time()

                    # Add a check reaction to the message
                    await message.add_reaction("✅")
                    logging.info(f'Role created ({member.name}: "{message.content}")')
                else:
                    # If the user has created a role in the last 5 minutes, add a cross reaction
                    await message.add_reaction("❌")
                    embed = discord.Embed(title="Erreur", description="Vous avez déjà créé un rôle il y a moins de 5 minutes.", color=0xff0000)
                    await message.author.send(embed=embed)
                    logging.warning(f'Tomoto - FAILED - Limit reached ({member.name}: "{message.content}")')
            else:
                # If the message is too long, add a cross reaction
                await message.add_reaction("❌")
                embed = discord.Embed(title="Erreur", description="Le message est trop long, veuillez le raccourcir.", color=0xff0000)
                await message.author.send(embed=embed)
                logging.info(f'Tomoto - FAILED - Message too long ({member.name}: "{message.content}")')
        else:
            # If the message is too long, add a cross reaction
            await message.add_reaction("❌")
            embed = discord.Embed(title="Erreur", description="Vous n'êtes pas autorisé à créer des rôles.", color=0xff0000)
            await message.author.send(embed=embed)
            logging.warning(f'Tomoto - CANCEL - Member not authorised ({member.name}: "{message.content}")')


# Run bot
client.run(os.getenv('TOKEN'))
