import random
import time
import os
import pickle

def CreateTranslationDict(EnglishWords:list[str], ForeignWords:list[str]) -> dict:
    translation = {}
    for i in range(len(EnglishWords)):
        if ForeignWords[i] not in [None]:
            translation[EnglishWords[i]] = ForeignWords[i]
        else:
            translation[EnglishWords[i]] = EnglishWords[i]
    return translation

def LoadTranslations(language:str|int = None) -> dict:
    #Returns a dictionary that has English words as keys and the translated words as value.
    f = open("translation.csv", encoding="UTF-8")
    englishWords = f.readline().split(';')
    if type(language) == str:
        for x in f:
            x = x.split(';')
            if x[0] == language: #Language found!
                return CreateTranslationDict(englishWords,x)
        print("Error: Language missing for " + language)
        return CreateTranslationDict(englishWords,englishWords)

    if type(language) == int:
        counter = 1
        for x in f:
            x = x.split(';')
            if counter == language:
                return CreateTranslationDict(englishWords,x)
            counter += 1
        return CreateTranslationDict(englishWords,englishWords)
    return CreateTranslationDict(englishWords,englishWords)

translation = LoadTranslations(None)

class Player:
    money = 1000
    hands = None
    #Game stats
    gameCount = 0
    winCount = 0
    loseCount = 0
    tieCount = 0
    cardsDrown = 0
    blackjackCount = 0
    firstGamePlayed = None
    lastGamePlayed = None
    playTime = 0
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

    def __init__(self, name:str, money:float, hands = None) -> None:
        self.name = name
        self.money = money
        self.hands = hands if hands != None else []
        self.firstGamePlayed = time.asctime(time.localtime())

class Hand:
    def __init__(self, bet:float, cards = None):
        self.cards = cards if cards != None else []
        self.bet = bet

class Card:
    def __init__(self, number:int, suit:int):
        self.number = number
        self.suit = suit

    def CardName(self) -> str:
        names = [translation["Ace"], translation["Two"], translation["Three"], translation["Four"], translation["Five"], translation["Six"], translation["Seven"], translation["Eight"], translation["Nine"], translation["Ten"], translation["Jack"], translation["Queen"], translation["King"]]
        suits = [translation["Hearts"],translation["Diamonds"], translation["Clubs"], translation["Spades"]]
        return names[self.number - 1] + " " + translation["of"] + " \x1b[38;2;" + ("125;0;0" if self.suit < 2 else "0;0;125") + "m" + suits[self.suit] + "\x1b[0m"

def ClearConsole():
    print("\x1b[0m") #Clears ANSI escape code
    os.system('cls' if os.name=='nt' else 'clear')

def PrintListDelay(textList:list[str], delay:float = 0.25, delayLast:bool = False) -> None:
    for i in range(len(textList)):
        print(textList[i])
        if i < len(textList[i]) or delayLast:
            time.sleep(delay)

def GenerateDeck(deckCount:int = 1) -> list[Card]:
    deck = []
    for j in range(deckCount):
        for i in range(13):
            for k in range(4):
                deck.append(Card(i+1,k))
    return deck

def Shuffle(cardList:list) -> list[Card]:
    for i in range(len(cardList)):
        r = random.randint(0,len(cardList) - 1)
        cardList[r],cardList[i] = cardList[i], cardList[r]
    return cardList

def PrintCards(character:Player, hideFirst:bool = False):
    if len(character.hands) <= 0: #No hands
        print(character.name + " " + translation["doesn't have set a bet."])
        return
    if len(character.hands) == 1: #Single hand
        print(character.name + " " + translation["has"])
        PrintHand(character.hands[0],hideFirst)
    else: #Multiple hands, splitting.
        for handIndex in range(len(character.hands)):
            print(character.name + " " + translation["has on"] + " " + str(handIndex + 1) + ". " + translation["hand"])
            PrintHand(character.hands[handIndex],hideFirst)

def PrintHand(hand:Hand, hideFirst:bool = False):
    time.sleep(0.5)
    for cardIndex in range(len(hand.cards)):
        if hideFirst and cardIndex == 0:
            print("\t" + translation["Face down card"])
        else:
            print("\t" + hand.cards[cardIndex].CardName())
        time.sleep(0.25)

