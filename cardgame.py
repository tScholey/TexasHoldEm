import random
import itertools


def evaluateHand(hand):
    values = [card.value for card in hand]
    suits = [card.suit for card in hand]

    # Check for Royal Flush
    if all(val in (10, 11, 12, 13, 1) for val in values) and len(set(suits)) == 1:
        return "Royal Flush"

    # Check for Straight Flush
    if len(set(suits)) == 1:
        min_val = min(values)
        if all(val == min_val + i for i, val in enumerate(values)):
            return "Straight Flush"

    # Check for Four of a Kind
    if len(set(values)) == 2:
        for val in set(values):
            if values.count(val) == 4:
                return "Four of a Kind"

    # Check for Full House
    if len(set(values)) == 2:
        for val in set(values):
            if values.count(val) == 3:
                return "Full House"

    # Check for Flush
    if len(set(suits)) == 1:
        return "Flush"

    # Check for Straight
    min_val = min(values)
    if all(val == min_val + i for i, val in enumerate(values)):
        return "Straight"

    # Check for Three of a Kind
    for val in set(values):
        if values.count(val) == 3:
            return "Three of a Kind"

    # Check for Two Pair
    if len(set(values)) == 3:
        return "Two Pair"

    # Check for Pair
    for val in set(values):
        if values.count(val) == 2:
            return "Pair"

    # Otherwise, return High Card
    return "High Card"

handRankings = {
    "Royal Flush": 10,
    "Straight Flush": 9,
    "Four of a Kind": 8,
    "Full House": 7,
    "Flush": 6,
    "Straight": 5,
    "Three of a Kind": 4,
    "Two Pair": 3,
    "Pair": 2,
    "High Card": 1
}

class Card:
    def __init__(self, value, suit):
        self.value = value
        self.suit = suit
    def __repr__(self):
        vals = {1 : "Ace",
                2 : "Two",
                3 : "Three",
                4 : "Four",
                5 : "Five",
                6 : "Six",
                7 : "Seven",
                8 : "Eight",
                9 : "Nine",
                10 : "Ten",
                11 : "Jack",
                12 : "Queen",
                13 : "King"
            }
        return f"{vals[self.value]} of {self.suit}"

class Deck:
    def __init__(self):
        self.deck = [Card(value,suit) for suit in ("Diamonds", "Spades", "Clubs", "Hearts")
                     for value in range(1,14)]
    def shuffle(self):
        random.shuffle(self.deck)
    
    def deal(self, toDeal):
        return [self.deck.pop() for i in range(toDeal)]


class Player:
    def __init__(self, name, cash):
        self.cash = cash
        self.hand = []
        self.name = name
    
    def __repr__(self):
        return f"{self.name} with £{self.cash}, holding {self.hand}"
    
    def addCash(self, cash):
        self.cash += cash
    
    def removeCash(self, cash):
        self.cash -= cash
    
    def addToHand(self, card : list):
        self.hand += card
    
    def resetHand(self):
        self.hand = []
    
    def evaluate(self):
        return evaluateHand(self.hand)
    
    def evaluateBest(self, game):
        community = game.community.hand
        pocket = self.hand
        combinations = itertools.combinations(pocket + community, 5)
    
        bestRanking = "High Card"
        bestHand = []
        for combination in combinations:
            ranking = evaluateHand(combination)
            if handRankings[ranking] > handRankings[bestRanking]:
                bestRanking = ranking
                bestHand = combination
        if bestHand == []:
            bestSum = 0
            for combination in combinations:
                sumVal = sum([card.val for card in combination])
                if sumVal > bestSum:
                    bestHand = combination
                    bestSum = sumVal
        return bestRanking, bestHand



