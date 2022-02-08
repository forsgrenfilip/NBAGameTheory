### import ###
import numpy as np                  
import pandas as pd              
import matplotlib.pyplot as plt       
import math                   
from sympy import symbols, Eq, solve
import time
from shootingOpt import shootingOpt
from shootingReal import shootingReal

########################################################
###################### OPTIONS #########################
########################################################
'''
Choose SimMode=True if you want to simulate a numbers of games and see the outcome,
That is the numbers of point, games won and 7-game-series won by each team over n games.
So, set n = <numbers of games>

Choose SimMode=False to "watch a game", that is viewving the oucome of a game.
Time of score, points scored and winner will be displayed.
set T = <time game will last> (how fast the game will play out, virtual time is always 48min)

Lastly, choose if Miami and Los Angeles will use "Game Theory optimal"/"Real Life Shooting" by setting
TEAMOptOff = True/False.

See https://drive.google.com/file/d/1wGOnZRKl5B-E3BS3Bi8gITDioTEESgxG/view 
to view a short report on the use of the code (it was for school project)

Feel free to play around and use code however you want:)
'''

SimMode = True
n = 1000
T = 2

# True -> Game Theory Optimal, False -> "Real-life Shooting"
MIHOptOff = True
LALOptOff = True



if SimMode:
    Watchmode = False
else:
    Watchmode = True

    
#########################################################
######## Importing NBA Player- and Team stats ###########
#########################################################
'''
(stats in excell file is from playoffs ss19-20 except 3pt% for adebayo wich is from reg ss 19-20)
'''

###Team Data
TeamStat = pd.read_excel('teamstat.xlsx', header=None)
TeamStat = TeamStat.values
TovPrc = np.array([float(TeamStat[1,14])*0.01,float(TeamStat[2,14])*0.01])
NormDReb = np.array([(float(TeamStat[1,12])*0.01) / (float(TeamStat[1,12])*0.01 + float(TeamStat[2,11])*0.01),(float(TeamStat[2,12])*0.01) / (float(TeamStat[2,12])*0.01 + float(TeamStat[1,11])*0.01)])

###PLayer Data
PlayerStat = pd.read_excel('playerstat.xlsx', header=None)
PlayerStat = PlayerStat.values
Players = PlayerStat[1:11,1]
TwoPtPrc = PlayerStat[1:11,11]
ThreePtPRc = PlayerStat[1:11,14]

ThreePtQuota =np.zeros(10)
for i in range(10):
    ThreePtQuota[i] = float(PlayerStat[i+1,13]) / (float(PlayerStat[i+1,10]) + float(PlayerStat[i+1,13]))

SPLakers = np.zeros(5)
SPHeat = np.zeros(5)    
for i in range(5):
    SPHeat[i] = float(PlayerStat[i+1,10]) + float(PlayerStat[i+1,13])
    SPLakers[i] = float(PlayerStat[i+6,10]) + float(PlayerStat[i+6,13])
TotAtHeat = np.sum(SPHeat)
TotAtLakers = np.sum(SPLakers)

for i in range(5):
    if i == 0:
        SPHeat[i] = SPHeat[i] / TotAtHeat
        SPLakers[i] = SPLakers[i] / TotAtLakers
    else:
        SPHeat[i] = (SPHeat[i] / TotAtHeat) + SPHeat[i-1]
        SPLakers[i] = (SPLakers[i] / TotAtLakers) + SPLakers[i-1]
        
DefDifThree = 0.1
DefDifTwo = 0.1
OptOffPlay = np.zeros(10)
for i in range(10):
    DPayoffM = np.array([[-(float(ThreePtPRc[i])*0.01-DefDifThree)*3, -(float(TwoPtPrc[i])*0.01+DefDifTwo)*2],[-(float(ThreePtPRc[i])*0.01+DefDifThree)*3, -(float(TwoPtPrc[i])*0.01-DefDifTwo)*2]])
    p = symbols('p') # probability p that the the offencive player shoots 3pt shot
    eq = Eq( p*DPayoffM[0,0] + (1-p)*DPayoffM[1,0] - (p*DPayoffM[0,1] + (1-p)*DPayoffM[1,1]),0)
    sol = solve(eq)
    OptOffPlay[i] = sol[0]
    
if Watchmode:
    n = 1
    t = T/48
    
    
##########################################################
####################### Game starts ######################
##########################################################

