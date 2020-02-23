from propellant import Propellant
from nist_reader import process_data
from numpy import pi

class Material(object):
    def __init__(self,yield_strength,density):
        self.yield_strength = yield_strength
        self.density = density


class Propellant_Mix(object):
    def __init__(self,fuel,oxidiser,temperature,pressure,OF_ratio):
        if not (fuel in fuels_phases.keys()):
            return ValueError
        else:
            self.fuel = Propellant(fuels_phases[fuel][0])
        
        if not oxidiser in oxidisers_phases.keys():
            return ValueError
        else:
            self.oxidiser = Propellant(oxidisers_phases[oxidiser][0])

        process_data(self.fuel,fuel)
        process_data(self.oxidiser,oxidiser)

        self.temperature = temperature
        self.pressure = pressure

        self.OF_molar_ratio = OF_ratio
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
    
    


class Vehicle(object):
    def __init__(self,propellant_mix,material,diameter):
        self.propellant_mix = propellant_mix
        self.material = material
        self.radius = diameter/2

        #Tank volume that must be gas - change if current thinking changes, but a good rule of thumb
        self.ullage = 0.1

        self.temperature = self.propellant_mix.temperature
    
    def calculate_minimum_tank_thickness(self):
        pressure = self.propellant_mix.pressure * 100000

        thickness = pressure * self.radius / self.material.yield_strength

        print(thickness,thickness*1000)
        self.wall_thickness = thickness
    
    def calculate_representative_scales(self):
        """
        Representative Length is the total length of tank required for 1kg of fuel and equivalent oxidiser
        Representative Mass is the mass of tankage (not tanks and propellant) needed to hold the above quantities of propellant
        Representative Mass Fraction is the mass fraction of a tank with Representative Length

        Note that this does not include bulkheads etc - potential future feature?
        """

        effective_fuel_density = (self.ullage * self.propellant_mix.fuel.vapor_density(self.temperature)) + ((1-self.ullage) * self.propellant_mix.fuel.liquid_density(self.temperature))
        effective_oxidiser_density = (self.ullage * self.propellant_mix.oxidiser.vapor_density(self.temperature)) + ((1-self.ullage) * self.propellant_mix.oxidiser.liquid_density(self.temperature))
        area = (self.radius**2 * pi) - (2 * pi * self.radius * self.wall_thickness)

        fuel_length = 1 / (effective_fuel_density * area)
        oxidisier_length = self.propellant_mix.OF_mass_ratio / (effective_oxidiser_density * area)

        representative_length = fuel_length + oxidisier_length

        representative_mass = 2 * pi * self.radius * self.wall_thickness * representative_length * self.material.density

        representative_mass_fraction = (1+self.propellant_mix.OF_mass_ratio) / representative_mass

        print(representative_length,representative_mass,representative_mass_fraction)

    


oxidisers_phases = {"nitrous":[2,44]}
fuels_phases = {"ammonia":[2,17],"ethane":[2,30]}


aluminium = Material(170*(10**6),2700)
        

ethane_nitrous = Propellant_Mix("ammonia","nitrous",250,17,7)
test_tank = Vehicle(ethane_nitrous,aluminium,0.1524)
test_tank.calculate_minimum_tank_thickness()
test_tank.wall_thickness = 0.00325
test_tank.calculate_representative_scales()