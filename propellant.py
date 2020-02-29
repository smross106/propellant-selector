"""
Defines the Propellant class, used throughout the program
"""
from numpy import poly1d

from nist_reader import propellant_data, combo_data

oxidisers_phases = {"nitrous":[2,44]}
fuels_phases = {"ammonia":[2,17],"ethane":[2,30],"ethanol":[0,46],"diesel":[0,166]}

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
        else:
            if self.twophase==0:
                return(0)
    
    def liquid_density(self, temperature):
        if type(self.F_pressure)==poly1d:
            return(self.F_density_liquid(temperature))
        else:
            if self.twophase==1:
                return(0)
    
    def vapor_density(self, temperature):
        if type(self.F_pressure)==poly1d and self.twophase!=0:
            return(self.F_density_vapour(temperature))
        else:
            if self.twophase==0:
                return(0)


class Propellant_Mix(object):
    def __init__(self,fuel,oxidiser,temperature,pressure):
        if not (fuel in fuels_phases.keys()):
            return ValueError
        else:
            self.fuel = Propellant(fuels_phases[fuel][0])
            self.fuel_name = fuel
        
        if not oxidiser in oxidisers_phases.keys():
            return ValueError
        else:
            self.oxidiser = Propellant(oxidisers_phases[oxidiser][0])
            self.oxidiser_name = oxidiser
        
        combo_data(self,"combos")

        propellant_data(self.fuel,fuel)
        propellant_data(self.oxidiser,oxidiser)

        self.temperature = temperature
        self.pressure = pressure

        self.OF_mass_ratio = self.OF_molar_ratio * oxidisers_phases[oxidiser][1] / fuels_phases[fuel][1]

        
        if self.fuel.pressure(self.temperature) > self.pressure:
            print("Fuel will self-pressurise to greater than pressure")
            input("Input any value to increase pressure to fuel vapour pressure  ")
            if input!="":
                self.pressure = self.fuel.pressure(self.temperature)

        if self.oxidiser.pressure(self.temperature) > self.pressure:
            print("Oxidiser will self-pressurise to greater than pressure")
            input("Input any value to increase pressure to oxidiser vapour pressure  ")
            if input!="":
                self.pressure = self.oxidiser.pressure(self.temperature)
        
        if self.pressure!=pressure:
            print("New pressure is "+str(round(self.pressure,2))+" bar")


class Pressurant(object):
    def __init__(self,name,molar_mass,R):
        self.name = name
        self.molar_mass = molar_mass
        self.R = R