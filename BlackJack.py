import random
import time
import os
import pickle

class Player:
    name = "Player"
    money = 1000
    hands = None
    #Game stats
    gameCount = 0
    winCount = 0
    loseCount = 0
    tieCount = 0
    cardsDrown = 0
    blackjackCount = 0
    #Money
    moneyBetted = 0
    moneyGained = 0
    moneyLost = 0
    #Player actions
    hitCount = 0
    standFirstCount = 0
    doubleDownCount = 0
    splitCount = 0
    surrenderCount = 0

    def __init__(self, name:str, money:float, hands = None):
        self.name = name
        self.money = money
        self.hands = hands if hands != None else []

class Hand:
    def __init__(self, bet:float, cards = None):
        self.cards = cards if cards != None else []
        self.bet = bet

class Card:
    number = 0
    suit = 0

    def __init__(self,number:int, suit:str = ""):
        self.number = number
        self.suit = suit

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

def PrintListDelay(textList:list[str], delay:float = 0.25, delayLast:bool = False):
    for i in range(len(textList)):
        print(textList[i])
        if i < len(textList[i]) or delayLast:
            time.sleep(delay)

def GenerateDeck(deckCount:int = 1):
    deck = []
    for j in range(deckCount):
        for i in range(13):
            for k in range(4):
                deck.append(Card(i+1,k))
    return deck

def Shuffle(cardList:list):
    for i in range(len(cardList)):
        r = random.randint(0,len(cardList) - 1)
        cardList[r],cardList[i] = cardList[i], cardList[r]
    return cardList

def PrintCards(character:Player, hideFirst:bool = False):
    if len(character.hands) <= 0:
        print(character.name + " doesn't have a bet.")
        return
    if len(character.hands) == 1:
        print(character.name + " has")
        PrintHand(character.hands[0],hideFirst)
    else:
        for handIndex in range(len(character.hands)):
            print(character.name + " has on " + str(handIndex + 1) + ". hand")
            PrintHand(character.hands[handIndex],hideFirst)

def PrintHand(hand:Hand, hideFirst:bool = False):
    time.sleep(0.5)
    for cardIndex in range(len(hand.cards)):
        if hideFirst and cardIndex == 0:
            print("\tFace down card")
        else:
            print("\t" + hand.cards[cardIndex].CardName())
        time.sleep(0.25)

def CountValues(cardList:list[Card]):
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

def CheckValue(cardList:list, value:int):
    return value in CountValues(cardList)

def CheckBust(cardList:list[Card]):
    values = CountValues(cardList)
    for value in values:
        if value <= 21:
            return False
    return True

def ShouldHouseDraw(house:Player):
    values = CountValues(house.hands[0].cards)
    for i in range(len(values)):
        if values[i] < 17:
            return True
    return False

def DrawCard(deck:list[Card], targetHand:list[Card], count:int = 1):
    if len(deck) == 0:
        deck = Shuffle(GenerateDeck())
    for i in range(count):
        targetHand.append(deck.pop())

def DealHand(deck:list[Card],predeterminedCards = None):
    if predeterminedCards == None:
        predeterminedCards = []
    arr = predeterminedCards
    while len(arr) < 2:
        arr.append(deck.pop())
    return arr

def CheckPair(cards:list[Card]):
    return len(cards) == 2 and cards[0].number == cards[1].number

def ClampList(list:list[int],minValue:int,maxValue:int):
    holder = []
    for i in range(len(list)):
        if list[i] >= minValue and list[i] <= maxValue:
            holder.append(list[i])
    return holder

## -------------------- GameLoop loop functions -------------------- ##
def ClearHands(player:Player, house:Player):
    player.hands = []
    house.hands = []

def SetHand(player:Player, deck:list[Card], predefinedCards = None): #Set bet, set hand
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
    player.moneyBetted += bet
    player.cardsDrown += 2 - len(player.hands[-1].cards)
    DrawCard(deck, player.hands[-1].cards, 2 - len(player.hands[-1].cards))
    return player.hands[-1]

def SetUpHouse(house:Player, deck:list[Card]):
    house.hands.append(Hand(0,[]))
    DrawCard(deck,house.hands[0].cards, 2)

def PrintStartingHands(player:Player, house:Player):
    print("You bet for \x1b[38;2;255;255;0m" + str(player.hands[0].bet) + "$\x1b[0m\n")
    PrintCards(house,True)
    PrintCards(player)