def CountValues(cardList:list[Card]) -> int:
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

def CheckValue(cardList:list, value:int) -> bool:
    return value in CountValues(cardList)

def CheckBust(cardList:list[Card]) -> bool:
    values = CountValues(cardList)
    for value in values:
        if value <= 21:
            return False
    return True

def ShouldHouseDraw(house:Player) -> bool:
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

def DealHand(deck:list[Card],predeterminedCards = None) -> list[Card]:
    if predeterminedCards == None:
        predeterminedCards = []
    arr = predeterminedCards
    while len(arr) < 2:
        arr.append(deck.pop())
    return arr

def CheckPair(cards:list[Card]) -> bool:
    return len(cards) == 2 and cards[0].number == cards[1].number

def ClampList(list:list[int],minValue:int,maxValue:int) -> list[int]:
    holder = []
    for i in range(len(list)):
        if list[i] >= minValue and list[i] <= maxValue:
            holder.append(list[i])
    return holder

def ClearHands(player:Player, house:Player):
    player.hands = []
    house.hands = []

def SetHand(player:Player, deck:list[Card], predefinedCards = None) -> Hand: #Set bet, set hand
    bet = 0
    print(translation["You currently posess"] + " \x1b[38;2;255;255;0m" + str(player.money) + "$\x1b[0m")
    while True:
        try:
            bet = float(input(translation["Size of the bet"] + ": "))
            if bet > player.money:
                print(translation["You don't have enough money to bet that amount"] + ".")
                continue
            if bet < 1:
                print(translation["Air in pockets, air in head"] + ".")
                continue
            if bet > 10000:
                print(translation["We allow maximium bets of ten thousand dollars here"] + ".")
            break
        except:
            print(translation["Invalid input"] + ". " + translation["Try again"] + ".")
            continue
    player.hands.append(Hand(bet,predefinedCards if predefinedCards != None else []))
    player.hands[-1].bet = bet
    player.money -= bet
    player.moneyBetted += bet
    player.cardsDrown += 2 - len(player.hands[-1].cards)
    DrawCard(deck, player.hands[-1].cards, 2 - len(player.hands[-1].cards))
    return player.hands[-1]

def SetUpHouse(house:Player, deck:list[Card]) -> None:
    house.hands.append(Hand(0,[]))
    DrawCard(deck,house.hands[0].cards, 2)

def PrintStartingHands(player:Player, house:Player) -> None:
    print(translation["You bet for"] + " \x1b[38;2;255;255;0m" + str(player.hands[0].bet) + "$\x1b[0m\n")
    PrintCards(house,True)
    PrintCards(player)

def CheckStartingBlackJacks(player:Player, house:Player) -> bool:
    ## ----- Check Blackjacks ----- ## 
    if CheckValue(house.hands[0].cards,21) and CheckValue(player.hands[0].cards,21):
        print(player.name + " & " + house.name + " " + translation["has BlackJack!"])
        time.sleep(0.25)
        PrintCards(house,False)
        Player.blackjackCount += 1
        EndBet(player,player.hands[0],0)
        return True
    if CheckValue(player.hands[0].cards,21): #BlackJack
        print(player.name + " " + translation["has BlackJack!"])
        Player.blackjackCount += 1
        EndBet(player,player.hands[0],1,1.5)
        return True
    if CheckValue(house.hands[0].cards,21):
        print(house.name + " " + translation["has BlackJack!"])
        time.sleep(0.25)
        PrintCards(house,False)
        EndBet(player,player.hands[0],-1)
        return True
    return False

def PlayersTurn(player:Player, hand:Hand, deck:list[Card]) -> dict[str,any]:
    optionText = []
    optionFunction = []
    optionText.append(str(len(optionText) + 1) + ".) " + translation["Hit"])
    optionFunction.append("Hit")
    optionText.append(str(len(optionText) + 1) + ".) " + translation["Stand"])
    optionFunction.append("Stand")
    if len(hand.cards) <= 2:
        if player.money >= hand.bet:
            optionText.append(str(len(optionText) + 1) + ".) " + translation["Double down, increaces bet to"] + " " + str(hand.bet * 2) + " " + translation["and draws a single card"] + ".")
            optionFunction.append("DoubleDown")
        if CheckPair(hand.cards):
            optionText.append(str(len(optionText) + 1) + ".) " + translation["Split, playing both hands as indevituals"] + ".")
            optionFunction.append("Split")
        optionText.append(str(len(optionText) + 1) + ".) " + translation["Surrender, gaining back half of the bet"] + ".")
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
            print(translation["Invalid input"] + ". " + translation["Try again"] + ".")
    return globals()[optionFunction[choice - 1]](player,hand,deck)  

