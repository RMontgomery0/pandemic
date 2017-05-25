"""
A script to drive the decks/draws for Z-Man Games' Pandemic.
With a fixed seed number allows reproduction of games.

"""

import numpy as np
import numpy.random as npran
from datetime import datetime, timedelta

eventList = ['Special Event: Airlift', 'Special Event: Forecast', 'Special Event: One Quiet Night', 'Special Event: Government Grant', 'Special Event: Resilient Population', 'Special Event: Mobile Hospital','Special Event: Rapid Vaccine Deployment','Special Event: Special Orders','Special Event: New Assignment','Special Event: Remote Treatment','Special Event: Borrowed Time','Special Event: Re-examined Research','Special Event: Commercial Travel Ban']
playEventList = ['Special Event: Forecast','Special Event: One Quiet Night','Special Event: Resilient Population','Special Event: Commercial Travel Ban']
vEpidemicList = ['Epidemic: Government Interference','Epidemic: Unacceptable Loss','Epidemic: Uncounted Populations','Epidemic: Rate Effect','Epidemic: Complex Molecular Strain','Epidemic: Hidden Pocket','Epidemic: Slippery Slope','Epidemic: Chronic Effect']
nEpidemicList = ['Epidemic!','Epidemic!','Epidemic!','Epidemic!','Epidemic!','Epidemic!','Epidemic!','Epidemic!']
roleList = ['Medic','Researcher','Operations Expert','Dispatcher','Scientist', 'Contingency Planner','Quarantine Specialist','Archivist','Epidemiologist','Field Operative','Troubleshooter','Generalist','Containment Specialist','First Repsonder','Field Director','Pilot']
mutationList = ['Mutation: 3 cities','Mutation: 1 city','Mutation: twos go to threes']
mutationInfectCards = ['Mutation: Infect', 'Mutation: Infect']
colorLists = {'black':['Algiers','Cairo','Baghdad','Istanbul','Moscow','Tehran','Karachi','Mumbai','Delhi','Kolkata','Riyadh','Chennai'],
              'blue':['Atlanta', 'San Francisco', 'Chicago', 'Toronto', 'New York', 'Washington', 'London', 'Madrid', 'Paris', 'Essen', 'Milan', 'Saint Petersburg'],
              'red':['Beijing','Shanghai','Tokyo','Seoul','Osaka','Taipei','Manilla','Sydney','Jacarta','Ho Chi Mihn','Hong Kong','Bankok'],
              'yellow':['Los Angeles','Mexico City','Lima','Santiago','Miami','Bogota','Sau Paolo','Buenos Aires','Lagos','Kinshasa','Khartoum','Johannesburg']}


class deck(list):
    def __init__(self, startCards):
        self.cardList = startCards
        self.discardPile = []
        self.eventList = []

    def shuffle(self):
        npran.shuffle(self.cardList)
        
    def draw(self, n=1):
        if len(self.cardList) == 0:
            print ' - Player Deck Exhausted... Game Over'
            return 'Game Over'
        if n == 1:
            drawnCard = self.cardList[:1][0]
            self.cardList = self.cardList[1:]
            self.discardPile.append(drawnCard)
        elif n == -1:
            drawnCard = self.cardList[-1]
            self.cardList = self.cardList[:n]
            self.discardPile.append(drawnCard)
        elif n != 0:
            drawnCard = self.cardList[:n]
            self.cardList = self.cardList[n:]
            for ii in range(n):
                self.discardPile.append(drawnCard[ii])
        return drawnCard
        
    def add(self, newCards, location=0):
        self.cardList = np.insert(self.cardList, location, newCards)
        
    def count(self):
        return len(self.cardList)

    def epidemic(self):
        bottomCard = self.draw(-1)
        print ' !!! Epidemic hits {} !!!'.format(bottomCard)
        print ' Shuffling {} cards back on top:'.format(len(self.discardPile))
        #print self.discardPile
        npran.shuffle(self.discardPile)
        self.add(self.discardPile)
        self.discardPile = []

    def mutation(self):
        bottomCard = self.draw(-1)
        print ' ... Mutation in *****> {} <***** ...'.format(bottomCard)
        

