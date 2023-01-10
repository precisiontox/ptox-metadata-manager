""" Module to created spreadsheets from the HarvesterInput, style and save them to disk.

@author: D. Batista (Terazus)
"""
from pandas import DataFrame, Series, concat as pd_concat

from ptmd.const import GENERAL_SHEET_COLUMNS, SAMPLE_SHEET_COLUMNS, DOSE_MAPPING, TIME_POINT_MAPPING
from .interfaces import InputsToDataframes


def build_general_dataframe(
        harvester: InputsToDataframes
) -> DataFrame:
    """ Builds a DataFrame with the general information of the harvester.

    :param harvester: The harvester to build the DataFrame from.
    :return: A DataFrame with the general information of the harvester.
    """
    dataframe = DataFrame(columns=GENERAL_SHEET_COLUMNS)
    series = Series([
        harvester.partner,
        harvester.organism,
        harvester.exposure_batch,
        harvester.replicate4control,
        harvester.replicate4exposure,
        harvester.replicate_blank,
        harvester.start_date.strftime('%Y-%m-%d'),
        harvester.end_date.strftime('%Y-%m-%d'),
        harvester.timepoints,
        harvester.vehicle,
    ], index=dataframe.columns)
    return series.to_frame().T


def build_sample_dataframe(
        harvester: InputsToDataframes,
        chemicals_mapping: dict[str, str],
        organism_code: str
) -> DataFrame:
    """ Builds a DataFrame with the sample information of the harvester.

    :param harvester: The harvester to build the DataFrame from.
    :param chemicals_mapping: A dictionary mapping chemicals names to ptox codes.
    :param organism_code: The organism code to use.
    :return: A DataFrame
    """
    dataframe: DataFrame = DataFrame(columns=SAMPLE_SHEET_COLUMNS)
    for exposure_condition in harvester.exposure_conditions:
        dose_code: str = DOSE_MAPPING[exposure_condition.dose]
        for chemical in exposure_condition.chemicals_name:
            chemical_code: str = chemicals_mapping[chemical]
            for tp in range(1, harvester.timepoints + 1):
                timepoint: str = f'TP{tp}'
                timepoint_code: str = TIME_POINT_MAPPING[timepoint]
                for replicate in range(1, harvester.replicate4exposure + 1):
                    hash_id: str = '%s%s%s%s%s%s' % (organism_code, harvester.exposure_batch, chemical_code,
                                                     dose_code, timepoint_code, replicate)
                    series: Series = Series([
                        '', '', '', '', '', '', '', '',
                        replicate, chemical, exposure_condition.dose, 'TP%s' % tp, hash_id
                    ], index=dataframe.columns)
                    dataframe = pd_concat([dataframe, series.to_frame().T], ignore_index=False, sort=False, copy=False)
    for replicate in range(1, harvester.replicate4control + 1):
        for tp in range(1, harvester.timepoints + 1):
            timepoint: str = f'TP{tp}'
            timepoint_code: str = TIME_POINT_MAPPING[timepoint]
            control_code = '999' if harvester.vehicle == 'DMSO' else '997'
            hash_id: str = '%s%s%s%sZ%s' % (organism_code, harvester.exposure_batch, control_code,
                                            timepoint_code, replicate)
            series: Series = Series([
                '', '', '', '', '', '', '', '',
                replicate, "CONTROL (%s)" % harvester.vehicle, 0, 'TP%s' % tp, hash_id
            ], index=dataframe.columns)
            dataframe = pd_concat([dataframe, series.to_frame().T], ignore_index=False, sort=False, copy=False)
    return add_blanks_to_sample_dataframe(dataframe, harvester.replicate_blank, organism_code, harvester.exposure_batch)


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
        hash_id = '%s%s998ZS%s' % (organism_code, exposure_batch, blank)
        series = Series(['', '', '', '', '', '', '', '', blank, 'EXTRACTION BLANK', "0", 'TP0', hash_id],
                        index=sample_df.columns)
        sample_df = pd_concat([sample_df, series.to_frame().T], ignore_index=False, sort=False, copy=False)
    return sample_df
