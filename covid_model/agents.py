from mesa import Agent
import random


class PersonAgent(Agent):

    def __init__(self,
                 unique_id,
                 model,
                 state,
                 age,
                 age_group,
                 wearing_mask,
                 social_distancing,
                 days_incubating,
                 days_infected
                 ):
        super().__init__(unique_id, model)
        self.state = state
        self.age = age
        self.age_group = age_group
        self.wearing_mask = wearing_mask
        self.social_distancing = social_distancing
        self.days_incubating = days_incubating
        self.days_infected = days_infected

    def step(self):
        self.status()
        self.interact()
        self.move()

    def move(self):
        if self.state not in ["R", "D"]:  # and self.not_quarantined():
            possible_steps = self.model.grid.get_neighborhood(
                self.pos,
                moore=True,
                include_center=False,
                radius=self.model.agent_movement_range)
            new_position = self.random.choice(possible_steps)
            self.model.grid.move_agent(self, new_position)

    def status(self):
        if self.state == "E":
            self.days_incubating += 1
            if self.days_incubating > self.random.normalvariate(self.model.average_incubation_period, 2):
                self.state_transition(self.state, "I")

        elif self.state == "I":
            if self.days_infected < self.random.normalvariate(self.model.average_infectious_period, 3):
                self.days_infected += 1
            else:
                if self.coin_toss(self.model.death_rate[self.age_group]):
                    self.state_transition(self.state, "D")
                    self.model.grid.remove_agent(self)
                    self.model.schedule.remove(self)
                    del self
                elif self.coin_toss(self.model.recovery_rate[self.age_group]):
                    self.state_transition(self.state, "R")
                    self.model.grid.remove_agent(self)
                    self.model.schedule.remove(self)
                    del self

    def interact(self):
        if self.state == "I":
            cellmates = self.model.grid.get_cell_list_contents([self.pos])
            if len(cellmates) > 1:
                for cellmate in cellmates:
                    if cellmate.state == "S":
                        # self.coin_toss(cellmate.model.infection_probability[cellmate.age_group]):
                        if self.in_contact_with(cellmate) and not cellmate.protected_by_measures() and self.coin_toss(cellmate.model.infection_rate[cellmate.age_group]):
                            cellmate.state_transition(cellmate.state, "E")

    def in_contact_with(self, cellmate):
        return self.coin_toss(self.model.contact_matrix[self.age_group][cellmate.age_group])

    def state_transition(self, current_state, next_state):
        self.model.summary[current_state][self.age_group] -= 1
        self.model.summary[next_state][self.age_group] += 1

        if current_state == "S":
            self.model.total[current_state][self.age_group] -= 1

        self.model.total[next_state][self.age_group] += 1
        self.model.total_added[next_state][self.age_group] += 1
        self.state = next_state

    def protected_by_measures(self):
        return self.wearing_mask or self.social_distancing

    # def not_quarantined(self):
    #    return self.model.min_age_restriction <= self.age <= self.model.max_age_restriction

    def coin_toss(self, ptrue):
        """Generates a pseudo-random choice"""
        if ptrue == 0:
            return False
        return random.uniform(0.0, 1.0) <= ptrue
