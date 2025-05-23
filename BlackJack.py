import random
import time
import os

class Player:
    name = "Player"
    money = 1000
    hands = None

    def __init__(self,name,money, hands = None):
        self.name = name
        self.money = money
        self.hands = hands if hands != None else []

class Hand:
    def __init__(self,bet,cards = None):
        self.cards = cards if cards != None else []
        self.bet = bet

class Card:
    number = 0
    suit = 0

    def __init__(self,n,s = ""):
        self.number = n
        self.suit = s

    def CardName(self):
        names = "Ace", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", "Jack", "Queen", "King"
        suits = ["Hearts","Diamonds", "Clubs", "Spades"]
        if self.suit < 2:
            return names[self.number - 1] + " of \x1b[38;2;125;0;0m" + suits[self.suit] + "\x1b[0m"
        else:
            return names[self.number - 1] + " of \x1b[38;2;0;0;125m" + suits[self.suit] + "\x1b[0m"

def ClearConsole():
    print("\x1b[0m") #Clears ANSI escape code
    os.system('cls' if os.name=='nt' else 'clear')

def PrintListDelay(textList,delay = 0.25, delayLast = False):
    for i in range(len(textList)):
        print(textList[i])
        if i < len(textList[i]) or delayLast:
            time.sleep(delay)

def GenerateDeck(deckCount = 1):
    deck = []
    for j in range(deckCount):
        for i in range(13):
            for k in range(4):
                deck.append(Card(i+1,k))
    return deck

def Shuffle(cardList):
    for i in range(len(cardList)):
        r = random.randint(0,len(cardList) - 1)
        cardList[r],cardList[i] = cardList[i], cardList[r]
    return cardList

def PrintCards(character, hideFirst = False):
    print(character.name + " has")
    for hand in character.hands:
        PrintHand(hand,hideFirst)
        print(" ")

def PrintHand(hand, hideFirst = False):
    time.sleep(0.5)
    for cardIndex in range(len(hand.cards)):
        if hideFirst and cardIndex == 0:
            print("\tFace down card")
        else:
            print("\t" + hand.cards[cardIndex].CardName())
        time.sleep(0.25)

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

def ShouldHouseDraw(house):
    values = CountValues(house.hands[0].cards)
    for i in range(len(values)):
        if values[i] < 17:
            return True
    return False

def DrawCard(deck, targetHand, count = 1):
    for i in range(count):
        targetHand.append(deck.pop())

def DealHand(deck,predeterminedCards = None):
    if predeterminedCards == None:
        predeterminedCards = []
    arr = predeterminedCards
    while len(arr) < 2:
        arr.append(deck.pop())
    return arr

def CheckPair(cards):
    return len(cards) == 2 and cards[0].number == cards[1].number

def ClampList(list,minValue,maxValue):
    holder = []
    for i in range(len(list)):
        if list[i] >= minValue and list[i] <= maxValue:
            holder.append(list[i])
    return holder

## -------------------- Main loop functions -------------------- ##
def ClearHands(player,house):
    player.hands = []
    house.hands = []

def SetHand(player, deck, predefinedCards = None): #Set bet, set hand
    bet = 0
    print("You currently posess \x1b[38;2;255;255;0m" + str(player.money) + "$\x1b[0m")
    while True:
        try:
            bet = float(input("Size of the bet: "))
            if bet > player.money:
                print("You don't have enough money to bet that amount")
                continue
            if bet < 1:
                print("Air in pockets, air in head")
                continue
            break
        except:
            print("Invalid input, try again.")
            continue
    player.hands.append(Hand(bet,predefinedCards if predefinedCards != None else []))
    player.hands[-1].bet = bet
    player.money -= bet
    DrawCard(deck, player.hands[-1].cards, 2 - len(player.hands[-1].cards))
    return player.hands[-1]

def SetUpHouse(house, deck):
    house.hands.append(Hand(0,[]))
    DrawCard(deck,house.hands[0].cards, 2)

def PrintStartingHands(player,house):
    print("You bet for \x1b[38;2;255;255;0m" + str(player.hands[0].bet) + "$\x1b[0m\n")
    PrintCards(house,True)
    PrintCards(player)

def CheckStartingBlackJacks(player,house):
    ## ----- Check Blackjacks ----- ## 
    if CheckValue(house.hands[0].cards,21) and CheckValue(player.hands[0].cards,21):
        print(player.name + " & house has BlackJack!","House has ")
        time.sleep(0.25)
        PrintCards(house,False)
        EndBet(player,player.hands[0],0)
        return True
    if CheckValue(player.hands[0].cards,21): #BlackJack
        print(player.name + " has BlackJack!")
        EndBet(player,player.hands[0],1,1.5)
        return True
    if CheckValue(house.hands[0].cards,21):
        print("House has BlackJack!")
        time.sleep(0.25)
        PrintCards(house,False)
        EndBet(player,player.hands[0],-1)
        return True
    return False

def PlayersTurn(player, hand, deck):
    optionText = []
    optionFunction = []
    optionText.append(str(len(optionText) + 1) + ".) Hit")
    optionFunction.append("Hit")
    optionText.append(str(len(optionText) + 1) + ".) Stand")
    optionFunction.append("Stand")
    if len(hand.cards) <= 2:
        if player.money >= hand.bet:
            optionText.append(str(len(optionText) + 1) + ".) Double down, increaces bet to " + str(hand.bet * 2) + " and draws a single card.")
            optionFunction.append("DoubleDown")
        if CheckPair(hand.cards):
            optionText.append(str(len(optionText) + 1) + ".) Split, playing both hands as indevituals.")
            optionFunction.append("Split")
        optionText.append(str(len(optionText) + 1) + ".) Surrender, gaining back half of the bet.")
        optionFunction.append("Surrender")
    PrintListDelay(optionText,0.25,True)
    choice = None
    while True:
        try:
            choice = int(input())
            if choice < 1 or choice > len(optionText):
                continue
            break
        except:
            print("Invalid input")
    return globals()[optionFunction[choice - 1]](player,hand,deck)  