class Game:
    def __init__(self, players):
        self.players = players
        self.deck = Deck()
        self.pot = 0
        self.community = Player("__Community",0)
    
    def start(self):
        self.deck.shuffle()
        self.community.resetHand()
        for player in self.players:
            player.resetHand()
            player.addToHand(self.deck.deal(2))    
    def bet(self, player, amnt):
        self.betTrack = {}
        if player.cash < amnt:
            return f"Player {player.name} does not have enough money"
        else:
            self.pot += amnt
            player.removeCash(amnt)
            self.betTrack[player.name] = amnt
        return f"The pot stands at {self.pot} after {player.name} bet £{amnt}"

    def fold(self, player):
        self.players.remove(player)
    
    def nextRound(self):
        if len(self.players) == 1:
            self.finishRound()
        else:
            if len(self.community.hand) == 0:
                self.community.addToHand(self.deck.deal(3))
                return "Flop"
            if len(self.community.hand) == 3:
                self.community.addToHand(self.deck.deal(1))
                return "Turn"
            if len(self.community.hand) == 4:
                self.community.addToHand(self.deck.deal(1))
                return "River"
            else: 
                print("Something has gone wrong!")
    
    def finishRound(self):
        if len(self.players) == 1:
            self.players[0].addCash(self.pot)
            self.pot = 0
            return f"Everyone but {self.players[0].name} folded, so they win £{self.pot} by default!"
        winner = self.players[0]
        winRank, winHand = winner.evaluateBest(self)
        draw = []
        for player in self.players[1:]:
            if self.community.evaluate() == "Royal Flush":
                draw = self.players
                break
            rank, hand = player.evaluateBest(self)
            if handRankings[rank] > handRankings[winRank]:
                draw = []
                winner = player
                winRank = rank
                winHand = hand
            elif handRankings[rank] == handRankings[winRank]:
                handVal = [card.value for card in hand]
                winVal = [card.value for card in winHand]
                handVal.sort()
                winVal.sort()
                
                
                if rank == "Straight Flush":
                    if max(handVal) > max(winVal):
                        winner = player
                        draw = []
                    elif max(handVal) == max(winVal):
                        draw.append(winner)
                        draw.append(player)
                
                
                if rank == "Four of a Kind":
                    if max(handVal, key = handVal.count) > max(winVal, key = winVal.count):
                        winner = player
                        draw = []
                    elif max(handVal, key = handVal.count) == max(winVal, key = winVal.count):
                        handKicker = min(handVal, key = handVal.count)
                        winKicker = max(winVal, key = winVal.count)
                        if handKicker > winKicker:
                            winner = player
                            draw = []
                        if handKicker == winKicker:
                            draw.append(winner)
                            draw.append(player)

                if rank == "Full House":
                    if max(handVal, key = handVal.count) > max(winVal, key = winVal.count):
                        winner = player
                        draw = []
                    elif max(handVal, key = handVal.count) == max(winVal, key = winVal.count):
                        handKicker = min(handVal, key = handVal.count)
                        winKicker = min(winVal, key = winVal.count)
                        if handKicker > winKicker:
                            winner = player
                            draw = []
                        if handKicker == winKicker:
                            draw.append(winner)
                            draw.append(player)
                
                
                if rank == "Flush":
                    for handCard, winCard in zip(handVal, winVal):
                        if handCard > winCard:
                            winner = player
                            draw = []
                            break
                        elif winCard > handCard:
                            break

                
                
                if rank == "Straight":
                    for handCard, winCard in zip(handVal, winVal):
                        if handCard > winCard:
                            winner = player
                            draw = []
                            break
                        if winCard > handCard:
                            break
                        else:
                            draw.append(winner)
                            draw.append(player)
                    
                
                
                if rank == "Three of a Kind":
                    if max(handVal, key = handVal.count) > max(winVal, key = winVal.count):
                        winner = player
                        draw = []
                    elif max(handVal, key = handVal.count) == max(winVal, key = winVal.count):
                        handKickers = [vals for vals in handVal if vals != max(handVal, key = handVal.count)]
                        winKickers = [vals for vals in winVal if vals != max(winVal, key = winVal.count)]
                        for handCard, winCard in zip(handKickers, winKickers):
                            if handCard > winCard:
                                winner = player
                                draw = []
                                break
                            elif winCard > handCard:
                                break
                        else:
                            draw.append(winner)
                            draw.append(player)
                    
                    
                if rank == "Two Pair":
                    handPairs = [vals for vals in handVal if handVal.count(vals) == 2]
                    winPairs = [vals for vals in winVal if winVal.count(vals) == 2]
                    for handPair, winPair in zip(handPairs, winPairs):
                        if handPair > winPair:
                            winner = player
                            draw = []
                            break
                        elif winPair > handPair:
                            break
                    else:
                        handKicker = min(handVal, key = handVal.count)
                        winKicker = min(winVal, key = winVal.count)
                        if handKicker > winKicker:
                            winner = player
                            draw = []
                        if handKicker == winKicker:
                            draw.append(winner)
                            draw.append(player)
              
                
                if rank == "Pair":
                  if max(handVal, key = handVal.count) > max(winVal, key = winVal.count):
                      winner = player
                      draw = []
                  elif max(handVal, key = handVal.count) == max(winVal, key = winVal.count):
                      handKickers = [vals for vals in handVal if vals != max(handVal, key = handVal.count)]
                      winKickers = [vals for vals in winVal if vals != max(winVal, key = winVal.count)]
                      for handCard, winCard in zip(handKickers, winKickers):
                          if handCard > winCard:
                              winner = player
                              draw = []
                              break
                          elif winCard > handCard:
                              break
                      else:
                          draw.append(winner)
                          draw.append(player)
                    
                    
                if rank == "High Card":
                    for handCard, winCard in zip(handVal, winVal):
                        if handCard > winCard:
                            winner = player
                            draw = []
                            break
                        elif winCard > handCard:
                            break
                    else:
                        draw.append(winner)
                        draw.append(player)
                    
                    
        
        if len(set(draw)) != 0:
            potSplit = self.pot/len(draw)
            for player in set(draw):
                player.addCash(potSplit)
            self.pot = 0
            playerNames = [player.name for player in set(draw)]
            return f"{playerNames} all drew. They have each recieved {potSplit}"
        else:
            winner.addCash(self.pot)
            self.pot = 0
            return f"{winner.name} has won with {winner.evaluateBest(self)}, they get £{self.pot}!"

if __name__ == "__main__":
    p1 = Player("Joe", 100)
    p2 = Player("Jim", 200)
    p3 = Player("Jop", 300)
    p4 = Player("Jimin", 400)
    p5 = Player("Jimbles", 500)
    newGame = Game([p1,p2,p3,p4,p5])
    newGame.start()
    print(newGame.players)
    newGame.nextRound()
    print(newGame.community)
    newGame.nextRound()
    print(newGame.community)
    newGame.nextRound()
    print(newGame.community)
    print(newGame.finishRound())