import pandas as pd
import numpy as np

#globale definitionen
farben = {'Eiche':0, 'Gras':1, 'Herz':2, 'Schelle':3}

def erstelleBlatt(blattLang):
    if blattLang == 'lang':
        niedrigste = 7
    else:
        niedrigste = 8
    werte = {'Ass':11, '10':10, 'König':4, 'Ober':3, 'Unter':2}
    basisRang = {'Ass':0, '10':1, 'König':2, 'Ober':3, 'Unter':4}
    for i,p in enumerate(range(9,niedrigste-1,-1)):
        werte[str(p)] = 0
        basisRang[str(p)] = i+5
    basisKarten = pd.DataFrame([{'Farbe' : f, 'Name': nw, 'Wert' : w, 'Basis Rang' : r} for f,order in farben.items() for (nw, w),(nr, r) in zip(werte.items(),basisRang.items())])
    print(basisKarten)
    return basisKarten

def verteileKarten(karten):
    #TODO: karten Mischen und Spielern zuweisen, in 2 ViererBlöcken für Klopf-Mechanismen
    return karten.copy()
    
def setzeTrumpfUndSpiel(cards,trumpf,spielArt):
    if spielArt == 'Farbspiel' or spielArt == 'Solo':
        #Farbspiel oder solo
        if spielArt == 'Farbspiel':
            trumpf = 'Herz'
        #definiere und markiere Trumpfkarten
        cards['Trumpf'] = False
        cards.loc[cards['Farbe'] == trumpf,'Trumpf'] = True
        cards.loc[cards['Name'] == 'Ober','Trumpf'] = True
        cards.loc[cards['Name'] == 'Unter','Trumpf'] = True
        #definiere Rangfolge der Karten unter Berücksichtigung Farbe
        cards = cards.sort_values(by=['Trumpf','Farbe','Basis Rang'],ascending=False)
        cards['Spiel Rang'] = cards['Basis Rang']
        for n,v in farben.items():
            #setze einen Offset für die Farben
            if n is not trumpf:
                #offset untereinander und gegen die Trümpfe
                cards.loc[cards['Farbe'] == n,'Spiel Rang'] = cards.loc[cards['Farbe'] == n,'Spiel Rang'] + v*10 + 20
            if n is trumpf:
                #offset für unter und ober
                cards.loc[cards['Farbe'] == n,'Spiel Rang'] = cards.loc[cards['Farbe'] == n,'Spiel Rang'] + 8
            #setze die Ober und Unter Rangordnung
            cards.loc[(cards['Name'] == 'Ober') & (cards['Farbe'] == n), 'Spiel Rang'] = v
            cards.loc[(cards['Name'] == 'Unter') & (cards['Farbe'] == n), 'Spiel Rang'] = v + 4
        cards = cards.drop(columns='Basis Rang')
        cards = cards.sort_values(by='Spiel Rang')

    print(cards)
    return cards

if __name__ == "__main__":
    basisKarten = erstelleBlatt('lang')
    spielKarten = verteileKarten(basisKarten)
    #warte auf  Spielentscheidung
    #TODO: logik klopfen
    #TODO: logik spielentscheidung
    spielKarten = setzeTrumpfUndSpiel(spielKarten,'Eiche','Farbspiel')
    #TODO: rundenlogik