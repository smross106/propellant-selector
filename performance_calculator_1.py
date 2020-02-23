from propellant import Propellant
from nist_reader import process_data

class Material(object):
    def __init__(self,yield_strength,density):
        self.yield_strength = yield_strength
        self.density = density


class Propellant_Mix(object):
    def __init__(self,fuel,oxidiser,temperature,pressure):
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
        self.pressure = pressure

        
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
    
    


class Tank(object):
    def __init__(self,propellant_mix,material,diameter):
        self.propellant_mix = propellant_mix
        self.material = material
        self.radius = diameter/2
    
    def calculate_minimum_tank_thickness(self):
        pressure = self.propellant_mix.pressure * 100000

        thickness = pressure * self.radius / self.material.yield_strength

        print(thickness,thickness*1000)
        self.wall_thickness = thickness

    


oxidisers_phases = {"nitrous":2}
fuels_phases = {"ammonia":2,"ethane":2}


aluminium = Material(100*(10**6))
        

ethane_nitrous = Propellant_Mix("ethane","nitrous",290,40)
test_tank = Tank(ethane_nitrous,aluminium,0.197)
test_tank.calculate_minimum_tank_thickness()