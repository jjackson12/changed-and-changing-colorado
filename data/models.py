from abc import ABC, abstractmethod
import pandas as pd
from enum import Enum


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
    def collect_data(geography_type: GEOGRAPHY) -> pd.DataFrame:
        pass
