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
# for i in range(100):
# 	simulator.run(4000, 5000) # (shoes, balance)
