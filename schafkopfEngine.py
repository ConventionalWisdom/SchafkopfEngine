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
    rang = {'Ober' : 0, 'Unter' : 1, 'Ass' : 2, '10' : 3, 'König' : 4}
    for i,p in enumerate(range(9,niedrigste-1,-1)):
        werte[str(p)] = 0
        rang[str(p)] = i+5
    karten = pd.DataFrame([{'Farbe' : f, 'Name': nw, 'Wert' : w, 'Basis Rang' : r} for f,order in farben.items() for (nw, w),(nr, r) in zip(werte.items(),rang.items())])
    print(karten)
    return karten

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
        #definiere rangfolge der Karten


    print(cards)
    return cards

if __name__ == "__main__":
    basisKarten = erstelleBlatt('lang')
    spielKarten = verteileKarten(basisKarten)
    #warte auf  Spielentscheidung
    spielKarten = setzeTrumpfUndSpiel(spielKarten,'Eiche','Farbspiel')