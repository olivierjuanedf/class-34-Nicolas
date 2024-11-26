import sys
from dataclasses import dataclass
from datetime import datetime, timedelta

from long_term_uc.common.constants_datatypes import DatatypesNames
from long_term_uc.common.constants_temporal import DATE_FORMAT_IN_JSON, MAX_DATE_IN_DATA, N_DAYS_DATA_ANALYSIS_DEFAULT
from long_term_uc.common.error_msgs import print_out_msg
from long_term_uc.utils.type_checker import apply_params_type_check


@dataclass
class AnalysisTypes: 
    calc: str = "calc"
    plot: str = "plot"
    plot_duration_curve: str = "plot_duration_curve"
    plot_rolling_horizon_avg: str = "plot_rolling_horizon_avg"


ANALYSIS_TYPES = AnalysisTypes()
AVAILABLE_ANALYSIS_TYPES = list(ANALYSIS_TYPES.__dict__.values())
AVAILABLE_DATA_TYPES = list(DatatypesNames.__annotations__.values())
DATA_SUBTYPE_KEY = "data_subtype"  # TODO[Q2OJ]: cleaner way to set/get it?
ORDERED_DATA_ANALYSIS_ATTRS = ["analysis_type", "data_type", "data_subtype", "country", 
                               "year", "climatic_year"]  # TODO[Q2OJ]: cleaner way to set/get it? (with data_subtype in 3rd pos)
RAW_TYPES_FOR_CHECK = {"analysis_type": "str", "data_type": "str", "data_subtype": "str", 
                       "country": "str", "year": "int", "climatic_year": "int"}


@dataclass
class DataAnalysis:
    analysis_type: str
    data_type: str
    country: str
    year: int
    climatic_year: int
    data_subtype: str = None
    period_start: datetime = None
    period_end: datetime = None

    def __repr__(self):
        repr_str = "ERAA data analysis with params:"
        repr_str += f"\n- of type {self.analysis_type}"
        if self.data_subtype is not None:
            data_type_suffix = f", and sub-datatype {self.data_subtype}"
        else:
            data_type_suffix = ""
        repr_str += f"\n- for data type: {self.data_type}{data_type_suffix}"
        repr_str += f"\n- country: {self.country}"
        repr_str += f"\n- year: {self.year}"
        repr_str += f"\n- climatic year: {self.climatic_year}"
        return repr_str

    def check_types(self):
        """
        Check coherence of types
        """
        dict_for_check = self.__dict__
        if self.data_subtype is None:
            del dict_for_check[DATA_SUBTYPE_KEY]
        apply_params_type_check(dict_for_check, types_for_check=RAW_TYPES_FOR_CHECK, 
                                param_name="Data analysis params - to set the calc./plot to be done")
    
    def process(self):
        # default is full year
        if self.period_start is None:
            self.period_start = datetime(year=1900, month=1, day=1)
            self.period_end = datetime(year=1900, month=12, day=1)
            if self.period_end is not None:
                print_out_msg(msg_level="warning", 
                              msg=f"End of period {self.period_end} cannot be used as start not defined")
        else:
            self.period_start = datetime.strptime(self.period_start, DATE_FORMAT_IN_JSON) 
            if self.period_end is None:       
                self.uc_period_end = min(MAX_DATE_IN_DATA, self.period_start + timedelta(days=N_DAYS_DATA_ANALYSIS_DEFAULT))
            else:
                self.period_end = datetime.strptime(self.period_end, DATE_FORMAT_IN_JSON)
                if self.period_end <= self.period_start:
                    print_out_msg(msg_level="error", 
                                  msg=f"{self.period_end.strftime(DATE_FORMAT_IN_JSON)} before {self.period_start.strftime(DATE_FORMAT_IN_JSON)} -> STOP")
                    sys.exit(1)

    def get_full_datatype(self) -> tuple:
        if self.data_subtype is None:
            return (self.data_type,)
        else:
            return (self.data_type, self.data_subtype)