def Hit(player,hand,deck):
    DrawCard(deck,hand.cards)
    print(player.name + " drew " + hand.cards[-1].CardName())
    if CheckBust(hand.cards):
        print(player.name + " busted!")
        EndBet(player,hand,-1)
        return
    if CheckValue(hand.cards,21):
        return
    PrintCards(player)
    return PlayersTurn(player, hand, deck)

def Stand(player, hand, deck):
    return

def DoubleDown(player, hand, deck):
    player.money -= hand.bet
    hand.bet *= 2
    DrawCard(deck,hand.cards)
    print(player.name + " drew " + hand.cards[-1].CardName())
    if CheckBust(hand.cards):
        print(player.name + " busted!")
        EndBet(player,hand,-1)
        return
    if CheckValue(hand.cards,21):
        return
    PrintCards(player)
    return

def Surrender(player, hand, deck):
    return EndBet(player, hand, 1, 0.5)

def Split(player, hand, deck):
    cardHolder = hand.cards.pop()
    DrawCard(deck,hand.cards)
    PrintHand(hand)
    PlayersTurn(player,hand,deck)
    handHolder = SetHand(player,deck,[cardHolder])
    PrintHand(handHolder)
    return PlayersTurn(player,handHolder,deck)

def HousesTurn(house,deck):
    print(house.name + " reveals!")
    time.sleep(0.5)
    PrintCards(house, False)
    #house draws to 17 or up
    while ShouldHouseDraw(house):
        DrawCard(deck,house.hands[0].cards)
        print(house.name + " drew " + house.hands[0].cards[-1].CardName())
        time.sleep(1)   

def CountPoints(player,house):
    #Check Busts
    for hand in player.hands[:]:
        if CheckBust(hand.cards):
            print(player.name + " busted!")
            EndBet(player,hand, -1)
    if CheckBust(house.hands[0].cards):
        print(house.name + " busted!")
        return EndBet(player,hand,1)

    if len(player.hands) <= 0:
        return
    # Compare points 
    playerScores = []
    for i in range(len(player.hands)):
        playerScores.append(ClampList(CountValues(player.hands[i].cards),2,21)[-1])
    houseScore = ClampList(CountValues(house.hands[0].cards),2,21)[-1]
    
    for hand in player.hands[:]:
        print(house.name + " has " + str(houseScore))
        print(player.name + " has " + str(playerScores[i]))
        time.sleep(1)
        if playerScores[i] == houseScore:
            EndBet(player,hand,0)
        elif playerScores[i] > houseScore:
            EndBet(player,hand,1)
        elif playerScores[i] < houseScore:
            EndBet(player,hand,-1)

def EndBet(player, hand ,result,payoutRatio = 1):
    time.sleep(1)
    bet = hand.bet
    if hand in player.hands:
        player.hands.remove(hand)
    if result < 0:
        print("House won!")
        return
    if result == 0:
        print("Tie!")
        player.money += bet
        return
    if result > 0:
        if result > 0 and payoutRatio > 0 and payoutRatio < 1: #Surrender
            print(player.name + " surrended!")
            time.sleep(0.25)
            print("Returned \x1b[38;2;255;255;0m" + str(bet * payoutRatio) + "$\x1b[0m")
            player.money += bet * payoutRatio
        else: #Actual victory!
            print(player.name + " won!")
            time.sleep(0.25)
            print("You gained \x1b[38;2;255;255;0m" + str(bet * payoutRatio) + "!$\x1b[0m")
            player.money += bet + bet * payoutRatio
        return

def PlayRound(player, house, deck):
    ClearConsole()
    ClearHands(player, house)
    SetHand(player, deck)
    SetUpHouse(house, deck)
    PrintStartingHands(player,house)
    if CheckStartingBlackJacks(player, house):
        return

    if len(player.hands) > 0:
        PlayersTurn(player, player.hands[0], deck)

    HousesTurn(house,deck)

    if len(player.hands) > 0:
        CountPoints(player,house)

def Setup():
    name = input("Name: ")
    while True:
        try:
            money = float(input("Starting money: "))
            if money < 1:
                print("Bums aren't allowed in here!")
                return
            break
        except:
            print("Invalid input, try again.")
    player = Player(name,money)
    house = Player("Mc Gillisson",0)
    deck = GenerateDeck(1)#Shuffle()
    Main(player, house, deck)

def Main(player, house, deck):
    time.sleep(0.5)
    print("You currently posess \x1b[38;2;255;255;0m" + str(player.money) + "$\x1b[0m")
    time.sleep(0.5)
    PlayRound(player, house, deck)
    time.sleep(0.5)
    if player.money < 1:
        PrintListDelay(["Money wasted!","Game over!"],0.25,False)
        return
    PrintListDelay(["You currently posess \x1b[38;2;255;255;0m" + str(player.money) + "$\x1b[0m","Do you want to continue?","1.) Continue","2.) Exit"],0.25,False)
    choice = input()
    if choice == "2":
        return
    ClearConsole()
    return Main(player, house, deck)
Setup()