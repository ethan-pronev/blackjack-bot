from operator import truediv
import time
import random
import re
import discord
from utils import enum
from engine import moves

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



	# Constructor
	def __init__(self, engine):
		super().__init__()

		self.engine = engine
		self.statuses = enum(
			STOPPED = 'STOPPED',
			PLAYING = 'PLAYING'
		)
		self.currentStatus = self.statuses.STOPPED

		self.waitTime = 5 # time in between games
		self.timeWaitedSoFar = 0 # to distribute waiting time over several moves



	# Main methods
	async def on_ready(self):
		print('Logged on as', self.user)

	async def on_message(self, message):
		username = str(message.author)
		content = message.content

		if message.author == self.user or username == 'ⓔ₮ℌἇℵ#2434':
			if content == 'START':
				if self.currentStatus == self.statuses.STOPPED:
					self.status = self.statuses.PLAYING
					await message.channel.send('starting blackjack...')
					await message.channel.send('-blackjack 1')
			elif content == 'STOP':
				if self.currentStatus != self.statuses.STOPPED:
					self.status = self.statuses.STOPPED
					await message.channel.send('stopping blackjack...')
		
		if self.status == self.statuses.STOPPED:
			return

		if username == 'Pancake#3691':
			print(content + '\n')

			embeds = message.embeds
			for embed in embeds:
				obj = embed.to_dict()
				print(obj)
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

						# await message.channel.send(' '.join(str(item) for item in allHands) + '\n' + str(self.engine.runningCount))

						# if this the end of MY game, start a new game
						if 'BlackjackGod' in obj['title']:
							balanceChange = 0 # if broke even
							if 'won' in obj['description']:
								balanceChange = int(obj['description'].split('🥞')[1])
							elif 'lost' in obj['description']:
								balanceChange = -int(obj['description'].split('🥞')[1])

							self.engine.updateBalance(balanceChange)
							betAmount = self.engine.calculateBetAmount()

							waitTime = self.waitTime - self.timeWaitedSoFar
							if waitTime > 0:
								time.sleep(waitTime)
								self.timeWaitedSoFar = 0
							await message.channel.send(f'-blackjack {betAmount}')
					
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
						self.timeWaitedSoFar += waitTime
						time.sleep(waitTime)
						await message.add_reaction(emoji)
