from propellant import Propellant, Propellant_Mix, Pressurant
from nist_reader import propellant_data
from numpy import pi

class Material(object):
    def __init__(self,yield_strength,density):
        self.yield_strength = yield_strength
        self.density = density

class Vehicle(object):
    def __init__(self,propellant_mix,material,pressurant,diameter):
        self.propellant_mix = propellant_mix
        self.material = material
        self.pressurant = pressurant
        self.radius = diameter/2

        #Tank volume that must be gas - change if current thinking changes, but a good rule of thumb
        self.ullage = 0.1

        self.temperature = self.propellant_mix.temperature
    
    def calculate_minimum_tank_thickness(self):
        pressure = self.propellant_mix.pressure * 100000

        thickness = pressure * self.radius / self.material.yield_strength

        print(thickness,thickness*1000)
        self.wall_thickness = thickness
    
    def calculate_representative_pressurant_data(self):
        """
        Representative Pressurant Mass is the mass of pressurant gas needed to fill a Representative Length tank to full pressure, accounting for  
                propellant vapour pressure
        Representative Pressurant System Mass is the mass of spherical tanks + pressurant needed to achieve this

        Warning: includes some arbitrary hard-coded values for pressurant storage
        """
        pressurant_storage_pressure = 210   #bar - lower end of paintball tank pressure
        pressurant_tank_safety_factor = 2  
        pressurant_plumbing_mass_factor = 5    #additional increase in mass of system to account for valves and plumbing - completely arbitrary

        area = (self.radius**2 * pi) - (2 * pi * self.radius * self.wall_thickness)

        fuel_overpressure = (self.propellant_mix.pressure - self.propellant_mix.fuel.pressure(self.temperature)) * (10**5)
        fuel_overpressure_volume = self.rep_fuel_length * area
        fuel_pressurant_mass = fuel_overpressure * fuel_overpressure_volume * self.pressurant.molar_mass / (self.pressurant.R * self.temperature)

        oxidiser_overpressure = (self.propellant_mix.pressure - self.propellant_mix.oxidiser.pressure(self.temperature)) * (10**5)
        oxidiser_overpressure_volume = self.rep_oxidiser_length * area
        oxidiser_pressurant_mass = oxidiser_overpressure * oxidiser_overpressure_volume * self.pressurant.molar_mass / (self.pressurant.R * self.temperature)

        representative_pressurant_mass = fuel_pressurant_mass + oxidiser_pressurant_mass

        pressurant_tank_volume = representative_pressurant_mass * self.pressurant.R * self.temperature / (pressurant_storage_pressure  * (10**5) * self.pressurant.molar_mass)
        pressurant_tank_radius = ((3*pressurant_tank_volume)/(4*pi))**(1/3)

        pressurant_tank_wall_thickness = (pressurant_storage_pressure * (10**5) * pressurant_tank_radius) / (2 * self.material.yield_strength / pressurant_tank_safety_factor)

        pressurant_tank_mass = 4 * pi * (pressurant_tank_radius**2) * pressurant_tank_wall_thickness * self.material.density

        pressurant_system_mass = (pressurant_tank_mass * pressurant_plumbing_mass_factor) + representative_pressurant_mass


        print(representative_pressurant_mass,pressurant_system_mass)

    
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

        self.rep_fuel_length = fuel_length
        self.rep_oxidiser_length = oxidisier_length

        representative_length = fuel_length + oxidisier_length

        representative_mass = 2 * pi * self.radius * self.wall_thickness * representative_length * self.material.density

        representative_mass_fraction = (1+self.propellant_mix.OF_mass_ratio) / representative_mass

        self.rep_mass = representative_mass

        print(representative_length,representative_mass,representative_mass_fraction)
    
    def calculate_representative_engine_data(self):
        print(self.propellant_mix.ISP_sea_level)

    
aluminium = Material(170*(10**6),2700)
pressurants = [Pressurant("helium",0.004,1.66),Pressurant("nitrogen",0.028,1.40),Pressurant("carbon-dioxide",44,1.29)]

ethane_nitrous = Propellant_Mix("ethanol","nitrous",250,17)
test_tank = Vehicle(ethane_nitrous,aluminium,pressurants[1],0.1524)
test_tank.calculate_minimum_tank_thickness()
test_tank.wall_thickness = 0.00325
test_tank.calculate_representative_scales()

test_tank.calculate_representative_pressurant_data()