import pandas as pd
import numpy as np

def createCards():
    farben = ['Eiche', 'Gras', 'Herz', 'Schelle']
    Werte = {'Ober' : 3, 'Unter' : 2, 'Ass' : 11, '10' : 10, 'König' : 4}
    for i in range(9,6,-1):
        Werte[str(i)] = 0
    karten = pd.DataFrame([{'Farbe' : f, 'Name': n, 'Wert' : w} for f in farben for n,w in Werte.items()])
    print(karten)
    return karten
    
def markTrumpf(cards,trumpf,special):
    if special == 'none':
        #Farbspiel
        #set Trumpf
        cards['Trumpf'] = False
        cards.loc[cards['Farbe'] == trumpf,'Trumpf'] = True
        cards.loc[cards['Name'] == 'Ober','Trumpf'] = True
        cards.loc[cards['Name'] == 'Unter','Trumpf'] = True
        #define order
        cards['Order'] = 0
        cards.loc[cards['Name'] == 'Ober']

    print(cards)
    return cards

if __name__ == "__main__":
    cards = createCards()
    gameSet = markTrumpf(cards,'Eiche','none')