def Hit(player:Player, hand:Hand, deck:list[Card]) -> None:
    DrawCard(deck,hand.cards)
    player.hitCount += 1
    player.cardsDrown += 1
    print(player.name + " " + translation["drew"] +" " + hand.cards[-1].CardName())
    if CheckBust(hand.cards):
        print(player.name + " " + translation["busted!"])
        EndBet(player,hand,-1)
        return
    if CheckValue(hand.cards,21):
        return
    PrintCards(player)
    return PlayersTurn(player, hand, deck)

def Stand(player:Player, hand:Hand, deck:list[Card]) -> None:
    if len(hand.cards) <= 2:
        player.standFirstCount += 1

def DoubleDown(player:Player, hand:Hand, deck:list[Card]) -> None:
    player.money -= hand.bet
    player.moneyBetted += hand.bet
    hand.bet *= 2
    player.doubleDownCount += 1
    DrawCard(deck,hand.cards)
    player.cardsDrown += 1
    print(player.name + " " + translation["drew"] +" " + hand.cards[-1].CardName())
    if CheckBust(hand.cards):
        print(player.name + " " + translation["busted!"])
        EndBet(player,hand,-1)
        return
    if CheckValue(hand.cards,21):
        return
    PrintCards(player)

def Surrender(player:Player, hand:Hand, deck:list[Card]) -> None:
    player.surrenderCount += 1
    return EndBet(player, hand, 1, 0.5)

def Split(player:Player, hand:Hand, deck:list[Card]) -> None:
    cardHolder = hand.cards.pop()
    DrawCard(deck,hand.cards)
    player.cardsDrown += 1
    PrintHand(hand)
    if CheckValue(hand.cards,21):
        print(player.name + " " + translation["has BlackJack!"])
        Player.blackjackCount += 1
        EndBet(player,hand,1,1.5)
    else:
        PlayersTurn(player,hand,deck)
    handHolder = SetHand(player,deck,[cardHolder])
    PrintHand(handHolder)
    if CheckValue(handHolder.cards,21):
        print(player.name + " " + translation["has BlackJack!"])
        Player.blackjackCount += 1
        EndBet(player,handHolder,1,1.5)
    else:
        return PlayersTurn(player,handHolder,deck)

def HousesTurn(house:Player, deck:list[Card]) -> None:
    print(house.name + " " + translation["reveals"] + "!")
    time.sleep(0.5)
    PrintCards(house, False)
    #house draws to 17 or up
    while ShouldHouseDraw(house):
        DrawCard(deck,house.hands[0].cards)
        print(house.name + " " + translation["drew"] + " " + house.hands[0].cards[-1].CardName())
        time.sleep(1)   

def CountPoints(player:Player, house:Player) -> None:
    #Check Busts
    for hand in player.hands[:]:
        if CheckBust(hand.cards):
            print(player.name + " " + translation["busted!"])
            EndBet(player,hand, -1)
    if CheckBust(house.hands[0].cards):
        print(house.name + " " + translation["busted!"])
        return EndBet(player,hand,1)

    if len(player.hands) <= 0:
        return
    # Compare points 
    playerScores = []
    for i in range(len(player.hands)):
        playerScores.append(ClampList(CountValues(player.hands[i].cards),2,21)[-1])
    houseScore = ClampList(CountValues(house.hands[0].cards),2,21)[-1]
    
    for hand in player.hands[:]:
        print(house.name + " " + translation["has a total score of"] + " " + str(houseScore))
        print(player.name + " " + translation["has a total score of"] + " " + str(playerScores[i]))
        time.sleep(1)
        if playerScores[i] == houseScore:
            EndBet(player,hand,0)
        elif playerScores[i] > houseScore:
            EndBet(player,hand,1)
        elif playerScores[i] < houseScore:
            EndBet(player,hand,-1)

