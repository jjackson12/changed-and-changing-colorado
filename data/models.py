from abc import ABC, abstractmethod
import pandas as pd
from enum import Enum
from typing import Dict, List
from census import Census
import os
import requests


class GEOGRAPHY(Enum):
    """Enum Class defining options for Geography types used in this analysis"""

    ZIP5 = "Zip5"
    ZIP9 = "Zip9"
    COUNTY = "County"
    DENVER_METRO = "Denver Metro"
    STATE = "State"


class DataSet(ABC):
    """Abstract Class defining how datasets for this project will be structured."""

    @abstractmethod
    def collect_data(self, geography_type: GEOGRAPHY, args) -> Dict[str, pd.DataFrame]:
        pass

    def get_data(self):
        return self.data_tables

    def __init__(self, geography_type: GEOGRAPHY, **args):
        self.data_tables = self.collect_data(geography_type, args)
        self.variable_list = list(self.data_tables.keys())


class PopulationData(DataSet):
    """Collect Population data by race and ethnicity from the Census ACS

    Args:
        geography_type (GEOGRAPHY): Geographic unit of aggregation
        args: Dict of additional arguments passed in init for collect_data. For this dataset, this requires year, ACS dataset name, variables (if left blank, will use "*"), and census api key.
    """

    def collect_data(self, geography_type: GEOGRAPHY, args) -> Dict[str, pd.DataFrame]:

        API_KEY = args["API_KEY"]
        c = Census(API_KEY)

        acs_year = args["year"]

        dataset_mappings = {
            "acs5": c.acs5,
            "acs3": c.acs3,
            "acs1": c.acs1,
            "acs5dp": c.acs5dp,
            "acs3dp": c.acs3dp,
            "acs1dp": c.acs1dp,
            "acs5st": c.acs5st,
        }
        dataset = dataset_mappings.get(args["dataset"], None)

        variables = args["variables"]
        variable_name_mapping = {}
        if type(variables) == dict:
            variable_name_mapping = variables
            variables = list(variables.keys())

        if not dataset:
            raise Exception(
                f"invalid argument for dataset {args['dataset']}. Must select from these options: {', '.join(dataset_mappings.keys())}"
            )

        # Colorado FIPS code
        state_fips = "08"

        if geography_type == GEOGRAPHY.ZIP5:
            results = dataset.state_zipcode(
                ["NAME"] + variables, state_fips, "*", year=acs_year
            )
        else:
            if geography_type == GEOGRAPHY.STATE:
                results = dataset.state(
                    ["NAME"] + list(variables.keys()), state_fips, year=acs_year
                )
            else:
                raise Exception(
                    f"Geography type {geography_type} not implemented for Population Census Dataset"
                )
        df = pd.DataFrame(results)

        variable_name_mapping.update(
            {"zip code tabulation area": "ZIP Code", "NAME": "Area Name"}
        )
        df = df.rename(columns=variable_name_mapping)

        return {"Population Demos": df}


dataset = "acs/acs5/profile"
year = 2022
url = f"https://api.census.gov/data/{year}/{dataset}/variables.json"

response = requests.get(url)
variables = response.json()["variables"]

table_variables = {
    key: f'{key}_{val["label"]}'
    for key, val in variables.items()
    if "PR" not in key and "DP02_" in key
}

census_api_key = os.environ["CENSUS_API_KEY"]
census_data_args = {
    "API_KEY": census_api_key,
    "year": 2022,
    "dataset": "acs5dp",
    "variables": table_variables,
}
pop_data = PopulationData(GEOGRAPHY.ZIP5, **census_data_args)
pop_data_tbls = pop_data.get_data()
print(pop_data_tbls)
