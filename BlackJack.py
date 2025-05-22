import random
import time

class Card:
    number = 0
    suit = 0

    def __init__(self,n,s = ""):
        self.number = n
        self.suit = s

    def CardName(self):
        names = "Ace", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", "Jack", "Queen", "King"
        return names[self.number - 1] + " of " + self.suit

def GenerateDeck(deckCount = 1):
    deck = []
    suits = ["Hearts","Spades","diamonds", "clubs"]
    for j in range(deckCount):
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
        time.sleep(0.25)
        print("\t" + cardList[i].CardName())

def PrintCardshouse(cardList):
    print("\tFace down card")
    for i in range(1,len(cardList)):
        time.sleep(0.25)
        print("\t" + cardList[i].CardName())

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

def CheckValue(cardList,value):
    return value in CountValues(cardList)

def CheckBust(cardList):
    values = CountValues(cardList)
    for value in values:
        if value <= 21:
            return False
    return True

def ShouldHouseDraw(cardList):
    values = CountValues(cardList)
    for i in range(len(values)):
        if values[i] < 17:
            return True
    return False

def DrawCard(deck,targetHand):
    targetHand.append(deck.pop())

def DealHand(deck,predeterminedCards = None):
    if predeterminedCards == None:
        predeterminedCards = []
    arr = predeterminedCards
    while len(arr) < 2:
        arr.append(deck.pop())
    return arr

def Pair(cards):
    return len(cards) == 2 and cards[0] == cards[1]

def ClampList(list,minValue,maxValue):
    holder = []
    for i in range(len(list)):
        if list[i] >= minValue and list[i] <= maxValue:
            holder.append(list[i])
    return holder

def PlayRound(money,bet,deck):
    money -= bet
    hand = DealHand(deck)
    house = DealHand(deck)

    print("House has")
    PrintCardshouse(house)
    time.sleep(1)
    print("")
    print("Player has")
    PrintCards(hand)
    time.sleep(1)
    print("")
    ## ----- Check Blackjacks ----- ## 
    if CheckValue(house,21) and CheckValue(hand,21):
        print("Player & house has BlackJack!")
        return Payout(money,bet,0)
    if CheckValue(hand,21): #Win on hand deal
        print("Player has BlackJack!")
        return Payout(money,bet,1.5)
    if CheckValue(house,21):
        print("house has BlackJack")
        return Payout(money,bet,-1)
    
    # ----- Surrender ----- #
    surrender = 0
    while True:
        print("Continue or Surrender?")
        time.sleep(0.25)
        print("1.) Continue")
        time.sleep(0.25)
        print("2.) Surrender, you will receive back half of your bet")
        surrender = input()
        if surrender in ["1","2",""]:
            break
        else:
            print("Invalid input")
    if surrender == "2":
        return Payout(money,bet,0.5)
    time.sleep(1)

    # ----- Double down ----- #
    if money >= bet:
        while True:
            print("Double down?")
            time.sleep(0.25)
            print("1.) Yes, double my bet to " + str(bet * 2) + " and draw a card.")
            time.sleep(0.25)
            print("2.) No, I will continue normally.")
            doubleDown = input()
            if doubleDown in ["1","2",""]:
                if doubleDown == "1":
                    money -= bet
                    bet *= 2
                    DrawCard(deck,hand)
                    print("Player drew " +  hand[-1].CardName())
                    PrintCards(hand)
                break
            else:
                print("Invalid input")
        time.sleep(1)

    # ----- Split ----- #
    if Pair(hand): #TODO
        #print("Pair!")
        pass

    # ----- Player action ----- #
    choice = 0
    while True:
        if doubleDown == "1":
            break
        print("You have")
        PrintCards(hand)
        time.sleep(1)
        print("")
        print("1.) Hit")
        time.sleep(0.25)
        print("2.) Stand")
        choice = input()
        if choice == "1" or choice == "":
            DrawCard(deck,hand)
            print("Player drew " + hand[-1].CardName())
            time.sleep(1)
            if CheckBust(hand):
                print("Player busted!")
                return Payout(money,bet,-1)
            if CheckValue(hand,21):
                break
        elif choice == "2":
            break
        else:
            print("Invalid input!")
    
    print("House reveals!")
    print("House has ")
    PrintCards(house)
    time.sleep(1)
    #house draws to 17 or up
    while ShouldHouseDraw(house):
        DrawCard(deck,house)
        print("House drew " + house[-1].CardName())
        PrintCards([house[-1]])
        time.sleep(1)

    #Check Busts
    if CheckBust(hand):
        print("Player busted!")
        return Payout(money,bet,-1)
    if CheckBust(house):
        print("house busted!")
        return Payout(money,bet,1)

    # Compare points 
    playerScore = ClampList(CountValues(hand),2,21)[-1]
    houseScore = ClampList(CountValues(house),2,21)[-1]
    
    print("Player has " + str(playerScore) + ", house has " + str(houseScore))
    time.sleep(1)
    if playerScore == houseScore:
        return Payout(money,bet,0)
    if playerScore > houseScore:
        return Payout(money,bet,1)
    if playerScore < houseScore:
        return Payout(money,bet,-1)

def Payout(money,bet,payoutRatio):
    time.sleep(1)
    if payoutRatio < 0:
        print("house Won!")
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

def Setup():
    money = None
    while money == None:
        try:
            money = int(input("Starting money: "))
            break
        except:
            print("Invalid input, try again.")

    deck = Shuffle(GenerateDeck(2))
    Main(money,deck)

def Main(money,deck):
    bet = 0
    time.sleep(0.5)
    print("You currently posess " + str(money) + "$")
    time.sleep(0.5)
    try:
        bet = int(input("Size of the bet: "))
        if bet > money:
            print("You don't have enough money to bet that amount")
            return Main(money,deck)
        if bet <= 1:
            print("Air in pockets, air in head")
            return Main(money,deck)
    except:
        print("Invalid input, try again.")
        return Main(money,deck)
    print("")
    money = PlayRound(money,bet,deck)
    if money < 1:
        time.sleep(0.25)
        print("Money wasted!")
        time.sleep(0.25)
        print("Game over!")
    print("You currently posess " + str(money) + "$")
    time.sleep(0.25)
    print("Do you want to continue?")
    time.sleep(0.25)
    print("1.) Continue")
    time.sleep(0.25)
    print("2.) Exit")
    choice = input()
    if choice == "2":
        return
    return Main(money,deck)
Setup()