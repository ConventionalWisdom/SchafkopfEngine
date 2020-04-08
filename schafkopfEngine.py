import pandas as pd
import numpy as np
import schafkopfDumbAi as ai
from random import shuffle

class SchafkopfLogik:
    #globale definitionen
    farben = {'Eichel':0, 'Gras':1, 'Herz':2, 'Schelle':3}
    spielerDict={'Name':'Typ', 'Score':0, 'gezogen':0, 'gestellt':False, 'gespritzt':False, 'spielt':False}
    spielerState = {0:spielerDict.copy(), 1:spielerDict.copy(), 2:spielerDict.copy(), 3:spielerDict.copy()}
    # spielZustände = {0:'NeuesSpiel', 1:'KartenVerteilt', 2:'Spiel', 3:'SpielBeendet'}
    satz =  {'Spiel':10,'Lauf':10}


    def erstelleBlatt(self,blattLang):
        if blattLang == 'lang':
            niedrigste = 7
        else:
            niedrigste = 9
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
        #setze Spielerstatus zurueck
        for i in range(0,4):
            self.spielerState[i]['spielt'] = False
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
        kartenProZug = int(kartenProSpieler / 2)
        if self.spielerState[spielerId]['gezogen'] == 0:
            self.spielerState[spielerId]['gezogen'] = kartenProZug
            return karten.iloc[self.zuordnung[spielerId][0:kartenProZug]][['Farbe','Name']]
        else:
            self.spielerState[spielerId]['gezogen'] = kartenProSpieler
            return karten.iloc[self.zuordnung[spielerId][kartenProZug:kartenProSpieler]][['Farbe','Name']]
    
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
        self.spielart = spielArt
        self.darfKartenLegen = True
        return True, str(self.spielerState[spielerId]['Name'] + ' spielt, ' + self.spielerState[self.rollenIstDran]['Name'] + ' kommt raus') #TODO: more detailed
    
    def starteSpiel(self):
        self.zugCounter = 0
        self.stich = {}
        self.rollenGeber = np.mod(self.rollenGeber+1,4)
        self.rollenIstDran = np.mod(self.rollenIstDran+1,4)
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

    def erlaubteKarten(self,spieler):
        #finde alle karten, die aktuell vom Spieler gelegt werden dürfen
        karten = self.spielBlatt
        stich = self.stich
        hand = self.spielBlatt[self.spielBlatt.Status == 'H'+str(spieler)]
        if len(stich.items()) == 0:
            return hand.index
        gesucht = stich['gespielt']
        if gesucht == 'Trumpf':
            #hat der Spieler Trumpf?
            legal = hand[hand.Trumpf]
        else:
            #hat der Spieler die Farbe?
            legal = hand[hand.Farbe == gesucht]

        if len(legal) == 0:
            return hand.index
        else:
            return legal.index
                

    def beendeStich(self):
        #TODO: alle Aktionen, um den aktuellen Stich abzurechnen, herauszufinden wer ihn gewinnt und Tisch für neue Aktion frei zu machen
        gespielt = self.stich['gespielt']
        kartenIdx = [kId for sId, kId in self.stich['liegt']]
        liegt = self.spielBlatt.loc[kartenIdx]
        #jetzt einfach die höchste liegende Karte finden (Farbe oder Trump), sehen wer die auf der Hand hatte und index extrahieren
        stecher = int(liegt[(liegt.Farbe == gespielt) | (liegt.Trumpf)].sort_values('Spiel Rang').iloc[0]['Status'][-1])
        self.spielBlatt.loc[liegt.index,'Status'] = 'S'+str(stecher)

        #stecher kommt raus
        self.rollenIstDran = stecher

        #neuer Zug bzw Ende der Runde
        self.stich = {}
        self.zugCounter = self.zugCounter + 1
        if self.zugCounter == 8:
            ret, msg = self.beendeSpiel()
            return True, msg
        return True, str('Stich beendet, Spieler ' + str(stecher) + ' kommt raus')

    def beendeSpiel(self):
        msg = ''
        #TODO: alle Aktionen, um ein Spiel abzurechnen und die Punkte anzupassen
        karten = self.spielBlatt
        punkte = [0, 0] #spieler, nichtspieler
        for i in range(0,4):
            searchStr = 'S'+str(i)
            pts = karten[karten.Status == searchStr]['Wert'].sum()
            if self.spielerState[i]['spielt']:
                punkte[0] = punkte[0] + pts
            else:
                punkte[1] = punkte[1] + pts
        
        #finde laufende
        bonusLauf = 0
        sK = karten.sort_values('Spiel Rang')
        team = True
        for i in range(0,4):
            lauf = i+1
            spielerIdx = int(sK.iloc[i]['Status'][-1])
            priorteam = team
            team = self.spielerState[spielerIdx]['spielt']
            if (i>0) & (priorteam != team):
                break
        #TODO: Wenz und andere Sonderregeln...

        if (self.spielart == 'Farbspiel') & (lauf > 2):
            bonusLauf = lauf * self.satz['Lauf']
        if (self.spielart == 'Wenz') & (lauf > 1):
            bonusLauf = lauf * self.satz['Lauf']

        #Prüfe Schneider
        bonusSchneider = 0
        if np.min(punkte) < 30:
            bonusSchneider = self.satz['Lauf']

        #Faktor Klopfen, Spritzen etc
        #TODO: setze maximum?
        faktor = 1
        for i in range(0,4):
            state = self.spielerState[i]
            if (state['gestellt']) | (state['gespritzt']):
                faktor = faktor * 2

        #Summation und Gutschrift
        summePunkte = faktor * (self.satz['Spiel'] + bonusLauf + bonusSchneider)
        spielerGewonnen = True
        if punkte[0]>=punkte[1]:
            msg = 'Spieler gewinnen'
        else:
            msg = 'Nichtspieler gewinnen'
            spielerGewonnen = False
        
        #schreibe punkte gut
        for i in range(0,4):
            if self.spielerState[i]['spielt'] == spielerGewonnen:
                self.spielerState[i]['Score'] = self.spielerState[i]['Score'] + summePunkte
            else:
                self.spielerState[i]['Score'] = self.spielerState[i]['Score'] - summePunkte

        #Sicherstellen dass niemand Karten legt und Geber weiterschieben
        self.darfKartenLegen = False
        self.rollenGeber = np.mod(self.rollenGeber+1,4)
        return True, msg

    def spieleKarte(self,spielerId,kartenIdx):
        # print('whoop')
        karten = self.spielBlatt
        if spielerId != self.rollenIstDran or not self.darfKartenLegen:
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
            legal = self.erlaubteKarten(spielerId)
            if kartenIdx not in legal:
                return False, str(self.spielerState[spielerId]['Name'] + ' hat einen illegalen Zug versucht. Depp.')
            self.stich['liegt'].append((spielerId,kartenIdx))

        #weiter zum nächsten Spieler
        self.rollenIstDran = np.mod(self.rollenIstDran+1,4)

        #wenn alle vier gespielt haben, rechne den Stich ab und stelle fest, wer heraus kommt
        msgStr = str('Spieler ' + str(spielerId) + ' hat ' + karten.at[kartenIdx,'Farbe'] + ' ' + karten.at[kartenIdx,'Name'] + ' gespielt')
        ret = True
        if len(self.stich['liegt']) == 4:
            ret, tStr = self.beendeStich()
            msgStr = msgStr + '\n' + tStr

        return ret, msgStr


    def __init__(self):
        self.basisBlatt = self.erstelleBlatt('lang')
        self.rollenGeber = 3
        self.rollenIstDran = 0
        self.darfKartenLegen = False

if __name__ == "__main__":
    sl = SchafkopfLogik()
    ret, msg =sl.starteSpiel()
    print(msg)
    spieler = {}
    for a in range(0,4):
        print('##### Spieler ' + str(a) + ': ')
        neueAi = ai.playerStupidAI(a)
        neueAi.kartenNehmen(sl)
        spieler[a] = neueAi
    print('##### Setze Trumpf und Spiel')
    for s in range(0,4):
        if int(sl.spielBlatt[(sl.spielBlatt.Farbe == 'Eichel') & (sl.spielBlatt.Name == 'Ass')]['Status'].values[0][-1]) != s:
            ret, msg = sl.setzeTrumpfUndSpiel(s,'Eichel','Farbspiel')
            break
    print(msg)
    for r in range(0,8):
        for s in range(0,4):
            sIdx = sl.rollenIstDran
            print('Spieler ' + str(sIdx) + ' ist dran. Karten auf der Hand:')
            print(spieler[sIdx].karten)
            spieler[sIdx].spielen(sl)
            # idx = int(input('tell me which card to play [by index]'))
            # print('Spieler ' + str(sIdx) + 'hat gespielt. Verbleibende Karten auf der Hand:')
            # print(cards[s])