def EndBet(player:Player, hand:Hand, result:int, payoutRatio:float = 1) -> None:
    player.gameCount += 1
    time.sleep(1)
    bet = hand.bet
    if hand in player.hands:
        player.hands.remove(hand)
    if result < 0:
        player.loseCount += 1
        player.moneyLost += bet
        print("\x1b[38;2;125;0;0m" + player.name + " " + translation["lost"] + "!\x1b[0m")
        return
    if result == 0:
        print(translation["Tie"] + "!")
        player.tieCount += 1
        player.money += bet
        return
    if result > 0:
        if result > 0 and payoutRatio > 0 and payoutRatio < 1: #Surrender
            player.loseCount += 1
            print("\x1b[38;2;125;0;0m" + player.name + " " + translation["surrended"] + "!\x1b[0m")
            time.sleep(0.25)
            print(translation["Returned"] + " \x1b[38;2;255;255;0m" + str(bet * payoutRatio) + "$\x1b[0m")
            player.moneyLost += bet * payoutRatio
            player.money += bet * payoutRatio
        else: #Actual victory!
            player.winCount += 1
            print("\x1b[38;2;0;255;0m" + player.name + " " + translation["won"] + "!$\x1b[0m")
            time.sleep(0.25)
            print(translation["You gained"] + " \x1b[38;2;255;255;0m" + str(bet * payoutRatio) + "!$\x1b[0m")
            player.moneyGained += bet * payoutRatio
            player.money += bet + bet * payoutRatio
        return

def PlayRound(player:Player, house:Player, deck:list[Card]) -> None:
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
    input(translation["Press enter to continue"] + "...")

def DisplayStats(player:Player) -> None:
    ClearConsole()
    PrintListDelay([
        translation["Stats"] + ": " + player.name,
        "\t" + translation["Game"] + ":",
        "\t\t" + translation["Total games"] + ": " + str(player.gameCount),
        "\t\t" + translation["Games won"] + ": \x1b[38;2;" + ("0;125;0" if player.winCount > 0 else "255;255;255") + "m" + str(player.winCount) + "\x1b[0m",
        "\t\t" + translation["Games lost"] + ": \x1b[38;2;" + ("125;0;0" if player.loseCount > 0 else "255;255;255") +"m" + str(player.loseCount) + "\x1b[0m",
        "\t\t" + translation["Games tied"] + ": " + str(player.loseCount),
        "\t\t" + translation["Cards drown"] + ": " + str(player.cardsDrown),
        "\t\t" + translation["Blackjack count"] + ": " + str(player.blackjackCount),
        "\t\t" + translation["Playing started at"] + ": " + str(player.firstGamePlayed),
        "\t" + translation["Money"] + ":",
        "\t\t" + translation["Money"] + ": \x1b[38;2;255;255;0m" + str(player.money) + "$\x1b[0m",
        "\t\t" + translation["Money bet"] + ": \x1b[38;2;255;255;0m" + str(player.moneyBetted) + "$\x1b[0m",
        "\t\t" + translation["Money gained"] + ": \x1b[38;2;" + ("0;125;0" if player.moneyGained > 0 else "255;255;255") + ";0m" + str(player.moneyGained) + "$\x1b[0m",
        "\t\t" + translation["Money lost"] + ": \x1b[38;2;" + ("125;0;0" if player.moneyLost > 0 else "255;255;255") + "m" + str(player.moneyLost) + "$\x1b[0m",
        "\t" + translation["Playstyle"] + ":",
        "\t\t" + translation["Hit count"] + ": " + str(player.hitCount),
        "\t\t" + translation["Stand on dealt hand"] + ": " + str(player.standFirstCount),
        "\t\t" + translation["Double down count"] + ": " + str(player.doubleDownCount),
        "\t\t" + translation["Split count"] + ": " + str(player.splitCount),
        "\t\t" + translation["Surrender count"] + ": \x1b[38;2;" + ("125;0;0" if player.surrenderCount > 0 else "255;255;255") + "m" + str(player.surrenderCount) + "\x1b[0m",
    ],0.25,True)
    input(translation["Press enter to continue"] + "...")
    ClearConsole()

