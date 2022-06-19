# model.py
from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from covid_model.data_collectors import *
from covid_model.agents import *
import random
import pandas as pd
import copy

class Covid19Model(Model):

    def __init__(self, variable_params, fixed_params, contact_matrix):
        self.steps = 0
        self.running = True
        self.grid = MultiGrid(50, 50, True)
        self.schedule = RandomActivation(self)
        self.summary = variable_params
        self.contact_matrix = pd.DataFrame(contact_matrix)
        self.infection_rate = fixed_params["infection_rate"]
        self.average_incubation_period = fixed_params["average_incubation_period"]
        self.average_infectious_period = fixed_params["average_infectious_period"]
        self.death_rate = fixed_params["death_rate"]
        self.recovery_rate = fixed_params["recovery_rate"]
        self.wearing_mask = fixed_params["wearing_mask"]
        self.wearing_mask_protection = fixed_params["wearing_mask_protection"]
        self.physical_distancing = fixed_params["physical_distancing"]
        self.physical_distancing_protection = fixed_params["physical_distancing_protection"]
        self.agent_movement_range = fixed_params["agent_movement_range"]

        # Instantiating PersonAgent objects
        age_group_size = 5
        age_group_range = lambda x: (x * age_group_size, (x + 1) * age_group_size - 1)
        for state in self.summary:
            if state not in "RDV":
                for age_group, count in enumerate(self.summary[state]):
                    for i in range(count):
                        unique_id = state + str(age_group) + "-" + str(i)
                        min_age, max_age = age_group_range(age_group)
                        age = random.randint(min_age, max_age)
                        wearing_mask = self.coin_toss(self.wearing_mask) and self.coin_toss(self.wearing_mask_protection)
                        physical_distancing = self.coin_toss(self.physical_distancing) and self.coin_toss(self.physical_distancing_protection)
                        days_incubating = 0 # if state != "E" else random.normalvariate(self.average_incubation_period, 3)
                        days_infected = 0 # if state != "I" else random.normalvariate(self.average_infectious_period, 3)

                        agent = PersonAgent(unique_id, self, state, age, age_group, wearing_mask, physical_distancing, days_incubating, days_infected)

                        x = self.random.randrange(self.grid.width)
                        y = self.random.randrange(self.grid.height)
                        self.grid.place_agent(agent, (x, y))
                        self.schedule.add(agent)

        self.data_collector_total = DataCollector(
            model_reporters={
                "S": get_sum_getter("S"),
                "E": get_sum_getter("E"),
                "I": get_sum_getter("I"),
                "D": get_sum_getter("D"),
                "R": get_sum_getter("R"),
                "V": get_sum_getter("V")})

        self.data_collector_age = DataCollector(
            model_reporters={
                "S": get_state_getter("S"),
                "E": get_state_getter("E"),
                "I": get_state_getter("I"),
                "R": get_state_getter("R"),
                "D": get_state_getter("D"),
                "V": get_state_getter("V")})

        self.total = {
            "S": copy.deepcopy(self.summary["S"]),
            "E": copy.deepcopy(self.summary["E"]),
            "I": copy.deepcopy(self.summary["I"]),
            "R": copy.deepcopy(self.summary["R"]),
            "D": copy.deepcopy(self.summary["D"]),
            "V": copy.deepcopy(self.summary["V"])}

        self.total_added = {
            "S": [0]*17,
            "E": [0]*17,
            "I": [0]*17,
            "R": [0]*17,
            "D": [0]*17,
            "V": [0]*17
        }

    def step(self):
        """Advances the model by one step"""
        self.steps += 1
        self.schedule.step()
        self.data_collector_total.collect(self)
        self.data_collector_age.collect(self)

    def coin_toss(self, ptrue):
        """Generates a pseudo-random choice"""
        if ptrue == 0:
            return False
        return random.uniform(0.0, 1.0) <= ptrue
