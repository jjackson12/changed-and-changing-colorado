from abc import ABC, abstractmethod
import pandas as pd
from enum import Enum
from typing import Dict, List
from census import Census


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

    @classmethod
    def create(cls, geography_type: GEOGRAPHY, **args):
        """Factory method to create and initialize a DataSet instance."""
        instance = cls()
        instance.data_tables = instance.collect_data(geography_type, args)
        instance.variable_list = list(instance.data_tables.keys())
        return instance


class PopulationData(DataSet):
    """Collect Population data by race and ethnicity from the Census ACS

    Args:
        geography_type (GEOGRAPHY): Geographic unit of aggregation
        args: Dict of additional arguments passed in init for collect_data. For this dataset, this requires year and ACS dataset name.
    """

    def collect_data(self, geography_type: GEOGRAPHY, args) -> Dict[str, pd.DataFrame]:
        df_dict = {}

        # TODO
        API_KEY = "YOUR_CENSUS_API_KEY"
        c = Census(API_KEY)

        # TODO
        acs_year = args["year"]
        acs_dataset = args["dataset"]

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

        # Query the Census API
        # FIXME: This isn't actually referencing "acs_dataset" variable
        results = c.acs5.state_zipcode(
            ["NAME"] + list(variables.keys()), state_fips, "*"
        )

        df = pd.DataFrame(results)

        rename_map = {var: desc for var, desc in variables.items()}
        rename_map.update({"zip code tabulation area": "ZIP Code", "NAME": "Area Name"})
        df = df.rename(columns=rename_map)

        # Convert numeric columns to proper types
        for col in variables.values():
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        return {"Population by Race": df}
