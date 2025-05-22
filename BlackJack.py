import random

money = 500

class Card:
    number = 0
    suit = 0

    def __init__(self,n,s = ""):
        self.number = n
        self.suit = s

    def PrintCard(self):
        names = "Ace", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", "Jack", "Queen", "King"
        print(names[self.number - 1] + " of " + self.suit)

def GenerateDeck():
    deck = []
    suits = ["Hearts","Spades","diamonds", "clubs"]
    for i in range(13):
        for k in range(4):
            deck.append(Card(i+1,suits[k]))
    return deck

def Shuffle(cardList):
    for i in range(len(cardList)):
        r = random.randint(0,len(cardList) - 1)
        cardList[r],cardList[i] = cardList[i], cardList[r]
    return cardList

def PrintCards(cardList):
    for i in range(len(cardList)):
        cardList[i].PrintCard()

def PrintCardsHouse(cardList):
    print("Face down card")
    for i in range(1,len(cardList)):
        cardList[i].PrintCard()

def CountValues(cardList):
    values = [0]
    for i in range(len(cardList)):
        for k in range(len(values)):
            if cardList[i].number > 10:
                values[k] += 10
            elif cardList[i].number == 1:
                values.append(values[k] + 11)
                values[k] += 1
            else:
                values[k] += cardList[i].number
    values = list(dict.fromkeys(values)) #Removes dublicates
    return values

def CheckBlackJack(cardList):
    return 21 in CountValues(cardList)

def CheckBust(cardList):
    values = CountValues(cardList)
    for value in values:
        if value <= 21:
            return False
    return True

def DealHand(deck,predeterminedCards = None):
    if predeterminedCards == None:
        predeterminedCards = []
    arr = predeterminedCards
    while len(arr) < 2:
        arr.append(deck.pop())
    return arr

def Pair(cards):
    return len(cards) == 2 and cards[0] == cards[1]
        
def Test(money,bet):
    money -= bet
    deck = Shuffle(GenerateDeck())
    hand = DealHand(deck)
    dealer = DealHand(deck)

    print("Dealer has")
    PrintCardsHouse(dealer)
    print("")
    print("Player has")
    PrintCards(hand)
    print("")

    ## ----- Instant actions ----- ## 
    if CheckBlackJack(dealer) and CheckBlackJack(hand):
        print("Player & House has BlackJack!")
        return Payout(money,bet,0)
    if CheckBlackJack(hand): #Win on hand deal
        print("Player has BlackJack!")
        return Payout(money,bet,1)
    if CheckBlackJack(dealer):
        print("House has BlackJack")
        return Payout(money,bet,-1)
    
    print()
    surrender = 0
    while True:
        print("Continue or Surrender?")
        print("1.) Continue")
        print("2.) Surrender")
        surrender = input()
        if surrender in ["1","2",""]:
            break
        else:
            print("Invalid input")
    if surrender == "2":
        return Payout(money,bet,0.5)


    if Pair(hand):
        print("Pair!")

    return PlayerDecision(deck,dealer,hand)

def PlayerDecision(deck,dealer,hand, choiceCount = 0):
    choice = 0
    while True:
        print("1.) Hit")
        print("2.) Stand")
        print("3.) Double down")
        choice = input("Choose an action: ")
        if choice in ["1","2","3","3"]:
            break
        else:
            print("Invalid input!")
            print("")
            print("")
            print("")
            print("")
    

def Payout(money,bet,payoutRatio):
    if payoutRatio < 0:
        print("House Won!")
        return money
    if payoutRatio == 0:
        print("Tie!")
        return money + bet
    if payoutRatio >= 1:
        print("Player Won!")
        print("You gained " + str(bet * payoutRatio) + "!")
        return money + bet + bet * payoutRatio
    if payoutRatio > 0 and payoutRatio < 1:
        print("Player surrended!")
        print("Returned " + str(bet * payoutRatio))
        return money + bet * payoutRatio

Test(money,50)