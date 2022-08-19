from operator import truediv
import time
import threading
import random
import re
import asyncio
import discord
from utils import enum
from engine import BlackjackEngine, moves

class DiscordClient(discord.Client):

	# Helper methods
	def __convertRawHand(self, rawHand):
		firstLine = rawHand['value'].split('\n')[0]
		split1 = re.split('♣|♦|❤|♠| |-', firstLine)
		filtered = [number for number in split1 if len(number) != 0] # no empty strings between previous delimiters
		for i in range(len(filtered)):
			if filtered[i] in ['J','Q','K']:
				filtered[i] = 10
			elif filtered[i] == 'A':
				filtered[i] = 1
			elif filtered[i] == 'XX': ## when hole card is not shown
				filtered[i] = 0
			else:
				filtered[i] = int(filtered[i])
		return filtered

	def __getUserHands(self, rawFields):
		userHandsRaw = [entry for entry in rawFields if 'Your hand' in entry['name'] or 'Hand' in entry['name']]
		userHands = list(map(self.__convertRawHand, userHandsRaw))
		return userHands
	
	def __getDealerHand(self, rawFields):
		dealerHandRaw = next(filter(lambda entry: 'Dealer hand' in entry['name'], rawFields)) # next() finds first occurrence
		dealerHand = self.__convertRawHand(dealerHandRaw)
		return dealerHand

	async def __startRound(self, channel, betAmount):
		while True:
			await channel.send(f'-blackjack {betAmount}')
			currentTime = time.time()
			self.startTime = currentTime
			await asyncio.sleep(10)
			if currentTime != self.startTime or self.currentStatus != self.statuses.PLAYING: # if self.startTime got updated during the sleep, a new round was started so we don't have to resend this round
				return
			await channel.send('trying again')



	# Constructor
	def __init__(self, engine):
		super().__init__()

		self.engine = engine
		self.statuses = enum(
			STOPPED = 'STOPPED',
			CHECKING_BALANCE = 'CHECKING_BALANCE',
			PLAYING = 'PLAYING'
		)
		self.currentStatus = self.statuses.STOPPED

		self.waitTime = 5.3 # time in between games
		self.startTime = time.time() # to distribute waiting time over several moves



	# Main methods
	async def on_ready(self):
		print('Logged on as', self.user)

	async def on_message(self, message):
		username = str(message.author)
		content = message.content

		if message.author == self.user or username == 'ⓔ₮ℌἇℵ#2434':
			if content == 'START':
				if self.currentStatus == self.statuses.STOPPED:
					self.currentStatus = self.statuses.CHECKING_BALANCE
					self.engine = BlackjackEngine() # reset all engine values to initial ones
					await message.channel.send('starting blackjack...')
					await message.channel.send('-bal')
			elif content == 'STOP':
				if self.currentStatus != self.statuses.STOPPED:
					self.currentStatus = self.statuses.STOPPED
					await message.channel.send('stopping blackjack...')
			elif content == 'ping':
				await message.channel.send('pong')

		if username == 'Pancake#3691':

			# print(content)

			embeds = message.embeds
			for embed in embeds:
				obj = embed.to_dict()

				# print(obj)

				# Get balance when first starting
				if self.currentStatus == self.statuses.CHECKING_BALANCE:
					if 'fields' in obj and 'author' in obj and 'name' in obj['author'] and obj['author']['name'] == 'BlackjackGod':
						balanceField = [x for x in obj['fields'] if 'name' in x and x['name'] == 'In Hand']
						if len(balanceField) == 1:
							self.engine.balance = int(balanceField[0]['value'][1:].replace(',', ''))
							print(self.engine.balance)
							print(self.engine.balance + 1)
							# GAME STARTS HERE
							self.currentStatus = self.statuses.PLAYING
							self.engine.warmingUp = True # redundancy (since engine is already reset)
							await self.__startRound(message.channel, 1)
					return


				if 'title' in obj and 'Blackjack' in obj['title']:
					# if this is the end of a game, update count
					if 'won' in obj['description'] or 'lost' in obj['description'] or 'broke even' in obj['description']:

						remaining = 0 # when 0 cards remain Pancake shows 'Shuffling'
						if 'Cards remaining' in obj['footer']['text']:
							remaining = int(obj['footer']['text'].split(' ')[2])

						allHands = self.__getUserHands(obj['fields'])
						dealerHand = self.__getDealerHand(obj['fields'])
						allHands.append(dealerHand)

						self.engine.updateCount(allHands, remaining)

						# if this the end of MY game, start a new game
						if 'BlackjackGod' in obj['title']:
							balanceChange = 0 # if broke even
							if 'won' in obj['description']:
								balanceChange = int(obj['description'][9:].replace(',', ''))
							elif 'lost' in obj['description']:
								balanceChange = -int(obj['description'][10:].replace(',', ''))

							self.engine.updateBalance(balanceChange)
							betAmount = self.engine.calculateBetAmount()

							# only stop at the end of a game
							if self.currentStatus == self.statuses.STOPPED:
								return

							endTime = time.time()
							elapsedTime = endTime - self.startTime
							if elapsedTime < self.waitTime:
								time.sleep(self.waitTime - elapsedTime)
							await self.__startRound(message.channel, betAmount)
					
					# if this is the middle of MY game, just play the hand
					elif 'BlackjackGod' in obj['title']:
						userHands = self.__getUserHands(obj['fields'])
						dealerHand = self.__getDealerHand(obj['fields'])
						checkIfSplit = [entry for entry in obj['fields'] if 'Hand' in entry['name']] # Hand capitalized if Hand 1/Hand 2 (after split)
						alreadySplit = True if len(checkIfSplit) == 1 else False
						move = self.engine.playHand(userHands[0], dealerHand, alreadySplit)

						emoji = 0
						if move == moves.HIT:
							emoji = '👋'
						elif move == moves.STAND:
							emoji = '🤚'
						elif move == moves.DOUBLE:
							emoji = '👐'
						elif move == moves.SPLIT:
							emoji = '✌'
						
						waitTime = random.uniform(0.6,0.9)
						time.sleep(waitTime)
						await message.add_reaction(emoji)
