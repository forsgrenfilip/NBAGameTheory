# -*- coding: utf-8 -*-
import numpy as np


#Shooting Functions:
def shootingReal(Player, ThreePtPRc, DefDifThree, TwoPtPrc, DefDifTwo, ThreePtQuota):
    ''' this function simuletes What shot
    the offencive player chooses to shoot
    based on data gathered from NBA.com 
    (plyoffs 19-20). (defencive player
    is assumed to adapt and defend 2pt and 3pt
    poportinatly to the offencive player'''    
    
    ###Shotig Percentages
    ShootingPrc = np.array([[(float(ThreePtPRc[Player])*0.01-DefDifThree), (float(TwoPtPrc[Player])*0.01+DefDifTwo)],[(float(ThreePtPRc[Player])*0.01+DefDifThree), (float(TwoPtPrc[Player])*0.01-DefDifTwo)]])
    
    ### Defence Choice:
    rand = np.random.random()
    if rand < ThreePtQuota[Player]:
        Def = 0                     #defend 3 pt
    else:
        Def = 1                     #defend 2 pt
    
    ###Offencive Choice:
    rand = np.random.random()
    if rand < ThreePtQuota[Player]:
        shot = 0                     #shoot 3 pt
    else:
        shot = 1                     #shoot 2 pt
    
    #does the ball go in?
    pts = 0
    rand = np.random.random()
    if Def == 0 and shot == 0 :
        if rand < ShootingPrc[0,0]:
            pts = 3
    elif Def == 1 and shot == 0 :
        if rand < ShootingPrc[1,0]:
            pts = 3
    elif Def == 0 and shot == 1 :
        if rand < ShootingPrc[0,1]:
            pts = 2
    elif Def == 1 and shot == 1 :
        if rand < ShootingPrc[1,1]:
            pts = 2
            
    return pts