def SaveFile(player:Player) -> None:
    with open("savefile.pkl", "wb") as f:
        pickle.dump(player, f)

def LoadFile() -> any:
    with open("savefile.pkl", "rb") as f:
        loadedData = pickle.load(f)
    return loadedData

def MainMenu() -> None:
    ClearConsole()
    optionText = []
    optionFunction = []
    optionText.append(str(len(optionText) + 1) + ".) " + translation["New game"])
    optionFunction.append("NewGame")
    if os.path.exists("savefile.pkl"):
        optionText.append(str(len(optionText) + 1) + ".) " + translation["Load save file"])
        optionFunction.append("LoadGame")
    optionText.append(str(len(optionText) + 1) + ".) " + translation["Settings"])
    optionFunction.append("Settings")
    optionText.append(str(len(optionText) + 1) + ".) " + translation["Quit game"])
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
            print(translation["Invalid input"] + ". " + translation["Try again"] + ".")
    ClearConsole()
    return globals()[optionFunction[choice - 1]]()

def Settings():
    ClearConsole()
    optionText = []
    optionFunction = []
    if os.path.exists("translation.csv"):
        optionText.append(str(len(optionText) + 1) + ".) " + translation["Change language"])
        optionFunction.append("ChooseLanguage")
    optionText.append(str(len(optionText) + 1) + ".) " + translation["Return"])
    optionFunction.append("MainMenu")
    PrintListDelay(optionText,0.25,True)
    choice = None
    while True:
        try:
            choice = int(input())
            if choice < 1 or choice > len(optionText):
                continue
            break
        except:
            print(translation["Invalid input"] + ". " + translation["Try again"] + ".")
    ClearConsole()
    return globals()[optionFunction[choice - 1]]()

def ChooseLanguage():
    global translation
    ClearConsole()
    print(translation["Current language"] + ": " + translation["English"])
    print(translation["Choose the language by index or by name"] + ":")
    f = open("translation.csv")
    counter = 1
    for x in f:
        x = x.split(';')
        print(str(counter) + ". " + x[0])
        counter += 1
    while True:
        choice = input()
        if choice == "":
            return
        if choice.isnumeric():
            if int(choice) < 1 or int(choice) > counter: #Limit to count of the languages
                continue
            translation = LoadTranslations(int(choice) - 1)
            break
        else:
            translation = LoadTranslations(choice)
            break
    return Settings()

def NewGame() -> None:
    house = Player(translation["House"],0)
    deck = Shuffle(GenerateDeck(1))
    name = input(translation["Name"] + ": ")
    while True:
        try:
            money = float(input(translation["Starting money"] + ": "))
            if money < 1:
                print(translation["We don't allow bums. Please leave."])
                return
            if money > 1000000000000000000000:
                print(translation["Don't lie!"])
                return
            break
        except:
            print(translation["Invalid input"] + ". " + translation["Try again"] + ".")
    player = Player(name,money)
    return GameLoop(player, house, deck)

def LoadGame() -> None:
    house = Player(translation["House"],0)
    deck = Shuffle(GenerateDeck(1))
    player = LoadFile()
    print(translation["Welcome back"] + " " + str(player.name))
    time.sleep(1)
    return GameLoop(player, house, deck)

def QuitGame() -> None:
    return

def GameLoop(player:Player, house:Player, deck:list[Card]) -> None:
    SaveFile(player)
    ClearConsole()
    choice = None
    while choice not in ["1",""]:
        PrintListDelay([
            translation["You currently posess"] + " \x1b[38;2;255;255;0m" + str(player.money) + "$\x1b[0m",
            "1.) " + translation["Play Blackjack"],
            "2.) " + translation["Stats"],
            "3.) " + translation["Quit"]]
            ,0.25,False)
        choice = input()
        if choice in ["1",""]:
            PlayRound(player, house, deck)
            time.sleep(0.5)
            if player.money < 1:
                PrintListDelay([translation["Money wasted"] + "!", translation["Game over"] + "!"],0.25,False)
                os.remove("savefile.pkl")
                return
        elif choice == "2":
            DisplayStats(player)
        elif choice == "3":
            return MainMenu()
        else:
            print(translation["Invalid input"])
    ClearConsole()
    return GameLoop(player, house, deck)

MainMenu()