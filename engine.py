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

	# hand is an array of numbers 1-10
	def updateCount(self, hand):
		pass

	def updateBalance(self):
		pass

	def calculateBetAmount(self):
		return 1

	def playHand(self):
		return moves.HIT
