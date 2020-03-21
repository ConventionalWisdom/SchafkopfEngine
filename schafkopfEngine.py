import pandas as pd
import numpy as np
from random import shuffle

class SchafkopfLogik:
    #globale definitionen
    farben = {'Eiche':0, 'Gras':1, 'Herz':2, 'Schelle':3}

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
            position[gemischt[i]] = 'Hand' + str(sIdx)
            if len(zuordnung[sIdx]) == 0:
                zuordnung[sIdx] = [gemischt[i]]
            else:
                zuordnung[sIdx].append(gemischt[i])
            sIdx = np.mod(sIdx+1,4)
        karten = karten.assign(Status=position)
        self.rundenBlatt = karten
        self.zuordnung = zuordnung
        # return karten, zuordnung

    def gebeKarten(self,spieler,runde):
        karten = self.rundenBlatt
        kartenProSpieler = len(karten.index)/4
        if runde == 0:
            return karten.iloc[self.zuordnung[spieler][0:4]][['Farbe','Name']]
        else:
            return karten.iloc[self.zuordnung[spieler][4:kartenProSpieler]]['Farbe','Name']

    def setzeTrumpfUndSpiel(self,trumpf,spielArt):
        karten = self.rundenBlatt
        if spielArt == 'Farbspiel' or spielArt == 'Solo':
            #Farbspiel oder solo
            if spielArt == 'Farbspiel':
                trumpf = 'Herz'
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
        self.rundenBlatt = karten

    def __init__(self):
        self.basisBlatt = self.erstelleBlatt('lang')

if __name__ == "__main__":
    sl = SchafkopfLogik()
    sl.verteileKarten()
    print(sl.gebeKarten(0,0))
    #warte auf  Spielentscheidung
    #TODO: logik klopfen
    #TODO: logik spielentscheidung
    spielKarten = sl.setzeTrumpfUndSpiel('Eiche','Farbspiel')
    #TODO: rundenlogik