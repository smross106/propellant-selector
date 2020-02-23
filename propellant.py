"""
Defines the Propellant class, used throughout the program
"""
from numpy import poly1d

class Propellant(object):
    def __init__(self,phase):
        self.twophase = phase
        #PHASE  0:LIQUID    1:GAS   2:TWO-PHASE

        self.F_density_liquid = None
        self.F_density_vapour = None
        self.F_pressure = None

    def pressure(self,temperature):
        if type(self.F_pressure)==poly1d:
            return(self.F_pressure(temperature))