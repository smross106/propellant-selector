from propellant import Propellant
from nist_reader import process_data

oxidisers_phases = {"nitrous":2}
fuels_phases = {"ammonia":2,"ethane":2}

class Propellant_Mix(object):
    def __init__(self,fuel,oxidiser,temperature,tank_pressure):
        if not (fuel in fuels_phases.keys()):
            return ValueError
        else:
            self.fuel = Propellant(fuels_phases[fuel])
        
        if not oxidiser in oxidisers_phases.keys():
            return ValueError
        else:
            self.oxidiser = Propellant(oxidisers_phases[oxidiser])

        process_data(self.fuel,fuel)
        process_data(self.oxidiser,oxidiser)

        self.temperature = temperature
        self.tank_pressure = tank_pressure

        print(self.fuel.pressure(self.temperature))
        print(self.oxidiser.pressure(self.temperature))


        

ethane_nitrous = Propellant_Mix("ethane","nitrous",250.1,15)