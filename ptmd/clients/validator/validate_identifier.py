""" Validate the identifier of the current ExcelValidator

@author: D. Batista (Terazus)
"""
from typing import Any

from re import match

from ptmd.database import Organism, Chemical
from ptmd.const import ALLOWED_EXPOSURE_BATCH, DOSE_MAPPING, TIME_POINT_MAPPING
from .const import PTX_ID_LABEL, BATCH_LABEL, COMPOUND_LABEL, DOSE_LABEL, TIMEPOINT_LABEL


INV_DOSE_MAPPING: dict = {v: k for k, v in DOSE_MAPPING.items()}
INV_TIMEPOINT_MAPPING: dict = {v: k for k, v in TIME_POINT_MAPPING.items()}


def validate_identifier(excel_validator: Any, record_index: int) -> None:
    """ Validate the identifier of the current ExcelValidator.

    :param excel_validator: The ExcelValidator for which to run the identifier validation.
    :param record_index: The index of the record to validate.
    """
    validate_unique_identifier(excel_validator, record_index)
    if excel_validator.report['valid']:
        validate_species(excel_validator)
        validate_batch(excel_validator)
        validate_compound(excel_validator)
        validate_dose(excel_validator)
        validate_timepoints(excel_validator)
        validate_replicate(excel_validator)


def validate_unique_identifier(validator: Any, record_index: int) -> None:
    """ Validates the identifier.

    :param validator: The ExcelValidator for which to run the identifier validation.
    :param record_index: The index of the record to validate.
    """
    ptx_id: str = validator.current_record['data'][PTX_ID_LABEL]
    if ptx_id in validator.identifiers:
        validator.report['valid'] = False
        msg: str = (f"Record at line {record_index + 2} ({ptx_id}) "
                    f"is duplicated with record at line {validator.identifiers.index(ptx_id) + 3}")
        validator.add_error(validator.current_record['label'], msg, PTX_ID_LABEL)
    validator.identifiers.append(ptx_id)


def validate_species(validator: Any) -> None:
    """ Validates the species.

    :param validator: The ExcelValidator for which to run the identifier validation.
    """
    species: str = validator.current_record['data'][PTX_ID_LABEL][0]
    try:
        organism_name: str = validator.general_info["biosystem_name"]
        organism: Organism = validator.session.query(Organism).filter(
            Organism.ptox_biosystem_name == organism_name
        ).first()
        if not organism:
            validator.report['valid'] = False
            validator.add_error(validator.current_record['label'], "Organism not found in database.", "biosystem_name")
        elif species != organism.ptox_biosystem_code:
            validator.report['valid'] = False
            validator.add_error(
                validator.current_record['label'],
                "The identifier organism doesn't match the biosystem_name.",
                PTX_ID_LABEL
            )
    except Exception as e:
        validator.report['valid'] = False
        validator.add_error(validator.current_record['label'], f"Error {e}", "unknown")


def validate_batch(validator: Any) -> None:
    """ Validates the batch.

    :param validator: The ExcelValidator for which to run the identifier validation.
    """
    batch: str = validator.current_record['data'][PTX_ID_LABEL][1:3]
    batch_reference: str = validator.general_info[BATCH_LABEL]

    # validate the batch in the general information sheet
    if not match(ALLOWED_EXPOSURE_BATCH, batch_reference):
        validator.report['valid'] = False
        validator.add_error(validator.current_record['label'],
                            f"The batch '{batch_reference}' is not valid.",
                            BATCH_LABEL)

    # validate the batch in the exposure information sheet
    if not match(ALLOWED_EXPOSURE_BATCH, batch):
        validator.report['valid'] = False
        validator.add_error(validator.current_record['label'],
                            f"The identifier doesn't contain a valid batch '{batch}'.",
                            PTX_ID_LABEL)

    # compare the batch in the general information sheet and the exposure information sheet
    elif batch != batch_reference:
        validator.report['valid'] = False
        validator.add_error(validator.current_record['label'],
                            f"The identifier batch doesn't match the batch '{batch_reference}'.",
                            PTX_ID_LABEL)


def validate_compound(validator: Any) -> None:
    """ Validates the compound.

    :param validator: The ExcelValidator for which to run the identifier validation.
    """
    compound_code: int = int(validator.current_record['data'][PTX_ID_LABEL][3:6])
    compound_reference: str = validator.current_record['data'][COMPOUND_LABEL]
    if compound_code < 1 or compound_code > 999:
        validator.report['valid'] = False
        validator.add_error(validator.current_record['label'],
                            f"The identifier doesn't contain a valid compound code '{compound_code}'.",
                            PTX_ID_LABEL)
    elif compound_reference:
        if 'CONTROL' not in compound_reference and 'EXTRACTION BLANK' not in compound_reference:
            validate_replicates_compound(validator, compound_reference, compound_code)
        elif 'CONTROL' in compound_reference:
            validate_controls_compound(validator, compound_reference, compound_code)
        elif 'EXTRACTION BLANK' in compound_reference and compound_code != '998':
            validator.report['valid'] = False
            validator.add_error(validator.current_record['label'],
                                f"The identifier compound should be 998 but got {compound_code}.",
                                PTX_ID_LABEL)


