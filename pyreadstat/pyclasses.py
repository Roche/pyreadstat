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

class metadata_container:
    """
    This class holds metadata we want to give back to python
    """
    def __init__(self):
        self.column_names = list()
        self.column_labels = list()
        self.column_names_to_labels = dict()
        self.file_encoding = None
        self.number_columns = None
        self.number_rows = None
        self.variable_value_labels = dict()
        self.value_labels = dict()
        self.variable_to_label = dict()
        self.notes = list()
        self.original_variable_types = dict()
        self.readstat_variable_types = dict()
        self.table_name = None
        self.missing_ranges = dict()
        self.missing_user_values = dict()
        self.variable_storage_width = dict()
        self.variable_display_width = dict()
        self.variable_alignment = dict()
        self.variable_measure = dict()
        self.creation_time = None
        self.modification_time = None
        self.mr_sets = dict()