HPtsAllowed = np.zeros(n)
LPtsAllowed = np.zeros(n)
HWins = np.zeros(n)
LWins = np.zeros(n)
HSwins = 0
LSwins = 0
for i in range(n):
    ###jump ball
    GameTime = 0
    Jump = np.random.random()
    if Jump<0.5:
        pos = 0         #Lakers ball
    else:
        pos = 1         #Heat Ball    
    GameTime = 0
    Lpoints = 0
    Hpoints = 0   
    Halftime = True
    Q1 = True
    Q3 = True
    end = False
    while GameTime < 2880 and not end  : # 1 loop = 1 game
        TimePos = np.random.random()*24      #time of possetion
        GameTime = GameTime + TimePos         #gameclock
        MinTime = math.floor(GameTime/60)
        SecTime = math.floor(GameTime%60)
        Clock = str(MinTime)+':'+str(SecTime)
        
        turnover = 0                         #turnover?
        rand = np.random.random()
        if rand < TovPrc[pos]:
            Turnover = 1
            if pos == 0:
                pos = 1
            else:
                pos = 0
        
        elif pos == 0 and turnover == 0:    #Lakers shooting
            rand = np.random.random()       #who is shooting
            if rand < SPLakers[0]:
                Player = 5
            elif SPLakers[0] < rand < SPLakers[1]:
                Player = 6
            elif SPLakers[1] < rand < SPLakers[2]:
                Player = 7            
            elif SPLakers[2] < rand < SPLakers[3]:
                Player = 8
            elif SPLakers[3] < rand < SPLakers[4]:
                Player = 9           
                
            if LALOptOff:                   #what strategy?
                Pts = shootingOpt(Player, ThreePtPRc, DefDifThree, TwoPtPrc, DefDifTwo, OptOffPlay)
            else:
                Pts = shootingReal(Player)
                
            Lpoints = Lpoints + Pts
            
            if Pts == 0:                   #rebound
                rand = np.random.random()
                if rand < NormDReb[pos+1]:
                    pos = 1
                else:
                    pos = 0
            else:
                pos = 1
                if Watchmode:
                    print(Players[Player], 'Scores', Pts, 'At time', Clock,'To make it, Miami Heat', Hpoints, '-', Lpoints, 'Los Angeles Lakers')
                    time.sleep(t*TimePos)                
    
        else:                            #Heat shooting
            rand = np.random.random()    #who is shooting
            if rand < SPHeat[0]:
                Player = 0
            elif SPHeat[0] < rand < SPHeat[1]:
                Player = 1
            elif SPHeat[1] < rand < SPHeat[2]:
                Player = 2            
            elif SPHeat[2] < rand < SPHeat[3]:
                Player = 3
            elif SPHeat[3] < rand < SPHeat[4]:
                Player = 4             
            
            if MIHOptOff:                   #what strategy?
                Pts = shootingOpt(Player, ThreePtPRc, DefDifThree, TwoPtPrc, DefDifTwo, OptOffPlay)
            else:
                Pts = shootingReal(Player, ThreePtPRc, DefDifThree, TwoPtPrc, DefDifTwo, ThreePtQuota)
                
            Hpoints = Hpoints + Pts
            
            if Pts == 0:                 #rebound
                rand = np.random.random()
                if rand < NormDReb[pos-1]:
                    pos = 0
                else:
                    pos = 1

            else:
                pos = 0
                if Watchmode:
                    print(Players[Player], 'Scores', Pts, 'At time', Clock,'To make it, Miami Heat', Hpoints, '-', Lpoints, 'Los Angeles Lakers')
                    time.sleep(t*TimePos)                
        
        if Watchmode and GameTime > 1440 and Halftime:
            print('At halftime the score is:', 'Miami Heat', Hpoints, '-', Lpoints, 'Los Angeles Lakers')
            Halftime = False
        if Watchmode and GameTime > 720 and Q1:
            print('After quarter 1 the score is:', 'Miami Heat', Hpoints, '-', Lpoints, 'Los Angeles Lakers')
            Q1= False
        if Watchmode and GameTime > 2160 and Q3:
            print('After quarter 3 the score is:', 'Miami Heat', Hpoints, '-', Lpoints, 'Los Angeles Lakers')
            Q3 = False  
            
        if GameTime > 2880  and Hpoints == Lpoints:   #overtime
            GameTime = 2580        
            
    HPtsAllowed[i] = Lpoints
    LPtsAllowed[i] = Hpoints
    if Hpoints < Lpoints:
        LWins[i] = 1
        end = True
    else:
        HWins[i] = 1
        end = True
        
    if Watchmode:
        print('Game ends: Miami Heat', Hpoints, '-', Lpoints, 'Los Angeles Lakers')
    
    if end:
        if (i+1)%7 == 0:
            HWS = sum(HWins[i-6:i+1])
            LWS = sum(LWins[i-6:i+1])
            if HWS < LWS:
                LSwins = LSwins + 1
            else:
                HSwins = HSwins + 1 


if SimMode:
    HWins = sum(HWins)
    LWins = sum(LWins)
    HPtsAllowedPG = sum(HPtsAllowed) / n
    LPtsAllowedPG = sum(LPtsAllowed) / n
    print('Games',HWins,LWins)
    print('Series', HSwins, LSwins)
    print('Pts Scored', LPtsAllowedPG, HPtsAllowedPG)
    
    data = {"Team":["Miami Heat", "Los Angeles Lakers"],"Series Won":[HSwins,LSwins]}
    dataFrame = pd.DataFrame(data=data)
    dataFrame.plot.bar(x="Team", y="Series Won", rot=70, title="Series won by each team")
    plt.show()
    
    data = {"Team":["Miami Heat", "Los Angeles Lakers"],"Games Won":[HWins,LWins]}
    dataFrame = pd.DataFrame(data=data)
    dataFrame.plot.bar(x="Team", y="Games Won", rot=70, title="Games won by each team")
    plt.show()
    
    data = {"Team":["Miami Heat", "Los Angeles Lakers"],"Points Scored per game":[LPtsAllowedPG,HPtsAllowedPG]}
    dataFrame = pd.DataFrame(data=data)
    dataFrame.plot.bar(x="Team", y="Points Scored per game", rot=70, title="Points scored per game for each team")
    plt.show()