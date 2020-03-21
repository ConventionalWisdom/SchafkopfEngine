import pandas as pd
import numpy as np

#globale definitionen
farben = {'Eiche':0, 'Gras':1, 'Herz':2, 'Schelle':3}

def erstelleBlatt(blattLang):
    if blattLang == 'lang':
        niedrigste = 7
    else:
        niedrigste = 8
    werte = {'Ober' : 3, 'Unter' : 2, 'Ass' : 11, '10' : 10, 'König' : 4}
    basisRang = {'Ass':0, '10':1, 'König':2, 'Ober':3, 'Unter':4}
    for i,p in enumerate(range(9,niedrigste-1,-1)):
        werte[str(p)] = 0
        basisRang[str(p)] = i+5
    basisKarten = pd.DataFrame([{'Farbe' : f, 'Name': nw, 'Wert' : w, 'Basis Rang' : r+10*order} for f,order in farben.items() for (nw, w),(nr, r) in zip(werte.items(),basisRang.items())])
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
        # cards.groupby(['Basis Rang'])
    print(cards)
    return cards

if __name__ == "__main__":
    basisKarten = erstelleBlatt('lang')
    spielKarten = verteileKarten(basisKarten)
    #warte auf  Spielentscheidung
    spielKarten = setzeTrumpfUndSpiel(spielKarten,'Eiche','Farbspiel')