def CheckStartingBlackJacks(player:Player, house:Player):
    ## ----- Check Blackjacks ----- ## 
    if CheckValue(house.hands[0].cards,21) and CheckValue(player.hands[0].cards,21):
        print(player.name + " & " + house.name + " has BlackJack!","House has ")
        time.sleep(0.25)
        PrintCards(house,False)
        Player.blackjackCount += 1
        EndBet(player,player.hands[0],0)
        return True
    if CheckValue(player.hands[0].cards,21): #BlackJack
        print(player.name + " has BlackJack!")
        Player.blackjackCount += 1
        EndBet(player,player.hands[0],1,1.5)
        return True
    if CheckValue(house.hands[0].cards,21):
        print(house.name + " has BlackJack!")
        time.sleep(0.25)
        PrintCards(house,False)
        EndBet(player,player.hands[0],-1)
        return True
    return False

def PlayersTurn(player:Player, hand:Hand, deck:list[Card]):
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

def Hit(player:Player, hand:Hand, deck:list[Card]):
    DrawCard(deck,hand.cards)
    player.hitCount += 1
    player.cardsDrown += 1
    print(player.name + " drew " + hand.cards[-1].CardName())
    if CheckBust(hand.cards):
        print(player.name + " busted!")
        EndBet(player,hand,-1)
        return
    if CheckValue(hand.cards,21):
        return
    PrintCards(player)
    return PlayersTurn(player, hand, deck)

def Stand(player:Player, hand:Hand, deck:list[Card]):
    if len(hand.cards) <= 2:
        player.standFirstCount += 1
    return

def DoubleDown(player:Player, hand:Hand, deck:list[Card]):
    player.money -= hand.bet
    player.moneyBetted += hand.bet
    hand.bet *= 2
    player.doubleDownCount += 1
    DrawCard(deck,hand.cards)
    player.cardsDrown += 1
    print(player.name + " drew " + hand.cards[-1].CardName())
    if CheckBust(hand.cards):
        print(player.name + " busted!")
        EndBet(player,hand,-1)
        return
    if CheckValue(hand.cards,21):
        return
    PrintCards(player)
    return

def Surrender(player:Player, hand:Hand, deck:list[Card]):
    player.surrenderCount += 1
    return EndBet(player, hand, 1, 0.5)

def Split(player:Player, hand:Hand, deck:list[Card]):
    cardHolder = hand.cards.pop()
    DrawCard(deck,hand.cards)
    player.cardsDrown += 1
    PrintHand(hand)
    if CheckValue(hand.cards,21):
        print(player.name + " has BlackJack!")
        Player.blackjackCount += 1
        EndBet(player,hand,1,1.5)
    else:
        PlayersTurn(player,hand,deck)
    handHolder = SetHand(player,deck,[cardHolder])
    PrintHand(handHolder)
    if CheckValue(handHolder.cards,21):
        print(player.name + " has BlackJack!")
        Player.blackjackCount += 1
        EndBet(player,handHolder,1,1.5)
    else:
        return PlayersTurn(player,handHolder,deck)

def HousesTurn(house:Player, deck:list[Card]):
    print(house.name + " reveals!")
    time.sleep(0.5)
    PrintCards(house, False)
    #house draws to 17 or up
    while ShouldHouseDraw(house):
        DrawCard(deck,house.hands[0].cards)
        print(house.name + " drew " + house.hands[0].cards[-1].CardName())
        time.sleep(1)   

def CountPoints(player:Player, house:Player):
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

def EndBet(player:Player, hand:Hand, result:int, payoutRatio:float = 1):
    player.gameCount += 1
    time.sleep(1)
    bet = hand.bet
    if hand in player.hands:
        player.hands.remove(hand)
    if result < 0:
        player.loseCount += 1
        player.moneyLost += bet
        print("\x1b[38;2;125;0;0m" + player.name + " lost!\x1b[0m")
        return
    if result == 0:
        print("Tie!")
        player.tieCount += 1
        player.money += bet
        return
    if result > 0:
        if result > 0 and payoutRatio > 0 and payoutRatio < 1: #Surrender
            player.loseCount += 1
            print("\x1b[38;2;125;0;0m" + player.name + " surrended!\x1b[0m")
            time.sleep(0.25)
            print("Returned \x1b[38;2;255;255;0m" + str(bet * payoutRatio) + "$\x1b[0m")
            player.moneyLost += bet * payoutRatio
            player.money += bet * payoutRatio
        else: #Actual victory!
            player.winCount += 1
            print("\x1b[38;2;0;255;0m" + player.name + " won!$\x1b[0m")
            time.sleep(0.25)
            print("You gained \x1b[38;2;255;255;0m" + str(bet * payoutRatio) + "!$\x1b[0m")
            player.moneyGained += bet * payoutRatio
            player.money += bet + bet * payoutRatio
        return

