from datetime import datetime
from os import PathLike
from typing import TYPE_CHECKING, Any, IO, Literal, Optional, overload

import numpy as np
import numpy.typing as npt

if TYPE_CHECKING:
    import pandas as pd
    import polars as pl


class Metadata:
    column_names: list[str]
    column_labels: list[str | None]
    column_names_to_labels: dict[str, str | None]
    file_encoding: str | None
    file_label: str | None
    number_columns: int | None
    number_rows: int | None
    variable_value_labels: dict[str, dict[Any, str]]
    value_labels: dict[str, dict[Any, str]]
    variable_to_label: dict[str, str]
    notes: list[str]
    original_variable_types: dict[str, str]
    readstat_variable_types: dict[str, str]
    table_name: str | None
    missing_ranges: dict[str, Any]
    missing_user_values: dict[str, Any]
    variable_storage_width: dict[str, int]
    variable_display_width: dict[str, int]
    variable_alignment: dict[str, str]
    variable_measure: dict[str, str]
    creation_time: datetime | None
    modification_time: datetime | None
    mr_sets: dict[str, Any]


metadata_container = Metadata
FilePathOrBuffer = str | bytes | PathLike[str] | PathLike[bytes] | IO[str] | IO[bytes]
DictOutput = dict[str, npt.NDArray[np.generic]]


@overload
def read_sav(
    filename_path: FilePathOrBuffer,
    metadataonly: bool = ...,
    dates_as_pandas_datetime: bool = ...,
    apply_value_formats: bool = ...,
    formats_as_category: bool = ...,
    formats_as_ordered_category: bool = ...,
    encoding: Optional[str] = ...,
    usecols: Optional[list[str]] = ...,
    user_missing: bool = ...,
    disable_datetime_conversion: bool = ...,
    row_limit: int = ...,
    row_offset: int = ...,
    output_format: Literal["pandas", None] = ...,
    extra_datetime_formats: Optional[list[str]] = ...,
    extra_date_formats: Optional[list[str]] = ...,
    extra_time_formats: Optional[list[str]] = ...,
) -> tuple["pd.DataFrame", Metadata]: ...


@overload
def read_sav(
    filename_path: FilePathOrBuffer,
    metadataonly: bool = ...,
    dates_as_pandas_datetime: bool = ...,
    apply_value_formats: bool = ...,
    formats_as_category: bool = ...,
    formats_as_ordered_category: bool = ...,
    encoding: Optional[str] = ...,
    usecols: Optional[list[str]] = ...,
    user_missing: bool = ...,
    disable_datetime_conversion: bool = ...,
    row_limit: int = ...,
    row_offset: int = ...,
    output_format: Literal["dict"] = ...,
    extra_datetime_formats: Optional[list[str]] = ...,
    extra_date_formats: Optional[list[str]] = ...,
    extra_time_formats: Optional[list[str]] = ...,
) -> tuple[DictOutput, Metadata]: ...


@overload
def read_sav(
    filename_path: FilePathOrBuffer,
    metadataonly: bool = ...,
    dates_as_pandas_datetime: bool = ...,
    apply_value_formats: bool = ...,
    formats_as_category: bool = ...,
    formats_as_ordered_category: bool = ...,
    encoding: Optional[str] = ...,
    usecols: Optional[list[str]] = ...,
    user_missing: bool = ...,
    disable_datetime_conversion: bool = ...,
    row_limit: int = ...,
    row_offset: int = ...,
    output_format: Literal["polars"] = ...,
    extra_datetime_formats: Optional[list[str]] = ...,
    extra_date_formats: Optional[list[str]] = ...,
    extra_time_formats: Optional[list[str]] = ...,
) -> tuple["pl.DataFrame", Metadata]: ...


read_sas7bdat: Any
read_xport: Any
read_dta: Any
read_por: Any
read_sas7bcat: Any
write_sav: Any
write_dta: Any
write_xport: Any
write_por: Any
read_file_in_chunks: Any
read_file_multiprocessing: Any
set_value_labels: Any
set_catalog_to_sas: Any
ReadstatError: type[Exception]

__version__: str