def validate_replicates_compound(validator: Any, compound_name: str, code: int) -> None:
    """ Validates the replicates compounds.

    :param validator: The ExcelValidator for which to run the identifier validation.
    :param compound_name: The reference compound name to check
    :param code: The compound code to check
    """
    try:
        compound: Chemical = validator.session.query(Chemical).filter(Chemical.common_name == compound_name).first()
        if not compound:
            validator.report['valid'] = False
            validator.add_error(validator.current_record['label'],
                                f"The identifier doesn't contain a valid compound code '{code}'.",
                                COMPOUND_LABEL)
        elif compound.ptx_code != code:
            validator.report['valid'] = False
            msg: str = "The identifier %s compound doesn't match the compound %s (%s)" % (
                code, compound_name, compound.ptx_code
            )
            validator.add_error(validator.current_record['label'], msg, PTX_ID_LABEL)
    except Exception as e:
        validator.report['valid'] = False
        validator.add_error(validator.current_record['label'], f"Error {e}", 'unknown')


def validate_controls_compound(validator: Any, compound_name: str, code: int) -> None:
    """ Validates the controls compound.

    :param validator: The ExcelValidator for which to run the identifier validation.
    :param compound_name: The reference compound name to check
    :param code: The compound code to check
    """
    if 'DMSO' in compound_name and compound_name != 999:
        validator.report['valid'] = False
        validator.add_error(validator.current_record['label'],
                            f"The identifier compound should be 999 but got {code}.",
                            PTX_ID_LABEL)
    elif 'WATER' in compound_name and compound_name != 997:
        validator.report['valid'] = False
        validator.add_error(validator.current_record['label'],
                            f"The identifier compound should be 997 but got {code}.",
                            PTX_ID_LABEL)


def validate_dose(validator: Any) -> None:
    """ Validates the dose.

    :param validator: The ExcelValidator for which to run the dose validation.
    """
    dose: str = validator.current_record['data'][PTX_ID_LABEL][6]
    dose_reference: str = validator.current_record['data'][DOSE_LABEL]
    if dose and dose_reference:
        try:
            dose_map: str = INV_DOSE_MAPPING[dose]
            if dose_map != dose_reference:
                validator.report['valid'] = False
                validator.add_error(validator.current_record['label'],
                                    f"The identifier dose maps to {dose_map} but should maps to '{dose_reference}'.",
                                    PTX_ID_LABEL)
        except KeyError:
            validator.report['valid'] = False
            validator.add_error(validator.current_record['label'],
                                f"The identifier contain a invalid dose '{dose}'.",
                                PTX_ID_LABEL)


def validate_timepoints(validator: Any) -> None:
    """ Validates the timepoints.

    :param validator: The ExcelValidator for which to run the timepoints validation.
    """
    timepoints: str = validator.current_record['data'][PTX_ID_LABEL][7]
    timepoints_reference: str = validator.current_record['data'][TIMEPOINT_LABEL]
    if timepoints and timepoints_reference:
        try:
            timepoints_map: str = INV_TIMEPOINT_MAPPING[timepoints]
            if timepoints_map != timepoints_reference:
                validator.report['valid'] = False
                message: str = (f"The identifier timepoints maps to {timepoints_map} "
                                f"but should maps to '{timepoints_reference}'.")
                validator.add_error(validator.current_record['label'], message, PTX_ID_LABEL)
        except KeyError:
            validator.report['valid'] = False
            validator.add_error(validator.current_record['label'],
                                f"The identifier contains an invalid timepoint '{timepoints}'.",
                                PTX_ID_LABEL)


def validate_replicate(validator: Any) -> None:
    """ Validates the replicates.

    :param validator: The ExcelValidator for which to run the validation of the identifier replicate.
    """
    replicate: int = int(validator.current_record['data'][PTX_ID_LABEL][-1])
    replicate_reference: int = validator.current_record['data']['replicate']
    if replicate != replicate_reference:
        validator.report['valid'] = False
        message: str = f"The identifier replicate {replicate} doesn't match the replicate {replicate_reference}."
        validator.add_error(validator.current_record['label'], message, PTX_ID_LABEL)
