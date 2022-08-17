import numpy as np
import math
from engine import moves

class BlackjackSimulator():

	# Helper methods
	def __newShoe(self):
		shoe = []
		for i in range(16): # 4 decks * 4 suits each = 16
			shoe += [1,2,3,4,5,6,7,8,9,10,10,10,10]
		shuffled = list(np.random.permutation(shoe))
		return shuffled
	
	def __drawCard(self):
		if len(self.shoe) == 0:
			self.shoe = self.__newShoe()
			self.shoesPlayed += 1
		return self.shoe.pop()
	
	def __calculateHandTotal(self, hand):
		total = sum(hand)
		if 1 in hand and total <= 11:
			total += 10
		return total

	def __playerTurn(self, playerHand, dealerHand, betAmount, alreadySplit):
		total = self.__calculateHandTotal(playerHand)
		if total >= 21:
			return [{ 'hand': playerHand, 'bet': betAmount }]

		move = self.engine.playHand(playerHand, dealerHand, alreadySplit)

		if move == moves.HIT:
			playerHand.append(self.__drawCard())
			return self.__playerTurn(playerHand, dealerHand, betAmount, alreadySplit)
		elif move == moves.STAND:
			return [{ 'hand': playerHand, 'bet': betAmount }]
		elif move == moves.DOUBLE:
			betAmount *= 2
			playerHand.append(self.__drawCard())
			return [{ 'hand': playerHand, 'bet': betAmount }]
		elif move == moves.SPLIT:
			hand1 = [playerHand[0], self.__drawCard()]
			hand2 = [playerHand[1], self.__drawCard()]
			return self.__playerTurn(hand1, dealerHand, betAmount, True) + self.__playerTurn(hand2, dealerHand, betAmount, True)

	def __dealerTurn(self, dealerHand):
		total = self.__calculateHandTotal(dealerHand)
		if total < 17:
			dealerHand.append(self.__drawCard())
			return self.__dealerTurn(dealerHand)
		else:
			return dealerHand



	# Constructor
	def __init__(self, engine):
		self.engine = engine
		self.shoe = self.__newShoe()
		self.shoesPlayed = 0
		self.handsPlayed = 0



	# Main method
	def run(self, totalShoes, startBalance):
		self.shoesPlayed = 0
		self.handsPlayed = 0
		self.shoe = self.__newShoe()
		self.engine.balance = startBalance

		# TODO: REMOVE
		prevBalance = self.engine.balance

		while (self.shoesPlayed < totalShoes):
			playerHand = []
			dealerHandFinal = []
			playerHand.append(self.__drawCard())
			dealerHandFinal.append(self.__drawCard())
			playerHand.append(self.__drawCard())
			dealerHandFinal.append(self.__drawCard())
			betAmount = self.engine.calculateBetAmount()


			playerHandsFinal = self.__playerTurn(playerHand, [dealerHandFinal[0], 0], betAmount, False) # hide hole hard to mimic pancake bot (not necessary)

			self.handsPlayed += len(playerHandsFinal)

			bustedHands = []
			blackjackHands = []
			for i in range(len(playerHandsFinal)):
				total = self.__calculateHandTotal(playerHandsFinal[i]['hand'])
				if total > 21:
					bustedHands.append(i)
				if playerHandsFinal[i]['hand'] in [[1,10],[10,1]]:
					blackjackHands.append(i)

			for idx in bustedHands:
				self.engine.updateBalance(-playerHandsFinal[idx]['bet'])
			
			for idx in blackjackHands:
				if dealerHandFinal not in [[1,10],[10,1]]:
					self.engine.updateBalance(math.floor(1.5*playerHandsFinal[idx]['bet']))
			
			for i in range(len(playerHandsFinal)):
				if i not in bustedHands and i not in blackjackHands:
					if dealerHandFinal in [[1,10],[10,1]]:
						self.engine.updateBalance(-playerHandsFinal[i]['bet'])
			
			if len(bustedHands) + len(blackjackHands) < len(playerHandsFinal) and dealerHandFinal not in [[1,10],[10,1]]: # only have dealer turn if at least 1 hand wasnt bust/blackjack and dealer doesn't have blackjack
				dealerHandFinal = self.__dealerTurn(dealerHandFinal)
				dealerTotal = self.__calculateHandTotal(dealerHandFinal)

				for i in range(len(playerHandsFinal)):
					if i not in bustedHands and i not in blackjackHands:
						playerTotal = self.__calculateHandTotal(playerHandsFinal[i]['hand'])
						
						if playerTotal > dealerTotal or dealerTotal > 21:
							self.engine.updateBalance(playerHandsFinal[i]['bet'])
						elif playerTotal < dealerTotal:
							self.engine.updateBalance(-playerHandsFinal[i]['bet'])

			if len(bustedHands) == len(playerHandsFinal): # hide hole card if all hands bust
				dealerHandFinal[1] = 0
			allHands = []
			for hand in playerHandsFinal:
				allHands.append(hand['hand'])
			allHands.append(dealerHandFinal)

			# ----- DEBUGGING ----- #
			# if betAmount < 0:
			# 	break
			# row = [f'Remaining Cards: {self.engine.remainingCards + self.engine.holeCards}', f'Running: {self.engine.runningCount}', f'True: {math.floor(self.engine.trueCount)}', f'Bet: {betAmount}', f'BalanceChange: {self.engine.balance-prevBalance}', f'Player: {allHands[0:len(allHands)-1]}', f'Dealer: {allHands[len(allHands)-1]}']
			# print("{: >22} {: >14} {: >10} {: >11} {: >20} {: >36} {: >26}".format(*row))
			# prevBalance = self.engine.balance
			# ----- DEBUGGING ----- #

			self.engine.updateCount(allHands, len(self.shoe))


		# print(f'Shoes: {totalShoes}')
		# print(f'Hands: {self.handsPlayed}')
		# print(f'Initial Balance: {startBalance}')
		print(f'Final Balance: {self.engine.balance}')
		# print(f'Average Gain per Hand: {(self.engine.balance - startBalance) / self.handsPlayed}')