def eventCheck(playerDeck, infectionDeck):
    playOrNo = raw_input(' Play a Special Event card? y/[n] ').lower()
    if playOrNo != 'y':
        print
        return
    
    ## Ask which Special Event they want to play:
    ## (here, we only care about the events which affect the cards drawn)
    for ii, event in enumerate(playEventList):
        print ii+1, event
    try:
        playEvent_index = int(raw_input('Which event would you like to play? [default=none] '))-1
        playEvent = playEventList[playEvent_index]
    except:
        playEvent = ''
    
    ## Do it:
    if playEvent == 'Special Event: Resilient Population':
        resPop_target = raw_input('Which card would you like to ResPop? [default=cancel] ')
        while resPop_target != '':
            if resPop_target in infectionDeck.discardPile:
                infectionDeck.discardPile = np.delete(infectionDeck.discardPile,np.argwhere(infectionDeck.discardPile == resPop_target))
                break
            elif resPop_target in infectionDeck.cardList: ## for when the epidemic already shuffled the card out of the discard pile
                infectionDeck.cardList = np.delete(infectionDeck.cardList, np.argwhere(infectionDeck.cardList == resPop_target))
                break
            else:
                resPop_target = raw_input('... sorry, cound not find that card in the discard pile, try again? [default=cancel] ')
                #infectionDeck.cardList = np.delete(infectionDeck.cardList,np.argwhere(infectionDeck.cardList == resPop_target))
    elif playEvent == 'Special Event: Forecast':
        topCards = infectionDeck.cardList[:6].copy()
        for ii, myCard in enumerate(topCards):
            print ii+1, myCard
        newOrder = raw_input('Please enter a comma separated list of card indices. The first numbers will go on top: ')
        newOrder = list([int(ind) for ind in newOrder.split(',')])
        for ii, oldInd in enumerate(newOrder):
            infectionDeck.cardList[ii] = topCards[oldInd-1]
    elif playEvent == 'Special Event: One Quiet Night':
        pass
    elif playEvent == 'Special Event: Commercial Travel Ban':
        pass
    print
    return playEvent
        

