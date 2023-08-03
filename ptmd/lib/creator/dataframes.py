""" Module to created spreadsheets from the HarvesterInput, style and save them to disk.

@author: D. Batista (Terazus)
"""
from typing import Any

from pandas import DataFrame, Series, concat as pd_concat

from ptmd.const import (
    GENERAL_SHEET_COLUMNS, SAMPLE_SHEET_COLUMNS,
    DOSE_MAPPING, TIME_POINT_MAPPING,
    EMPTY_FIELDS_VALUES,
    BLANK_CODE
)


def build_general_dataframe(harvester: Any) -> DataFrame:
    """ Builds a DataFrame with the general information of the harvester.

    :param harvester: The harvester to build the DataFrame from.
    :return: A DataFrame with the general information of the harvester.
    """
    dataframe = DataFrame(columns=GENERAL_SHEET_COLUMNS)
    series = Series([
        harvester.partner,
        harvester.organism,
        harvester.exposure_batch,
        harvester.replicates4control,
        harvester.replicates4exposure,
        harvester.replicates_blank,
        harvester.start_date.strftime('%Y-%m-%d'),
        harvester.end_date.strftime('%Y-%m-%d'),
        harvester.timepoints,
        harvester.vehicle,
    ], index=dataframe.columns)
    return series.to_frame().T


def build_sample_dataframe(harvester: Any, chemicals_mapping: dict[str, str], organism_code: str) -> DataFrame:
    """ Builds a DataFrame with the sample information of the harvester.

    :param harvester: The harvester to build the DataFrame from.
    :param chemicals_mapping: A dictionary mapping chemicals names to ptox codes.
    :param organism_code: The organism code to use.
    :return: A DataFrame
    """
    dataframe: DataFrame = DataFrame(columns=SAMPLE_SHEET_COLUMNS)
    timepoint: str
    hash_id: str
    series: Series
    timepoint_value: int
    timepoint_key: str
    number_of_timepoints: int = len(harvester.timepoints)

    # build the section containing the exposition conditions
    for exposure_condition in harvester.exposure_conditions:
        dose_code: str = DOSE_MAPPING[exposure_condition['dose']]
        for chemical in exposure_condition['chemicals']:
            chemical_code: str = chemicals_mapping[chemical]
            for tp in range(1, number_of_timepoints + 1):
                timepoint_key = f'TP{tp}'
                timepoint = TIME_POINT_MAPPING[timepoint_key] if timepoint_key in TIME_POINT_MAPPING else 'X'
                timepoint_value = harvester.timepoints[tp - 1]
                for replicate in range(1, harvester.replicates4exposure + 1):
                    hash_id = '%s%s%s%s%s%s' % (organism_code, harvester.exposure_batch, chemical_code,
                                                dose_code, timepoint, replicate)
                    series = Series([
                        hash_id,
                        f'PTX{chemical_code}',
                        *EMPTY_FIELDS_VALUES,
                        replicate,
                        chemical,
                        exposure_condition['dose'],
                        'TP%s' % tp,
                        timepoint_value
                    ], index=dataframe.columns)
                    dataframe = pd_concat([dataframe, series.to_frame().T], ignore_index=False, sort=False, copy=False)

    # build the section containing the control conditions
    for tp in range(1, number_of_timepoints + 1):
        timepoint_key = f'TP{tp}'
        timepoint = TIME_POINT_MAPPING[timepoint_key] if timepoint_key in TIME_POINT_MAPPING else 'X'
        timepoint_value = harvester.timepoints[tp - 1]
        control_code = '999' if harvester.vehicle == 'DMSO' else '997'
        for replicate in range(1, harvester.replicates4control + 1):
            hash_id = '%s%s%sZ%s%s' % (organism_code, harvester.exposure_batch, control_code, timepoint, replicate)
            series = Series([hash_id, f'PTX{control_code}', *EMPTY_FIELDS_VALUES,
                             replicate, "CONTROL (%s)" % harvester.vehicle, 0, 'TP%s' % tp, timepoint_value],
                            index=dataframe.columns)
            dataframe = pd_concat([dataframe, series.to_frame().T], ignore_index=False, sort=False, copy=False)

    # add the blanks and return the dataframe
    return add_blanks_to_sample_dataframe(dataframe,
                                          harvester.replicates_blank,
                                          organism_code,
                                          harvester.exposure_batch)


def add_blanks_to_sample_dataframe(
        sample_df: DataFrame,
        replicate_blank: int,
        organism_code: str,
        exposure_batch: str
) -> DataFrame:
    """ Add the blanks to the sample dataframe.

    :param sample_df: The sample dataframe.
    :param replicate_blank: The number of blanks to add.
    :param organism_code: The organism code to use.
    :param exposure_batch: The exposure batch to use.
    :return: The sample dataframe with the blanks.
    """
    for blank in range(1, replicate_blank + 1):
        hash_id = '%s%s%sZS%s' % (organism_code, exposure_batch, BLANK_CODE, blank)
        series = Series([hash_id, f'PTX{BLANK_CODE}', *EMPTY_FIELDS_VALUES, blank, 'EXTRACTION BLANK', "0", 'TP0', 0],
                        index=sample_df.columns)
        sample_df = pd_concat([sample_df, series.to_frame().T], ignore_index=False, sort=False, copy=False)
    return sample_df
