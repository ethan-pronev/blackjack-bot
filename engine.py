import math
import json
from xml.etree.ElementInclude import include
from utils import enum

moves = enum(
	HIT = 'HIT',
	STAND = 'STAND',
	DOUBLE = 'DOUBLE',
	SPLIT = 'SPLIT'
)

class BlackjackEngine():
	def __init__(self):
		self.runningCount = 0
		self.trueCount = 0
		self.remainingCards = 208
		self.holeCards = 0

		self.balance = 0
		self.bettingUnits = 1000 # how many units to divide our bankroll by
		self.betSpread = [0,1,4,7,10,12,14,17,20,25] # [0,1,3,4,6,7,9,10,12,13,15,16,18,19,21,22,24,25,27,28,30] # how many betting units for each true count (array idx)

		self.tables = json.load(open('strategyTables.json'))

		self.warmingUp = True # if we are still playing the first shoe

	# hand is an array of numbers 1-10
	def updateCount(self, hands, remaining):
		if remaining < self.remainingCards: # normal case
			self.remainingCards = remaining
			for hand in hands:
				for card in hand:
					if card in [1,10]:
						self.runningCount -= 1
					elif 2 <= card <= 6:
						self.runningCount += 1
					elif card == 0:
						self.holeCards += 1 # if dealer has XX treat this as a remaining card
			
			self.trueCount = self.runningCount / (max(self.remainingCards + self.holeCards, 1) / 52)
		else: # if this hand has some cards from the next shoe, figure out which cards those are and only use those to update the count
			self.warmingUp = False # this case also signifies the end of a shoe
			
			self.remainingCards = remaining
			self.holeCards = 0
			self.runningCount = 0

			dealtOrder = []
			if len(hands) == 2: # ie. player didnt split
				dealtOrder = [hands[0][0]] + [hands[1][0]] + [hands[0][1]] + [hands[1][1]] + hands[0][2:] + hands[1][2:]
			else: #ie. if player splits and they have 2 hands
				dealtOrder = [hands[0][0]] + [hands[2][0]] + [hands[1][0]] + [hands[2][1]] + hands[0][1:] + hands[1][1:] + hands[2][2:]

			includedCards = dealtOrder[-(208-self.remainingCards):] # suffix of list we want to include
			for card in includedCards:
				if card in [1,10]:
					self.runningCount -= 1
				elif 2 <= card <= 6:
					self.runningCount += 1
				elif card == 0:
					self.holeCards += 1
			self.trueCount = self.runningCount / (max(self.remainingCards + self.holeCards, 1) / 52)

	def updateBalance(self, amount):
		self.balance += amount

		if self.balance >= 100000:
			self.bettingUnits = 2000
		elif self.balance >= 1000000:
			self.bettingUnits = 3000
		elif self.balance >= 10000000:
			self.bettingUnits = 4000

	def calculateBetAmount(self):
		if self.trueCount >= 1 and not self.warmingUp:
			roundedTrueCount = min(math.floor(self.trueCount),len(self.betSpread)-1)
			amount = self.balance * self.betSpread[roundedTrueCount] / self.bettingUnits

			if self.balance < 200:
				amount = 2
			elif self.balance < 1000:
				amount = 3

			# print(f'Balance: {self.balance}\tTrue Count: {roundedTrueCount}\tBet: {round(amount)}')
			return round(amount)
		else:
			return 1

	def playHand(self, userHand, dealerHand, alreadySplit):
		# default to hard total
		table = 'hard'
		total = sum(userHand)
		dealer = dealerHand[0]

		# check if we can use pair table
		if len(userHand) == 2 and userHand[0] == userHand[1] and not alreadySplit:
			table = 'pair'
			total = userHand[0]
		
		# check if soft total (but not two aces)
		elif 1 in userHand and userHand != [1,1] and total <= 11:
			table = 'soft'
			total += 10

		# look up in table
		tableEntry = self.tables[table][str(total)][str(dealer)]
		move = tableEntry['move']
		if 'index' in tableEntry and self.trueCount >= tableEntry['index']['count']:
			move = tableEntry['index']['move']

		# if move is to double, check that we haven't already split
		if move == 'Dh' and (alreadySplit or len(userHand) > 2):
			move = 'H'
		elif move == 'Ds' and (alreadySplit or len(userHand) > 2):
			move = 'S'
		
		# return correct move
		if move == 'H':
			return moves.HIT
		elif move == 'S':
			return moves.STAND
		elif move in ['Dh', 'Ds']:
			return moves.DOUBLE
		elif move == 'P':
			return moves.SPLIT
