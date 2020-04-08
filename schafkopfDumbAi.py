import numpy as np
import pandas as pd
import schafkopfEngine

class playerStupidAI:
    def __init__(self, id):
        self.karten = []
        self.id = id
        return

    def kartenNehmen(self, engine):
        k1 = engine.gebeKarten(self.id) 
        #hier klopflogik einfügen
        k2 = engine.gebeKarten(self.id)
        self.karten = pd.concat([k1, k2])
        return

    def spielen(self, engine):
        legal = engine.erlaubteKarten(self.id)
        idx = legal[0]
        ret, msg = engine.spieleKarte(self.id,idx)
        print(msg)
        self.karten = self.karten.drop(idx)
        return
