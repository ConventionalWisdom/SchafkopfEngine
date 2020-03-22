import pandas as pd
import numpy as np
from random import shuffle

class SchafkopfLogik:
    #globale definitionen
    farben = {'Eichel':0, 'Gras':1, 'Herz':2, 'Schelle':3}
    spielerDict={'Name':'Typ', 'gezogen':0, 'gestellt':False, 'gespritzt':False, 'spielt':False}
    spielerState = {0:spielerDict, 1:spielerDict, 2:spielerDict, 3:spielerDict}
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
        self.rundenBlatt = karten
        self.zuordnung = zuordnung
        return True, str('Karten sind gemischt')
        # return karten, zuordnung

    def gebeKarten(self,spieler):
        karten = self.rundenBlatt
        kartenProSpieler = len(karten.index)/4
        if self.spielerState[spieler].gezogen == 0:
            self.spielerState[spieler].gezogen = 4
            return karten.iloc[self.zuordnung[spieler][0:4]][['Farbe','Name']]
        else:
            self.spielerState[spieler].gezogen = kartenProSpieler
            return karten.iloc[self.zuordnung[spieler][4:kartenProSpieler]]['Farbe','Name']
    
    def setzeTrumpfUndSpiel(self,spieler,farbe,spielArt):
        karten = self.rundenBlatt
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
        #finde die Spieler
        self.spielerState[spieler]['spielt'] = True
        if self.suche != 'nix':
            mitspieler = int(str(karten.loc[(karten['Farbe'] == self.suche) & (karten['Name'] == 'Ass'),'Status'].item())[1])
            if spieler == mitspieler:
                raise 
            self.spieler = [spieler, mitspieler]
            self.spielerState[mitspieler]['spielt'] = True
        else:
            self.spieler = [spieler]
        print('Spieler ' + str(self.spieler))
        self.rundenBlatt = karten
        return True, str(self.spielerState[spieler]['Name'] + ' spielt, ' + self.spielerState[self.rollenIstDran]['Name'] + ' kommt raus') #TODO: more detailed
    
    def starteSpiel(self):
        self.zugCounter = 0
        self.rollenGeber = np.mod(self.rollenGeber+1,4)
        self.rollenIstDran = np.mod(self.rollenIstDran+1,4)
        self.liegt = []
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
        else 
            return False, str(self.spielerState[spieler]['Name'] + ' hat zu spät gestellt. Depp.')
    
    def spritze(self, spieler):
        if self.spielerState[spieler]['gezogen'] < len(self.basisBlatt.index)
            return False, str(self.spielerState[spieler]['Name'] + ' wollte zu früh spritzen. Depp.')
        if self.spielerState[spieler]['spielt']:
            return False, str(self.spielerState[spieler]['Name'] + ' wollte spritzen und ist selber Spieler. Depp.')
        if self.zugCounter > 0:
            return False, str(self.spielerState[spieler]['Name'] + ' wollte spritzen, ist aber zu spät dran. Depp.')
        #TODO: Check ob der Spieler schon dran war
        self.spielerState[spieler]['gespritzt'] = True
        return False, str('')

    def prufeKarteLegal(self,spieler,kartenIdx):
        liegt = self.liegt
        karten = self.rundenBlatt
        if len(liegt) == 0:
            return True
        gesucht = self.farbeGesucht
        farbe = karten[kartenIdx]['Farbe']
        if farbe != gesucht:
            return False #TODO: implement all that stuff...
        #TODO: a lot is missing here...
        return True
        

    def spieleKarte(self,spieler,kartenIdx):
        print('whoop')
        #TODO: Implement
        if len(liegt) == 0:
            if karten[kartenIdx]['Trumpf']:
                self.farbeGesucht = 'Trumpf'
            else:
                self.farbeGesucht = karten[kartenIdx]['Name']
        #implement all the turn logic here
        return True


    def __init__(self):
        self.basisBlatt = self.erstelleBlatt('lang')
        self.rollenGeber = 3
        self.rollenIstDran = 0

if __name__ == "__main__":
    sl = SchafkopfLogik()
    sl.verteileKarten()
    print(sl.gebeKarten(0,0))
    #warte auf  Spielentscheidung
    #TODO: logik klopfen
    #TODO: logik spielentscheidung
    spielKarten = sl.setzeTrumpfUndSpiel(0,'Schelle','Farbspiel')
    #TODO: rundenlogik