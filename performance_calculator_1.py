from propellant import Propellant, Propellant_Mix, Pressurant
from nist_reader import propellant_data
from numpy import pi

class Material(object):
    def __init__(self,name,yield_strength,density):
        self.name = name
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

        self.rep_pressurant_mass = representative_pressurant_mass
        self.rep_pressurant_system_mass = pressurant_system_mass


    
    def calculate_representative_scales(self):
        """
        Representative Length is the total length of tank required for 1kg of fuel and equivalent oxidiser
        Representative Mass is the mass of tankage (not tanks and propellant) needed to hold the above quantities of propellant
        Representative Prop System Mass is Representative Mass plus mass of propllant needed to fill that
        Representative Mass Fraction is the mass fraction of a tank with Representative Length

        Note that this does not include bulkheads etc - potential future feature?
        """
        bulkhead_mass_factor = 1.25

        effective_fuel_density = (self.ullage * self.propellant_mix.fuel.vapor_density(self.temperature)) + ((1-self.ullage) * self.propellant_mix.fuel.liquid_density(self.temperature))
        effective_oxidiser_density = (self.ullage * self.propellant_mix.oxidiser.vapor_density(self.temperature)) + ((1-self.ullage) * self.propellant_mix.oxidiser.liquid_density(self.temperature))
        area = (self.radius**2 * pi) - (2 * pi * self.radius * self.wall_thickness)

        fuel_length = 1 / (effective_fuel_density * area)
        oxidisier_length = self.propellant_mix.OF_mass_ratio / (effective_oxidiser_density * area)

        self.rep_fuel_length = fuel_length
        self.rep_oxidiser_length = oxidisier_length

        representative_length = fuel_length + oxidisier_length

        representative_mass = 2 * pi * self.radius * self.wall_thickness * representative_length * self.material.density * bulkhead_mass_factor

        representative_system_mass = (1+self.propellant_mix.OF_mass_ratio) + representative_mass

        representative_mass_fraction = (1+self.propellant_mix.OF_mass_ratio) / representative_mass

        self.rep_length = representative_length
        self.rep_mass = representative_mass
        self.rep_system_mass = representative_system_mass

    
    def calculate_representative_engine_data(self):
        """
        Representative thrust - assume a max flow rate of 0.1kg/s for oxidiser
        Representative TWR - representative Thrust divided by (mass of )
        """
        oxidiser_mass_flow = 1
        burn_time =  self.propellant_mix.OF_mass_ratio 
        fuel_mass_flow = 1 / burn_time

        mass_flow = oxidiser_mass_flow + fuel_mass_flow

        representative_thrust = self.propellant_mix.ISP_sea_level * 9.81 * mass_flow

        representative_mass = self.rep_system_mass + self.rep_pressurant_system_mass

        representative_TWR = representative_thrust / representative_mass

        representative_impulse = representative_thrust * burn_time

        self.rep_thrust = representative_thrust
        self.rep_TWR = representative_TWR
        self.rep_impulse = representative_impulse

    
    def __repr__(self):
        return("***Initial Vehicle Parameters: \n"
        "Fuel: " + self.propellant_mix.fuel_name + "\n" +
        "Oxidiser: " + self.propellant_mix.oxidiser_name + "\n" +
        "Propellant temperature: " + str(self.temperature) + "K \n" +
        "Tank pressure: " + str(self.propellant_mix.pressure) + "bar \n" +
        "Tank diameter: " + str(self.radius*2) + "m \n" +
        "Tank material: " + self.material.name + "\n" + 
        "Pressurant: " + self.pressurant.name + "\n \n" +
        "*** Representative Performance of a System with 1kg of fuel *** \n    Masses of tank walls, propellants and pressurising system considered" + "\n" +
        "Length of tank required: {:.2f}".format(self.rep_length) + "m \n" +
        "Tank wall thickness:  {:.2f}".format(self.wall_thickness*1000) + "mm \n" +
        "Mass of tank (including bulkhead estimate):  {:.2f}".format(self.rep_mass) + "kg \n" +
        "Total propellant system mass:  {:.2f}".format(self.rep_system_mass) + "kg \n \n" +
        "Pressurant mass required:  {:.2f}".format(self.rep_pressurant_mass) + "kg \n" +
        "Pressurant system mass estimate:  {:.2f}".format(self.rep_pressurant_system_mass) + "kg \n \n" +
        "*** Representative Thrust and TWR assumes a constant fuel flow rate of 0.1kg/s, and does not factor in engine or airframe mass \n" +
        "Representative burn time :  {:.2f}".format(self.propellant_mix.OF_mass_ratio) + "s \n" +
        "Representative thrust:  {:.2f}".format(self.rep_thrust) + "N \n" +
        "Representative system TWR:  {:.2f}".format(self.rep_TWR) + "\n" +
        "Representative system impulse:  {:.2f}".format(self.rep_impulse) + "Ns \n")

    
aluminium = Material("aluminium",170*(10**6),2700)
pressurants = [Pressurant("helium",0.004,1.66),Pressurant("nitrogen",0.028,1.40),Pressurant("carbon-dioxide",0.044,1.29)]

ethane_nitrous = Propellant_Mix("ammonia","nitrous",250,17)
test_tank = Vehicle(ethane_nitrous,aluminium,pressurants[2],0.1524)
test_tank.calculate_minimum_tank_thickness()
test_tank.wall_thickness = 0.004
test_tank.calculate_representative_scales()
test_tank.calculate_representative_pressurant_data()
test_tank.calculate_representative_engine_data()

print(test_tank)