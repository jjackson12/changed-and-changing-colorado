from abc import ABC, abstractmethod
import pandas as pd
from enum import Enum
from typing import Dict, List
from census import Census
import os


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

    def __init__(self, geography_type: GEOGRAPHY, **args):
        self.data_tables = self.collect_data(geography_type, args)
        self.variable_list = list(self.data_tables.keys())


class PopulationData(DataSet):
    """Collect Population data by race and ethnicity from the Census ACS

    Args:
        geography_type (GEOGRAPHY): Geographic unit of aggregation
        args: Dict of additional arguments passed in init for collect_data. For this dataset, this requires year, ACS dataset name, and census api key.
    """

    def collect_data(self, geography_type: GEOGRAPHY, args) -> Dict[str, pd.DataFrame]:

        df_dict = {}

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

        if not dataset:
            raise Exception(
                f"invalid argument for dataset {args['dataset']}. Must select from these options: {', '.join(dataset_mappings.keys())}"
            )

        # TODO
        variables = {
            "B01003_001E": "Total Population",
            "B02001_002E": "White Population",
            "B02001_003E": "Black Population",
            "B02001_005E": "Asian Population",
            "B19013_001E": "Median Household Income",
        }

        # Colorado FIPS code
        state_fips = "08"

        if geography_type == GEOGRAPHY.ZIP5:
            # TODO: Use Geography var
            results = dataset.state_zipcode(
                ["NAME"] + list(variables.keys()), state_fips, "*", year=acs_year
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

        rename_map = {var: desc for var, desc in variables.items()}
        rename_map.update({"zip code tabulation area": "ZIP Code", "NAME": "Area Name"})
        df = df.rename(columns=rename_map)

        # Convert numeric columns to proper types
        for col in variables.values():
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        return {"Population Demos": df}


census_api_key = os.environ["CENSUS_API_KEY"]
census_data_args = {"API_KEY": census_api_key, "year": 2022, "dataset": "acs5"}
pop_data = PopulationData(GEOGRAPHY.ZIP5, **census_data_args)
pop_data_tbls = pop_data.data_tables
print(pop_data_tbls)
