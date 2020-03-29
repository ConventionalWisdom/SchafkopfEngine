import pandas as pd
import numpy as np
from random import shuffle

class SchafkopfLogik:
    #globale definitionen
    farben = {'Eichel':0, 'Gras':1, 'Herz':2, 'Schelle':3}
    spielerDict={'Name':'Typ', 'gezogen':0, 'gestellt':False, 'gespritzt':False, 'spielt':False}
    spielerState = {0:spielerDict.copy(), 1:spielerDict.copy(), 2:spielerDict.copy(), 3:spielerDict.copy()}
    gameStateMachine = {0:'NeuesSpiel', 1:'KartenVerteilt', 2:'Spiel', 3:'SpielBeendet'}

    def erstelleBlatt(self,blattLang):
        if blattLang == 'lang':
            niedrigste = 7
        else:
            niedrigste = 8
        werte = {'Ass':11, '10':10, 'König':4, 'Ober':3, 'Unter':2}
        basisRang = {'Ass':0, '10':1, 'König':2, 'Ober':3, 'Unter':4}
        for i,p in enumerate(range(9,niedrigste-1,-1)):
            werte[str(p)] = 0
            basisRang[str(p)] = i+5
        basisKarten = pd.DataFrame([{'Farbe' : f, 'Name': nw, 'Wert' : w, 'Basis Rang' : r} for f,order in self.farben.items() for (nw, w),(nr, r) in zip(werte.items(),basisRang.items())])
        print(basisKarten)
        return basisKarten

    # def updateStatemachine(self):
    #     #use this to govern transitions of the overall game statemachine; call after external interaction calls
    #     #TODO: implement state machine transitions
    #     if self.state == 'Austeilen':
    #         print('.')
    #     if self.state == 'RundenSpiel':
    #         print('.')
    #     return True

    def verteileKarten(self):
        #TODO: Karten mischen und Spielern zuweisen, in 2 ViererBlöcken für Klopf-Mechanismen
        karten = self.basisBlatt.copy()
        gemischt = [i for i in range(0,len(karten.index))]
        shuffle(gemischt)
        position = ['none' for i in range(0,len(karten.index))]
        zuordnung = {i:[] for i in range(0,4)} #benutze um den Spielern Kartenzuteilung zu zeigen
        sIdx = 0
        for i in range(0,len(karten.index)):
            position[gemischt[i]] = 'H' + str(sIdx)
            if len(zuordnung[sIdx]) == 0:
                zuordnung[sIdx] = [gemischt[i]]
            else:
                zuordnung[sIdx].append(gemischt[i])
            sIdx = np.mod(sIdx+1,4)
        karten = karten.assign(Status=position)
        self.spielBlatt = karten
        self.zuordnung = zuordnung
        return True, str('Karten sind gemischt')
        # return karten, zuordnung

    def gebeKarten(self,spielerId):
        karten = self.spielBlatt
        kartenProSpieler = int(len(karten.index)/4)
        if self.spielerState[spielerId]['gezogen'] == 0:
            self.spielerState[spielerId]['gezogen'] = 4
            return karten.iloc[self.zuordnung[spielerId][0:4]][['Farbe','Name']]
        else:
            self.spielerState[spielerId]['gezogen'] = kartenProSpieler
            return karten.iloc[self.zuordnung[spielerId][4:kartenProSpieler]][['Farbe','Name']]
    
    def setzeTrumpfUndSpiel(self,spielerId,farbe,spielArt):
        karten = self.spielBlatt
        self.mitspieler = -1
        if spielArt == 'Farbspiel':
            trumpf = 'Herz'
            self.suche = farbe
        else:
            trumpf = farbe
            self.suche = 'nix'
        if spielArt == 'Farbspiel' or spielArt == 'Solo':
            #Farbspiel oder solo
            #definiere und markiere Trumpfkarten
            karten['Trumpf'] = False
            karten.loc[karten['Farbe'] == trumpf,'Trumpf'] = True
            karten.loc[karten['Name'] == 'Ober','Trumpf'] = True
            karten.loc[karten['Name'] == 'Unter','Trumpf'] = True
            #definiere Rangfolge der Karten unter Berücksichtigung Farbe
            karten = karten.sort_values(by=['Trumpf','Farbe','Basis Rang'],ascending=False)
            karten['Spiel Rang'] = karten['Basis Rang']
            for n,v in self.farben.items():
                #setze einen Offset für die Farben
                if n is not trumpf:
                    #offset untereinander und gegen die Trümpfe
                    karten.loc[karten['Farbe'] == n,'Spiel Rang'] = karten.loc[karten['Farbe'] == n,'Spiel Rang'] + v*10 + 20
                if n is trumpf:
                    #offset für unter und ober
                    karten.loc[karten['Farbe'] == n,'Spiel Rang'] = karten.loc[karten['Farbe'] == n,'Spiel Rang'] + 8
                #setze die Ober und Unter Rangordnung
                karten.loc[(karten['Name'] == 'Ober') & (karten['Farbe'] == n), 'Spiel Rang'] = v
                karten.loc[(karten['Name'] == 'Unter') & (karten['Farbe'] == n), 'Spiel Rang'] = v + 4
            karten = karten.drop(columns='Basis Rang')
            karten = karten.sort_values(by='Spiel Rang')
        print(karten)
        #TODO: add functions for Wenz etc.
        #finde die Spieler
        self.spielerState[spielerId]['spielt'] = True
        if self.suche != 'nix':
            mitspielerId = int(str(karten.loc[(karten['Farbe'] == self.suche) & (karten['Name'] == 'Ass'),'Status'].item())[1])
            if spielerId == mitspielerId:
                raise 
            self.spielerId = [spielerId, mitspielerId]
            self.spielerState[mitspielerId]['spielt'] = True
        else:
            self.spielerId = [spielerId]
        print('Spieler ' + str(self.spielerId))
        self.spielBlatt = karten
        return True, str(self.spielerState[spielerId]['Name'] + ' spielt, ' + self.spielerState[self.rollenIstDran]['Name'] + ' kommt raus') #TODO: more detailed
    
    def starteSpiel(self):
        self.zugCounter = 0
        self.stich = {}
        self.rollenGeber = np.mod(self.rollenGeber+1,4)
        self.rollenIstDran = np.mod(self.rollenIstDran+1,4)
        self.rundeState = 'Austeilen'
        for i in range(0,4):
            self.spielerState[i]['gestellt'] = False
            self.spielerState[i]['gezogen'] = 0
            self.spielerState[i]['gespritzt'] = False
            self.spielerState[i]['spielt'] = False
        self.verteileKarten()
        return True, str('Spiel kann losgehen, zieht eure Karten')
    
    def stelle(self, spieler):
        if self.spielerState['gezogen'] < 5:
            self.spielerState['gestellt'] = True
            return True, str(self.spielerState[spieler]['Name'] + ' hat gestellt')
        else:
            return False, str(self.spielerState[spieler]['Name'] + ' hat zu spät gestellt. Depp.')
    
    def spritze(self, spieler):
        if self.spielerState[spieler]['gezogen'] < len(self.basisBlatt.index):
            return False, str(self.spielerState[spieler]['Name'] + ' wollte zu früh spritzen. Depp.')
        if self.spielerState[spieler]['spielt']:
            return False, str(self.spielerState[spieler]['Name'] + ' wollte spritzen und ist selber Spieler. Depp.')
        if self.zugCounter > 0:
            return False, str(self.spielerState[spieler]['Name'] + ' wollte spritzen, ist aber zu spät dran. Depp.')
        #TODO: Check ob der Spieler schon dran war
        self.spielerState[spieler]['gespritzt'] = True
        return True, str('')

    def prufeKarteLegal(self,spieler,kartenIdx):
        karten = self.spielBlatt
        stich = self.stich
        if len(stich.items()) == 0:
            return True
        gesucht = stich['gespielt']
        farbe = karten.at[kartenIdx,'Farbe']
        trumpf = karten.at[kartenIdx,'Trumpf']
        if (farbe != gesucht) & (~trumpf):
            return False #TODO: implement all that stuff...
        #TODO: a lot is missing here...
        return True

    def beendeStich(self):
        #TODO: alle Aktionen, um den aktuellen Stich abzurechnen, herauszufinden wer ihn gewinnt und Tisch für neue Aktion frei zu machen

        #neuer Zug bzw Ende der Runde
        self.stich = {}
        self.zugCounter = self.zugCounter + 1
        if self.zugCounter == 8:
            self.beendeSpiel()
        return True, str('Stich beendet, xxx kommt raus')

    def beendeSpiel(self):
        #TODO: alle Aktionen, um ein Spiel abzurechnen und die Punkte anzupassen
        for i in range(0,4):
            self.spielerState[i]['spielt'] = False
        return True

    def spieleKarte(self,spielerId,kartenIdx):
        # print('whoop')
        karten = self.spielBlatt
        if spielerId != self.rollenIstDran:
            return False, str(self.spielerState[spielerId]['Name'] + ' versucht zu spielen und ist nicht dran. Depp.')
        if len(self.stich) == 0:
            #first in the round
            if karten.at[kartenIdx,'Trumpf']:
                angespielt = 'Trumpf'
            else:
                angespielt = karten.at[kartenIdx,'Farbe']
            liegt = [(spielerId,kartenIdx)]
            self.stich = {'gespielt':angespielt, 'liegt':liegt}
        else:
            #check whether legal card
            if not self.prufeKarteLegal(spielerId,kartenIdx):
                return False, str(self.spielerState[spielerId]['Name'] + ' hat einen illegalen Zug versucht. Depp.')
            self.stich['liegt'].append((spielerId,kartenIdx))

        #weiter zum nächsten Spieler
        self.rollenIstDran = np.mod(self.rollenIstDran+1,4)

        #wenn alle vier gespielt haben, rechne den Stich ab und stelle fest, wer heraus kommt
        msgStr = str('Spieler ' + str(spielerId) + ' hat ' + karten.at[idx,'Farbe'] + ' ' + karten.at[idx,'Name'] + ' gespielt')
        ret = True
        if len(self.stich['liegt']) == 4:
            ret, tStr = self.beendeStich()
            msgStr = msgStr + '\n' + tStr

        return ret, msgStr


    def __init__(self):
        self.basisBlatt = self.erstelleBlatt('lang')
        self.rollenGeber = 3
        self.rollenIstDran = 0

if __name__ == "__main__":
    sl = SchafkopfLogik()
    ret, msg =sl.starteSpiel()
    print(msg)
    cards = {}
    for a in range(0,4):
        print('##### Spieler ' + str(a) + ': ')
        k1 = sl.gebeKarten(a)
        k2 = sl.gebeKarten(a)
        cards[a] = pd.concat([k1,k2])
    print('##### Setze Trumpf und Spiel')
    ret, msg = sl.setzeTrumpfUndSpiel(0,'Eichel','Farbspiel')
    print(msg)
    for r in range(0,8):
        for s in range(0,4):
            sIdx = sl.rollenIstDran
            print('Spieler ' + str(sIdx) + ' ist dran. Karten auf der Hand:')
            print(cards[s])
            idx = int(input('tell me which card to play [by index]'))
            ret, msg = sl.spieleKarte(sIdx,idx)
            print(msg)
            cards[s] = cards[s].drop(idx)
            # print('Spieler ' + str(sIdx) + 'hat gespielt. Verbleibende Karten auf der Hand:')
            # print(cards[s])