def pandemic(nPlayers=4, nEpidemics=5, useVirulent=False, useMutation=False,
             lenientRoles=True, timeLimit=7*24*60, seed=-1, rk=False):
    if rk: ## Our default game:
        nPlayers=2
        nEpidemics=7
        useVirulent=True
        useMutation=True
        lenientRoles=True
    tStart = datetime.now()
    timeLimit = timedelta(timeLimit/(24.0*60.0)) ## convert from minutes to days
    #print 'Starting play at: {}'.format(tStart)

    if seed == -1: ## If no seed is set, choose one...
        seed = npran.randint(1,1000000)
    print ' Seed = {}\n'.format(seed) ## and regardless, display it
    npran.seed(seed)
    
    ## Set up the epidemics we'll be using:
    if useVirulent:
        myEpidemics = npran.choice(vEpidemicList, nEpidemics, replace=False)
        npran.shuffle(myEpidemics)
    else:
        myEpidemics = npran.choice(nEpidemicList, nEpidemics, replace=False)
    
    ## Set up the special events we'll be using, and shuffle up the player deck:
    nEvents = 2*nPlayers
    myEvents = npran.choice(eventList, nEvents, replace=False)
    playerDeck = deck(np.concatenate([np.concatenate(colorLists.values()), myEvents]))
    playerDeck.shuffle()
    
    ## Set up the base infection deck:
    infectionDeck = deck(np.concatenate(colorLists.values()))
    infectionDeck.shuffle()
    
    ## Draw roles:
    rolePile = deck(np.array(roleList))
    rolePile.shuffle()
    if lenientRoles:
        for iPlayer in range(nPlayers):
            print "Player {} must choose between these roles:".format(iPlayer+1)
            print ' - {}'.format(rolePile.draw())
            print ' - {}'.format(rolePile.draw())
            print
        extraPair = raw_input('Would you like to see an extra pair of roles? y/[n] ').lower()
        if extraPair == 'y':
            print ' - {}'.format(rolePile.draw())
            print ' - {}'.format(rolePile.draw())
            print
    else:
        for iPlayer in range(nPlayers):
            print "Player {}'s role is : {}\n".format(iPlayer+1, rolePile.draw())
    
    ## Draw starting hands:
    tmp = raw_input('Hit Enter when ready to draw starting hands and infect the board! ')
    print
    handSize0 = 9/nPlayers ## (uses integer division to make appropriate hand-sizes for 2-4 players)
    for iPlayer in range(nPlayers):
        print "Player {}'s hand:".format(iPlayer+1)
        for iHand in range(handSize0):
            print ' -----> {} <-----'.format(playerDeck.draw())
    
    ## Add in mutation cards:
    if useMutation:
        playerDeck.add(mutationList)
        playerDeck.shuffle()
        infectionDeck.discardPile.extend(mutationInfectCards)
    
    ## Add in epidemics:
    pileSize = np.repeat(playerDeck.count()/nEpidemics, nEpidemics)
    nBiggerPiles = playerDeck.count() % nEpidemics
    pileSize[:nBiggerPiles] += 1
    for iEp in range(nEpidemics):
        epLoc = npran.randint(pileSize[iEp]+1) ## (could also be after last card)
        playerDeck.add(myEpidemics[iEp], epLoc+pileSize[:iEp].sum()+iEp)
    
    ## Infect the board:
    print
    print 'Infecting the Board:'
    for iInfect in range(3):
        print '  Place {} cubes on...'.format(3-iInfect)
        if useMutation:
            print '   (and {} purple cubes on the first city)'.format(iInfect+1)
        for iCard in range(3):
            print '   - *****> {} <*****'.format(infectionDeck.draw())
    
    ## Loop through draws as the game progresses:
    infectionRate = [2,2,2,3,3,4,4,4]
    nEpidemicsDrawn = 0
    nPlayerDraw = 2
    nDrawn = 0
    nTurns = 0
    nBanTurnsLeft = 0
    eradicatedVirulent = 0
    playEvent = ''
    virulentStrain = ''
    
    action = ''
    while action != 'quit':
        tPlay = datetime.now() - tStart
        if tPlay > timeLimit:
            print ' )))))))))))))))  Time Has Expired... ((((((((((((((('
        print '\nElapsed Time: '+':'.join(str(tPlay).split(':')[:2])
        action = raw_input('Player {} draw phase? (Draw as default, "Help" for help) '.format((nTurns % nPlayers)+1)).lower()
        print
        if action == 'help': ## help menu:
            print 'Next options:'
            print '  -> [] = End Turn (draw cards)'
            print '  -> Help = Show this menu'
            print '  -> Quit = Exit loop'
            print '  -> Eradicate = Toggle "Rate Effect"'
            print '  -> Count = Show Counts'
        elif action == 'count':
            print ' There are {} cards left in the player deck.'.format(len(playerDeck.cardList))
            print ' The pile sizes (including epidemics) are:',pileSize+1
            print ' You have drawn {} cards, {} epidemics, and the infection rate is {}.'.format(nDrawn,nEpidemicsDrawn,infectionRate[nEpidemicsDrawn])
            print ' The cards in the infection discard pile are:'
            print infectionDeck.discardPile
        elif action == 'eradicate':
            if eradicatedVirulent:
                print ' Turning eradication of virulent strain OFF'
            else:
                print ' Turning eradication of virulent strain ON'
            eradicatedVirulent = 1 - eradicatedVirulent
        elif action == '':
            print '---------------------------------------------------------------'
            print "Player {}'s Turn:".format((nTurns % nPlayers)+1)
            nTurns += 1
            nDrawn += nPlayerDraw
            for iCard in range(nPlayerDraw):
                myCard = playerDeck.draw()
                if myCard == 'Game Over':
                    break
                print ' Drawing from the Player Deck -----> {} <-----'.format(myCard)
                if 'Epidemic' in myCard:
                    nEpidemicsDrawn += 1
                    tmp = raw_input(' Enter when ready to see the bottom card...')
                    infectionDeck.epidemic()
                    if 'Epidemic: Rate Effect' in playerDeck.discardPile:
                        if virulentStrain == '':
                            print colorLists.keys()
                            virulentStrain = raw_input('What color is the virulent strain? ').lower()
                        if myCard == 'Epidemic: Hidden Pocket' and eradicatedVirulent:
                            print ' Turning eradication of virulent strain OFF'
                            eradicatedVirulent = 1 - eradicatedVirulent
                if 'Mutation' in myCard:
                    if '1' in myCard:
                        tmp = raw_input(' Enter when ready to see the bottom card...')
                        infectionDeck.mutation()
                    elif '3' in myCard:
                        tmp = raw_input(' Enter when ready to see the bottom cards...')
                        infectionDeck.mutation()
                        infectionDeck.mutation()
                        infectionDeck.mutation()
            if myCard == 'Game Over':
                break

            playEvent = ''
            playEvent = eventCheck(playerDeck, infectionDeck)
            if playEvent == 'Special Event: One Quiet Night':
                nInfect = 0
            elif playEvent == 'Special Event: Commercial Travel Ban':
                nBanTurnsLeft = nPlayers-1
                nInfect = 1
            elif nBanTurnsLeft > 0:
                nInfect = 1
                nBanTurnsLeft -= 1
            else:
                nInfect = infectionRate[nEpidemicsDrawn]
            print ' Drawing {} from the Infection Deck:'.format(nInfect)
            rateEffectTrigger = False
            for iInfect in range(nInfect):
                infected = infectionDeck.draw()
                if ('Epidemic: Rate Effect' in playerDeck.discardPile) and (infected in colorLists[virulentStrain]) and not eradicatedVirulent:
                    rateEffectTrigger = True
                print ' - *****> {} <*****'.format(infected)
                if 'Mutation' in infected:
                    infectionDeck.mutation()
            if rateEffectTrigger:
                print ' Drawing another due to the Rate Effect:'
                infected = infectionDeck.draw()
                print ' - *****> {} <*****'.format(infected)
                if 'Mutation' in infected:
                    infectionDeck.mutation()

    ## After the game, print a reminder about the seed:
    print ' Seed# was {}\n'.format(seed)

