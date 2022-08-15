import os
from dotenv import load_dotenv
from engine import BlackjackEngine
from discordWrapper import DiscordClient
from simulator import BlackjackSimulator

load_dotenv()
engine = BlackjackEngine()
discordClient = DiscordClient(engine)
simulator = BlackjackSimulator(engine)

# run the engine against Discord's Pancake bot
discordClient.run(os.getenv('TOKEN'))

# run the engine against a simulator
# simulator.run(sth,sth,sth)