def PlayRound(player:Player, house:Player, deck:list[Card]):
    ClearConsole()
    ClearHands(player, house)
    SetHand(player, deck)
    SetUpHouse(house, deck)
    PrintStartingHands(player,house)
    if not CheckStartingBlackJacks(player, house):
        if len(player.hands) > 0:
            PlayersTurn(player, player.hands[0], deck)

        HousesTurn(house,deck)
        PrintCards(player)
        for hand in player.hands:
            CountPoints(player,house)
    input("Press enter to continue...")

def DisplayStats(player:Player):
    ClearConsole()
    PrintListDelay([
        player.name + "'s stats:",
        "\tGame:",
        "\t\tTotal games: " + str(player.gameCount),
        "\t\tGames won: \x1b[38;2;0;" + ("125" if player.winCount > 0 else "0") + ";0m" + str(player.winCount) + "\x1b[0m",
        "\t\tGames lost: \x1b[38;2;" + ("125" if player.loseCount > 0 else "0") +";0;0m" + str(player.loseCount) + "\x1b[0m",
        "\t\tGames tied: " + str(player.loseCount),
        "\t\tCards count: " + str(player.blackjackCount),
        "\t\tBlackjack count: " + str(player.blackjackCount),
        "\tMoney:",
        "\t\tMoney: \x1b[38;2;255;255;0m" + str(player.money) + "$\x1b[0m",
        "\t\tMoney bet: \x1b[38;2;255;255;0m" + str(player.moneyBetted) + "$\x1b[0m",
        "\t\tMoney gained: \x1b[38;2;0;" + ("125" if player.moneyGained > 0 else "0") + ";0m" + str(player.moneyGained) + "$\x1b[0m",
        "\t\tMoney lost: \x1b[38;2;" + ("125" if player.moneyLost > 0 else "0") + ";0;0m" + str(player.moneyLost) + "$\x1b[0m",
        "\tPlaystyle:",
        "\t\tHit: " + str(player.hitCount),
        "\t\tStand on dealt hand: " + str(player.standFirstCount),
        "\t\tDouble down: " + str(player.doubleDownCount),
        "\t\tSplit: " + str(player.splitCount),
        "\t\tSurrender: \x1b[38;2;" + ("125" if player.surrenderCount > 0 else "0") + ";0;0m" + str(player.surrenderCount) + "\x1b[0m",
    ],0.25,True)
    input("Press enter to continue")
    ClearConsole()

def SaveFile(player:Player):
    with open("savefile.pkl", "wb") as f:
        pickle.dump(player, f)

def LoadFile(player:Player):
    with open("savefile.pkl", "rb") as f:
        loadedData = pickle.load(f)
    return loadedData

def MainMenu():
    ClearConsole()
    optionText = []
    optionFunction = []
    optionText.append(str(len(optionText) + 1) + ".) New game")
    optionFunction.append("NewGame")
    if os.path.exists("savefile.pkl"):
        optionText.append(str(len(optionText) + 1) + ".) Load save file")
        optionFunction.append("LoadGame")
    optionText.append(str(len(optionText) + 1) + ".) Quit game")
    optionFunction.append("QuitGame")
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
    ClearConsole()
    return globals()[optionFunction[choice - 1]]()

def NewGame():
    house = Player("House",0)
    deck = Shuffle(GenerateDeck(1))
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
    return GameLoop(player, house, deck)

def LoadGame():
    house = Player("House",0)
    deck = Shuffle(GenerateDeck(1))
    player = LoadFile(Player("",0))
    print("Welcome back " + str(player.name))
    time.sleep(1)
    return GameLoop(player, house, deck)

def QuitGame():
    return

def GameLoop(player:Player, house:Player, deck:list[Card]):
    SaveFile(player)
    ClearConsole()
    choice = None
    while choice not in ["1",""]:
        PrintListDelay(["You currently posess \x1b[38;2;255;255;0m" + str(player.money) + "$\x1b[0m","1.) Play Blackjack","2.) Stats","3.) Quit"],0.25,False)
        choice = input()
        if choice in ["1",""]:
            PlayRound(player, house, deck)
            time.sleep(0.5)
            if player.money < 1:
                PrintListDelay(["Money wasted!","Game over!"],0.25,False)
                os.remove("savefile.pkl")
                return
        elif choice == "2":
            DisplayStats(player)
        elif choice == "3":
            return MainMenu()
        else:
            print("Invalid input")
    ClearConsole()
    return GameLoop(player, house, deck)
MainMenu()