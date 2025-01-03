from abc import ABC, abstractmethod
import pandas as pd
from enum import Enum
from typing import Dict, List


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
    def collect_data(self, geography_type: GEOGRAPHY) -> Dict[str, pd.DataFrame]:
        pass

    @classmethod
    def create(cls, geography_type: GEOGRAPHY):
        """Factory method to create and initialize a DataSet instance."""
        instance = cls()
        instance.data_tables = instance.collect_data(geography_type)
        instance.variable_list = list(instance.data_tables.keys())
        return instance


class PopulationData(DataSet):

    def collect_data(self, geography_type: GEOGRAPHY) -> Dict[str, pd.DataFrame]:
        df_dict = {}
        # TODO: Collect data here
        return df_dict
