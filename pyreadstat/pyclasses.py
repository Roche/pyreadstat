# #############################################################################
# Copyright 2018 Hoffmann-La Roche
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# #############################################################################

# Typing

from typing import TYPE_CHECKING, Literal, TypedDict

if TYPE_CHECKING:
    from datetime import datetime


class _MissingRange(TypedDict):
    lo: float
    hi: float


class MRSet(TypedDict):
    """A dictionary to hold the definition of a multiple-response (MR) set."""

    type: Literal["D", "C"]
    is_dichotomy: bool
    counted_value: int
    label: str
    variable_list: list[str]


# Classes


class metadata_container:
    """
    This class holds metadata we want to give back to python
    """

    def __init__(self) -> None:
        self.column_names: list[str] = list()
        self.column_labels: list[str] = list()
        self.column_names_to_labels: dict[str, str] = dict()
        self.file_encoding: str = None  # type: ignore[assignment]
        self.number_columns: int = None  # type: ignore[assignment]
        self.number_rows: int = None  # type: ignore[assignment]
        self.variable_value_labels: dict[str, dict[float | int, str]] = dict()
        self.value_labels: dict[str, dict[float | int, str]] = dict()
        self.variable_to_label: dict[str, str] = dict()
        self.notes: list[str] = list()
        self.original_variable_types: dict[str, str] = dict()
        self.readstat_variable_types: dict[str, str] = dict()
        self.table_name: str = None  # type: ignore[assignment]
        self.missing_ranges: dict[str, list[int | float | str | _MissingRange]] = dict()
        self.missing_user_values: dict[str, list[int | float | str | _MissingRange]] = (
            dict()
        )
        self.variable_storage_width: dict[str, int] = dict()
        self.variable_display_width: dict[str, int] = dict()
        self.variable_alignment: dict[str, str] = dict()
        self.variable_measure: dict[
            str, Literal["nominal", "ordinal", "scale", "unknown"]
        ] = dict()
        self.creation_time: "datetime" = None  # type: ignore[assignment]
        self.modification_time: "datetime" = None  # type: ignore[assignment]
        self.mr_sets: dict[str, MRSet] = dict()
