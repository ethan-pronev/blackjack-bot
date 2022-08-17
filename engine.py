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

		self.balance = 0
		self.bettingUnits = 500 # how many units to divide our bankroll by
		self.betSpread = [0,20,20,20,20,20,20,20] # how many betting units for each true count (array idx)

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
						self.remainingCards += 1 # if dealer has XX treat this as a remaining card
			self.trueCount = self.runningCount / (self.remainingCards / 52)
		else: # if this hand has some cards from the next shoe, figure out which cards those are and only use those to update the count
			self.warmingUp = False # this case also signifies the end of a shoe
			
			self.remainingCards = remaining
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
					self.remainingCards += 1
			self.trueCount = self.runningCount / (self.remainingCards / 52)

	def updateBalance(self, amount):
		self.balance += amount

	def calculateBetAmount(self):
		return 1


		if self.warmingUp:
			return 1
		elif self.trueCount >= 1:
			roundedTrueCount = min(math.floor(self.trueCount),7)
			return self.balance * self.betSpread[roundedTrueCount] / self.bettingUnits
		else:
			return 2

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
		elif 1 in userHand and userHand != [1,1]:
			table = 'soft'
			total += 10

		# look up in table
		tableEntry = self.tables[table][str(total)][str(dealer)]
		move = tableEntry['move']
		if 'index' in tableEntry and self.trueCount >= tableEntry['index']['count']:
			move = tableEntry['index']['move']

		# if move is to double, check that we haven't already split
		if move == 'Dh' and alreadySplit:
			move = 'H'
		elif move == 'Ds' and alreadySplit:
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
