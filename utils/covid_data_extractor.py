import pandas as pd
import copy


class DOHCovid19DataExtractor:

    def __init__(self, filename):
        # Opens the COVID19 Data file as a Pandas DataFrame
        self.data = pd.read_csv(filename, index_col=0)
        self.filename = filename
        self.data['DateResultRelease'] = pd.to_datetime(
            self.data['DateResultRelease'])
        self.data['DateSpecimen'] = pd.to_datetime(
            self.data['DateResultRelease'])
        self.data['DateRecover'] = pd.to_datetime(self.data['DateRecover'])
        self.data['DateDied'] = pd.to_datetime(self.data['DateDied'])
        self.previous_data = []

    def generate_age_groups(self, size, groups):
        def age_range(x): return (x * size, (x + 1) * size - 1)
        return [age_range(i) for i in range(groups)]

    def count_cases(self, column, data_filter, age_stratified=True, use_data_filter=True):
        # Initializes the return variable: count
        # I = infectious, R = recovered, D = died
        count = {"I": [], "R": [], "D": []}

        # Filters the COVID19 data with the `column` column and data_filter
        if use_data_filter:
            data = self.data[self.data[column] == data_filter]
        # data = self.data

        # Generates the age groups; size = 10
        age_groups = self.generate_age_groups(5, 16)
        age_groups.append((80, 120))  # Special case: 80 and above

        for min_age, max_age in age_groups:
            # Filters the data with the Age column
            # Age of case must be within the min and max age
            age_group_data = data[data["Age"].between(
                min_age, max_age, inclusive='both')]

            # Counts the number of recovered, dead, and active
            recovered = len(
                age_group_data[age_group_data["HealthStatus"] == "RECOVERED"].index)
            dead = len(
                age_group_data[age_group_data["HealthStatus"] == "DIED"].index)
            active = len(age_group_data.index) - recovered - dead

            # Saves the counts to the return variable
            count["I"].append(active)
            count["R"].append(recovered)
            count["D"].append(dead)

        # Gets the sum of the age_stratified values when the age_stratified parameter is False
        if not age_stratified:
            for key in count:
                count[key] = sum(count[key])

        return count

    def count_cases_province(self, province):
        return self.count_cases("ProvRes", province.upper())

    def count_cases_city(self, city):
        return self.count_cases("CityMunRes", city.upper())

    def count_cases_region(self, region):
        return self.count_cases("RegionRes", region)

    def get_distribution(self, arr):
        arr_sum = sum(arr)
        return [i / arr_sum for i in arr]

    def cut_data(self, start, end, column):
        start_date = pd.Timestamp(start["y"], start["m"], start["d"])
        end_date = pd.Timestamp(end["y"], end["m"], end["d"])
        self.previous_data = copy.deepcopy(self.data)
        self.data = self.data[self.data[column] >= start_date]
        self.data = self.data[self.data[column] <= end_date]

    def undo_cutting(self):
        self.data = copy.deepcopy(self.previous_data)
