import os
from engine import BlackjackEngine
from discordWrapper import DiscordClient
from simulator import BlackjackSimulator
# from dotenv import load_dotenv
# load_dotenv()

engine = BlackjackEngine()
discordClient = DiscordClient(engine)
simulator = BlackjackSimulator(engine)

# run the engine against Discord's Pancake bot
discordClient.run(os.getenv('TOKEN'))

# run the engine against a simulator
# for i in range(100):
# 	simulator.run(2000, 5000) # (shoes, balance) should be around 400 shoes per day on discord
