# -*- coding: utf-8 -*-
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

from datetime import datetime
import unittest
import os
import sys

import pandas as pd
import numpy as np


class TestBasic(unittest.TestCase):
    """
    Test suite for pyreadstat.
    """

    def _prepare_data(self):

        self.script_folder = os.path.dirname(os.path.realpath(__file__))
        self.parent_folder = os.path.split(self.script_folder)[0]
        self.data_folder = os.path.join(self.parent_folder, "test_data")
        self.basic_data_folder = os.path.join(self.data_folder, "basic")
        self.catalog_data_folder = os.path.join(self.data_folder, "sas_catalog")
        self.international_data_folder = os.path.join(self.data_folder, "ínternátionál")
        self.missing_data_folder = os.path.join(self.data_folder, "missing_data")
        self.write_folder = os.path.join(self.data_folder, "write")
        if not os.path.isdir(self.write_folder):
            os.makedirs(self.write_folder)


        # basic
        pandas_csv = os.path.join(self.basic_data_folder, "sample.csv")
        df_pandas = pd.read_csv(pandas_csv)
        df_pandas["mydate"] = [datetime.strptime(x, '%Y-%m-%d').date() if type(x) == str else float('nan') for x in df_pandas["mydate"]]
        df_pandas["dtime"] = [datetime.strptime(x, '%Y-%m-%dT%H:%M:%S.000000') if type(x) == str else float('nan') for x in
                              df_pandas["dtime"]]
        df_pandas["mytime"] = [datetime.strptime(x, '%H:%M:%S.000000').time() if type(x) == str else float('nan') for x in
                               df_pandas["mytime"]]
        df_pandas["myord"] = df_pandas["myord"].astype(float)
        df_pandas["mylabl"] = df_pandas["mylabl"].astype(float)
        self.df_pandas = df_pandas
        # formatted
        mylabl_format = {1.0:"Male", 2.0:"Female"}
        myord_format = {1.0:"low", 2.0:"medium", 3.0:"high"}
        df_pandas_formatted = df_pandas.copy()
        df_pandas_formatted["mylabl"] = df_pandas_formatted["mylabl"].apply(lambda x: mylabl_format[x])
        df_pandas_formatted["myord"] = df_pandas_formatted["myord"].apply(lambda x: myord_format[x])
        df_pandas_formatted["mylabl"] = df_pandas_formatted["mylabl"].astype("category")
        df_pandas_formatted["myord"] = df_pandas_formatted["myord"].astype("category")
        self.df_pandas_formatted = df_pandas_formatted
        # skip some columns
        self.usecols = ['mynum', 'myord']
        cols_to_drop = list(set(df_pandas.columns.values.tolist()) - set(self.usecols))
        self.df_usecols = df_pandas.drop(cols_to_drop, axis=1)
        # sas formatted
        sas_formatted = os.path.join(self.catalog_data_folder, "sas_formatted.csv")
        df_sas = pd.read_csv(sas_formatted)
        df_sas["SEXA"] = df_sas["SEXA"].astype("category")
        df_sas["SEXB"] = df_sas["SEXB"].astype("category")
        self.df_sas_format = df_sas
        # dates
        sas_dates = os.path.join(self.basic_data_folder, "dates.csv")
        df_dates1 = pd.read_csv(sas_dates)
        df_dates1["date"] = pd.to_datetime(df_dates1["date"])
        df_dates1["dtime"] = pd.to_datetime(df_dates1["dtime"])
        df_dates1["time"] = pd.to_datetime(df_dates1["time"])
        df_dates1["time"] = df_dates1["time"].apply(lambda x: x.time())
        self.df_sas_dates_as_pandas = df_dates1

        df_dates2 = df_dates1.copy()
        df_dates2["date"] = df_dates2["date"].apply(lambda x: x.date())
        self.df_sas_dates = df_dates2

        # missing data
        pandas_missing_sav_csv = os.path.join(self.basic_data_folder, "sample_missing.csv")
        df_missing_sav = pd.read_csv(pandas_missing_sav_csv, na_values="#NULL!", keep_default_na=False)
        df_missing_sav["mydate"] = [datetime.strptime(x, '%Y-%m-%d').date() if type(x) == str else float('nan') for x in
                                    df_missing_sav["mydate"]]
        df_missing_sav["dtime"] = [datetime.strptime(x, '%Y-%m-%dT%H:%M:%S.000000') if type(x) == str else float('nan') for x
                              in df_missing_sav["dtime"]]
        df_missing_sav["mytime"] = [datetime.strptime(x, '%H:%M:%S.000000').time() if type(x) == str else float('nan') for x
                               in df_missing_sav["mytime"]]
        self.df_missing_sav = df_missing_sav

        pandas_missing_user_sav_csv = os.path.join(self.basic_data_folder, "sample_missing_user.csv")
        df_user_missing_sav = pd.read_csv(pandas_missing_user_sav_csv, na_values="#NULL!", keep_default_na=False)
        df_user_missing_sav["mydate"] = [datetime.strptime(x, '%Y-%m-%d').date() if type(x) == str else float('nan') for x in
                                         df_user_missing_sav["mydate"]]
        df_user_missing_sav["dtime"] = [datetime.strptime(x, '%Y-%m-%dT%H:%M:%S.000000') if type(x) == str else float('nan')
                                   for x in df_user_missing_sav["dtime"]]
        df_user_missing_sav["mytime"] = [datetime.strptime(x, '%H:%M:%S.000000').time() if type(x) == str else float('nan')
                                    for x in df_user_missing_sav["mytime"]]
        self.df_user_missing_sav = df_user_missing_sav

        # no dates
        nodates_spss_csv = os.path.join(self.basic_data_folder, "sample_nodate_spss.csv")
        df_nodates_spss = pd.read_csv(nodates_spss_csv)
        df_nodates_spss["myord"] = df_nodates_spss["myord"].astype(float)
        df_nodates_spss["mylabl"] = df_nodates_spss["mylabl"].astype(float)
        self.df_nodates_spss = df_nodates_spss

        nodates_sastata_csv = os.path.join(self.basic_data_folder, "sample_nodate_sas_stata.csv")
        df_nodates_sastata = pd.read_csv(nodates_sastata_csv)
        df_nodates_sastata["myord"] = df_nodates_sastata["myord"].astype(float)
        df_nodates_sastata["mylabl"] = df_nodates_sastata["mylabl"].astype(float)
        self.df_nodates_sastata = df_nodates_sastata
        

    def setUp(self):

        # set paths
        self._prepare_data()

    def test_sas7bdat(self):

        df, meta = pyreadstat.read_sas7bdat(os.path.join(self.basic_data_folder, "sample.sas7bdat"))
        self.assertTrue(df.equals(self.df_pandas))
        self.assertTrue(meta.number_columns == len(self.df_pandas.columns))
        self.assertTrue(meta.number_rows == len(self.df_pandas))

    def test_sas7bdat_metaonly(self):

        df, meta = pyreadstat.read_sas7bdat(os.path.join(self.basic_data_folder, "sample.sas7bdat"))
        df2, meta2 = pyreadstat.read_sas7bdat(os.path.join(self.basic_data_folder, "sample.sas7bdat"), metadataonly=True)
        self.assertTrue(df2.empty)
        self.assertTrue(meta.number_columns == meta2.number_columns)
        self.assertTrue(meta.number_rows == meta2.number_rows)
        self.assertTrue(meta.column_names == meta2.column_names)
        self.assertTrue(meta.column_labels == meta2.column_labels)

    def test_sas7bdat_usecols(self):

        df, meta = pyreadstat.read_sas7bdat(os.path.join(self.basic_data_folder, "sample.sas7bdat"), usecols=self.usecols)
        self.assertTrue(df.equals(self.df_usecols))
        self.assertTrue(meta.number_columns == len(self.usecols))
        self.assertTrue(meta.column_names == self.usecols)
        
    def test_sas7bdat_international(self):
        """
        On windows, paths with international characters are problematic. This is verifying that it is working as expected
        """
        # in addition, this works only in python 3
        if sys.version_info[0]>2:
            df, meta = pyreadstat.read_sas7bdat(os.path.join(self.international_data_folder, "sample.sas7bdat"))
            self.assertTrue(df.equals(self.df_pandas))
            self.assertTrue(meta.number_columns == len(self.df_pandas.columns))
            self.assertTrue(meta.number_rows == len(self.df_pandas))

    def test_sas7bdat_nodates(self):
        df, meta = pyreadstat.read_sas7bdat(os.path.join(self.basic_data_folder, "sample.sas7bdat"), disable_datetime_conversion=True)
        self.assertTrue(df.equals(self.df_nodates_sastata))

    def test_xport(self):

        df, meta = pyreadstat.read_xport(os.path.join(self.basic_data_folder, "sample.xpt"))
        df.columns = [x.lower() for x in df.columns]
        self.assertTrue(df.equals(self.df_pandas))
        self.assertTrue(meta.number_columns == len(self.df_pandas.columns))
        self.assertTrue(meta.number_rows == len(self.df_pandas))

    def test_xport_metaonly(self):

        df, meta = pyreadstat.read_xport(os.path.join(self.basic_data_folder, "sample.xpt"))
        df2, meta2 = pyreadstat.read_xport(os.path.join(self.basic_data_folder, "sample.xpt"), metadataonly=True)
        self.assertTrue(df2.empty)
        self.assertTrue(meta.number_columns == meta2.number_columns)
        self.assertTrue(meta2.number_rows is None)
        self.assertTrue(meta.column_names == meta2.column_names)
        self.assertTrue(meta.column_labels == meta2.column_labels)

    def test_xport_usecols(self):
        # Currently readstat does not support skipping cols for XPT files,
        usecols = [x.upper() for x in self.usecols]
        df, meta = pyreadstat.pyreadstat.read_xport(os.path.join(self.basic_data_folder, "sample.xpt"), usecols=usecols)
        df.columns = [x.lower() for x in df.columns]
        self.assertTrue(df.equals(self.df_usecols))
        self.assertTrue(meta.number_columns == len(self.usecols))

    def test_xport_nodates(self):
        df, meta = pyreadstat.read_xport(os.path.join(self.basic_data_folder, "sample.xpt"), disable_datetime_conversion=True)
        df.columns = [x.lower() for x in df.columns]
        self.assertTrue(df.equals(self.df_nodates_sastata))

    def test_dta(self):

        # discard dtime and arrange time
        df, meta = pyreadstat.read_dta(os.path.join(self.basic_data_folder, "sample.dta"))
        df_pandas = self.df_pandas.copy()
        df_pandas["myord"] = df_pandas["myord"].astype(np.int64)
        df_pandas["mylabl"] = df_pandas["mylabl"].astype(np.int64)
        self.assertTrue(df.equals(df_pandas))
        self.assertTrue(meta.number_columns == len(df_pandas.columns))
        self.assertTrue(meta.number_rows == len(df_pandas))

    def test_dta_metaonly(self):

        df, meta = pyreadstat.read_dta(os.path.join(self.basic_data_folder, "sample.dta"))
        df2, meta2 = pyreadstat.read_dta(os.path.join(self.basic_data_folder, "sample.dta"), metadataonly=True)
        self.assertTrue(df2.empty)
        self.assertTrue(meta.number_columns == meta2.number_columns)
        self.assertTrue(meta.number_rows == meta2.number_rows)
        self.assertTrue(meta.column_names == meta2.column_names)
        self.assertTrue(meta.column_labels == meta2.column_labels)

    def test_dta_usecols(self):
        df, meta = pyreadstat.read_dta(os.path.join(self.basic_data_folder, "sample.dta"), usecols=self.usecols)
        df_pandas = self.df_usecols.copy()
        df_pandas["myord"] = df_pandas["myord"].astype(np.int64)
        self.assertTrue(df.equals(df_pandas))
        self.assertTrue(meta.number_columns == len(self.usecols))
        self.assertTrue(meta.column_names == self.usecols)

    def test_dta_nodates(self):
        df, meta = pyreadstat.read_dta(os.path.join(self.basic_data_folder,"sample.dta"), disable_datetime_conversion=True)
        df_pandas = self.df_nodates_sastata
        df_pandas["myord"] = df_pandas["myord"].astype(np.int64)
        df_pandas["mylabl"] = df_pandas["mylabl"].astype(np.int64)
        df_pandas["dtime"] = df_pandas["dtime"] * 1000
        df_pandas["mytime"] = df_pandas["mytime"] * 1000
        self.assertTrue(df.equals(df_pandas))

    def test_sav(self):

        df, meta = pyreadstat.read_sav(os.path.join(self.basic_data_folder, "sample.sav"))
        self.assertTrue(df.equals(self.df_pandas))
        self.assertTrue(meta.number_columns == len(self.df_pandas.columns))
        self.assertTrue(meta.number_rows == len(self.df_pandas))
        self.assertTrue(len(meta.notes)>0)
        self.assertTrue(meta.variable_display_width["mychar"]==9)
        self.assertTrue(meta.variable_storage_width["mychar"] == 8)
        self.assertTrue(meta.variable_measure["mychar"]=="nominal")

    def test_sav_metaonly(self):

        df, meta = pyreadstat.read_sav(os.path.join(self.basic_data_folder, "sample.sav"))
        df2, meta2 = pyreadstat.read_sav(os.path.join(self.basic_data_folder, "sample.sav"), metadataonly=True)
        self.assertTrue(df2.empty)
        self.assertTrue(meta.number_columns == meta2.number_columns)
        self.assertTrue(meta.number_rows == meta2.number_rows)
        self.assertTrue(meta.column_names == meta2.column_names)
        self.assertTrue(meta.column_labels == meta2.column_labels)
        self.assertTrue(len(meta2.notes) > 0)

    def test_sav_formatted(self):
        df, meta = pyreadstat.read_sav(os.path.join(self.basic_data_folder, "sample.sav"), apply_value_formats=True, formats_as_category=True)
        #df.columns = self.df_pandas_formatted.columns
        self.assertTrue(df.equals(self.df_pandas_formatted))
        self.assertTrue(meta.number_columns == len(self.df_pandas_formatted.columns))
        self.assertTrue(meta.number_rows == len(self.df_pandas_formatted))
        self.assertTrue(len(meta.notes) > 0)

    def test_sav_usecols(self):
        df, meta = pyreadstat.read_sav(os.path.join(self.basic_data_folder, "sample.sav"), usecols=self.usecols)
        self.assertTrue(df.equals(self.df_usecols))
        self.assertTrue(meta.number_columns == len(self.usecols))
        self.assertTrue(meta.column_names == self.usecols)

    def test_sav_missing(self):
        df, meta = pyreadstat.read_sav(os.path.join(self.basic_data_folder, "sample_missing.sav"))
        self.assertTrue(df.equals(self.df_missing_sav))
        self.assertTrue(meta.missing_ranges == {})
        df_user, meta_user = pyreadstat.read_sav(os.path.join(self.basic_data_folder, "sample_missing.sav"), user_missing=True)
        self.assertTrue(df_user.equals(self.df_user_missing_sav))
        self.assertTrue(meta_user.missing_ranges['mynum'][0]=={'lo': 2000.0, 'hi': 3000.0})
        # user missing with usecols
        df_user, meta_user = pyreadstat.read_sav(os.path.join(self.basic_data_folder, "sample_missing.sav"), user_missing=True, usecols=["mynum", "mylabl"])
        df_sub = self.df_user_missing_sav[["mynum", "mylabl"]]
        self.assertTrue(df_user.equals(df_sub))

    def test_sav_nodates(self):
        df, meta = pyreadstat.read_sav(os.path.join(self.basic_data_folder, "sample.sav"), disable_datetime_conversion=True)
        self.assertTrue(df.equals(self.df_nodates_spss))
        
    def test_zsav(self):

        df, meta = pyreadstat.read_sav(os.path.join(self.basic_data_folder, "sample.zsav"))
        self.assertTrue(df.equals(self.df_pandas))
        self.assertTrue(meta.number_columns == len(self.df_pandas.columns))
        self.assertTrue(meta.number_rows == len(self.df_pandas))
        self.assertTrue(len(meta.notes) > 0)

    def test_zsav_metaonly(self):

        df, meta = pyreadstat.read_sav(os.path.join(self.basic_data_folder, "sample.zsav"))
        df2, meta2 = pyreadstat.read_sav(os.path.join(self.basic_data_folder, "sample.sav"), metadataonly=True)
        self.assertTrue(df2.empty)
        self.assertTrue(meta.number_columns == meta2.number_columns)
        self.assertTrue(meta.number_rows == meta2.number_rows)
        self.assertTrue(meta.column_names == meta2.column_names)
        self.assertTrue(meta.column_labels == meta2.column_labels)
        self.assertTrue(len(meta2.notes) > 0)

    def test_zsav_formatted(self):
        df, meta = pyreadstat.read_sav(os.path.join(self.basic_data_folder, "sample.zsav"), apply_value_formats=True, formats_as_category=True)
        self.assertTrue(df.equals(self.df_pandas_formatted))
        self.assertTrue(meta.number_columns == len(self.df_pandas_formatted.columns))
        self.assertTrue(meta.number_rows == len(self.df_pandas_formatted))
        self.assertTrue(len(meta.notes) > 0)

    def test_zsav_usecols(self):
        df, meta = pyreadstat.read_sav(os.path.join(self.basic_data_folder, "sample.zsav"), usecols=self.usecols)
        self.assertTrue(df.equals(self.df_usecols))
        self.assertTrue(meta.number_columns == len(self.usecols))
        self.assertTrue(meta.column_names == self.usecols)

    def test_zsav_nodates(self):
        df, meta = pyreadstat.read_sav(os.path.join(self.basic_data_folder, "sample.zsav"), disable_datetime_conversion=True)
        self.assertTrue(df.equals(self.df_nodates_spss))

    def test_por(self):
        df, meta = pyreadstat.read_por(os.path.join(self.basic_data_folder, "sample.por"))
        # dates, datetimes and timestamps are not translated but stay as integers, let's just drop them
        df_pandas_por = self.df_pandas.drop(labels=["dtime", "mydate", "mytime"], axis=1)
        df.columns = [x.lower() for x in df.columns]
        df = df.drop(labels=["dtime", "mydate", "mytime"], axis=1)
        self.assertTrue(df.equals(df_pandas_por))
        self.assertTrue(meta.number_columns == len(self.df_pandas.columns))
        self.assertTrue(meta.number_rows == len(df_pandas_por))
        self.assertTrue(len(meta.notes) > 0)

    def test_por_formatted(self):
        df, meta = pyreadstat.read_por(os.path.join(self.basic_data_folder, "sample.por"), apply_value_formats=True, formats_as_category=True)
        # dates, datetimes and timestamps are not translated but stay as integers, let's just drop them
        df_pandas_por = self.df_pandas_formatted.drop(labels=["dtime", "mydate", "mytime"], axis=1)
        df.columns = [x.lower() for x in df.columns]
        df = df.drop(labels=["dtime", "mydate", "mytime"], axis=1)
        self.assertTrue(df.equals(df_pandas_por))
        self.assertTrue(meta.number_columns == len(self.df_pandas_formatted.columns))
        self.assertTrue(meta.number_rows == len(df_pandas_por))
        self.assertTrue(len(meta.notes) > 0)

    def test_por_metaonly(self):

        df, meta = pyreadstat.read_por(os.path.join(self.basic_data_folder, "sample.por"))
        df2, meta2 = pyreadstat.read_por(os.path.join(self.basic_data_folder, "sample.por"), metadataonly=True)
        self.assertTrue(df2.empty)
        self.assertTrue(meta.number_columns == meta2.number_columns)
        self.assertTrue(meta2.number_rows is None)
        self.assertTrue(meta.column_names == meta2.column_names)
        self.assertTrue(meta.column_labels == meta2.column_labels)
        self.assertTrue(len(meta2.notes) > 0)

    def test_por_usecols(self):
        df, meta = pyreadstat.read_por(os.path.join(self.basic_data_folder, "sample.por"),  usecols=["MYNUM"])
        df_pandas_por = self.df_pandas[["mynum"]]
        df.columns = [x.lower() for x in df.columns]
        self.assertTrue(df.equals(df_pandas_por))
        self.assertTrue(meta.number_columns == len(df_pandas_por.columns.values.tolist()))

    def test_por_nodates(self):
        df, meta = pyreadstat.read_por(os.path.join(self.basic_data_folder, "sample.por"), disable_datetime_conversion=True)
        df.columns = [x.lower() for x in df.columns]
        self.assertTrue(df.equals(self.df_nodates_spss))

    def test_sas_catalog_win(self):
        """these sas7bdat and sasbcat where produced on windows, probably 32 bit"""
        dat = os.path.join(self.catalog_data_folder, "test_data_win.sas7bdat")
        cat = os.path.join(self.catalog_data_folder, "test_formats_win.sas7bcat")
        df, meta = pyreadstat.read_sas7bdat(dat, catalog_file=cat)
        self.assertTrue(df.equals(self.df_sas_format))

    def test_sas_catalog_linux(self):
        """these sas7bdat and sasbcat where produced on linux 64 bit"""
        dat = os.path.join(self.catalog_data_folder, "test_data_linux.sas7bdat")
        cat = os.path.join(self.catalog_data_folder, "test_formats_linux.sas7bcat")
        df, meta = pyreadstat.read_sas7bdat(dat, catalog_file=cat)
        self.assertTrue(df.equals(self.df_sas_format))

    def test_sas_dates(self):

        sas_file = os.path.join(self.basic_data_folder, "dates.sas7bdat")
        df_sas, meta = pyreadstat.read_sas7bdat(sas_file)
        self.assertTrue(df_sas.equals(self.df_sas_dates))

    def test_sas_dates_as_pandas(self):

        sas_file = os.path.join(self.basic_data_folder, "dates.sas7bdat")
        df_sas, meta = pyreadstat.read_sas7bdat(sas_file, dates_as_pandas_datetime=True)
        self.assertTrue(df_sas.equals(self.df_sas_dates_as_pandas))
        
    def test_sas_user_missing(self):
        sas_file = os.path.join(self.missing_data_folder, "missing_test.sas7bdat")
        cat_file = os.path.join(self.missing_data_folder, "missing_formats.sas7bcat")
        unformatted_csv = os.path.join(self.missing_data_folder, "missing_unformatted.csv")
        formatted_csv = os.path.join(self.missing_data_folder, "missing_sas_formatted.csv")
        labeled_csv = os.path.join(self.missing_data_folder, "missing_sas_labeled.csv")
        
        df_sas, meta = pyreadstat.read_sas7bdat(sas_file)
        df_csv = pd.read_csv(unformatted_csv)
        self.assertTrue(df_sas.equals(df_csv))
        
        df_sas, meta = pyreadstat.read_sas7bdat(sas_file, user_missing=True)
        df_csv = pd.read_csv(formatted_csv)
        self.assertTrue(df_sas.equals(df_csv))
        self.assertTrue(meta.missing_user_values == ['A', 'B', 'C', 'X', 'Y', 'Z', '_'])
        
        df_sas, meta = pyreadstat.read_sas7bdat(sas_file,
                            catalog_file=cat_file, user_missing=True,
                            formats_as_category=False)
        df_csv = pd.read_csv(labeled_csv)
        self.assertTrue(df_sas.equals(df_csv))
        
    def test_dta_user_missing(self):
        dta_file = os.path.join(self.missing_data_folder, "missing_test.dta")
        unformatted_csv = os.path.join(self.missing_data_folder, "missing_unformatted.csv")
        formatted_csv = os.path.join(self.missing_data_folder, "missing_dta_formatted.csv")
        labeled_csv = os.path.join(self.missing_data_folder, "missing_dta_labeled.csv")
        
        df_sas, meta = pyreadstat.read_dta(dta_file)
        df_csv = pd.read_csv(unformatted_csv)
        self.assertTrue(df_sas.equals(df_csv))
        
        df_sas, meta = pyreadstat.read_dta(dta_file, user_missing=True)
        df_csv = pd.read_csv(formatted_csv)
        self.assertTrue(df_sas.equals(df_csv))
        self.assertTrue(meta.missing_user_values == ['a', 'b', 'c', 'x', 'y', 'z'])
        
        df_sas, meta = pyreadstat.read_dta(dta_file,
                            apply_value_formats=True, user_missing=True,
                            formats_as_category=False)
        df_csv = pd.read_csv(labeled_csv)
        self.assertTrue(df_sas.equals(df_csv))
        
    def test_sav_user_missing(self):
        sav_file = os.path.join(self.missing_data_folder, "missing_test.sav")
        unformatted_csv = os.path.join(self.missing_data_folder, "missing_sav_unformatted.csv")
        formatted_csv = os.path.join(self.missing_data_folder, "missing_sav_formatted.csv")
        labeled_csv = os.path.join(self.missing_data_folder, "missing_sav_labeled.csv")
        
        df_sas, meta = pyreadstat.read_sav(sav_file)
        df_csv = pd.read_csv(unformatted_csv)
        self.assertTrue(df_sas.equals(df_csv))
        
        df_sas, meta = pyreadstat.read_sav(sav_file, user_missing=True)
        df_csv = pd.read_csv(formatted_csv)
        self.assertTrue(df_sas.equals(df_csv))
        
        df_sas, meta = pyreadstat.read_sav(sav_file,
                            apply_value_formats=True, user_missing=True,
                            formats_as_category=False)
        df_sas['var1'].loc[1] = int(df_sas['var1'][1])
        df_sas['var1'] = df_sas['var1'].astype(str)
        df_csv = pd.read_csv(labeled_csv)
        self.assertTrue(df_sas.equals(df_csv))
        
    def test_sav_missing_char(self):
        df, meta = pyreadstat.read_sav(os.path.join(self.missing_data_folder, "missing_char.sav"))
        mdf = pd.DataFrame([[np.nan], ["a"]], columns=["mychar"])
        self.assertTrue(df.equals(mdf))
        self.assertTrue(meta.missing_ranges == {})
        df2, meta2 = pyreadstat.read_sav(os.path.join(self.missing_data_folder, "missing_char.sav"), user_missing=True)
        mdf2 = pd.DataFrame([["Z"], ["a"]], columns=["mychar"])
        self.assertTrue(df2.equals(mdf2))
        self.assertTrue(meta2.missing_ranges['mychar'][0]=={'lo': "Z", 'hi': "Z"})

    # writing: none of this works on python 2

    def test_sav_write_basic(self):

        #if sys.version_info[0] < 3:
        #    return

        file_label = "basic write"
        file_note = "These are some notes"
        col_labels = ["mychar label","mynum label", "mydate label", "dtime label", None, "myord label", "mytime label"]
        path = os.path.join(self.write_folder, "basic_write.sav")
        pyreadstat.write_sav(self.df_pandas, path, file_label=file_label, column_labels=col_labels, note=file_note)
        df, meta = pyreadstat.read_sav(path)
        self.assertTrue(df.equals(self.df_pandas))
        self.assertEqual(meta.file_label, file_label)
        self.assertListEqual(meta.column_labels, col_labels)
        self.assertEqual(meta.notes[0], file_note)

    def test_zsav_write_basic(self):

        #if sys.version_info[0] < 3:
        #    return

        file_label = "basic write"
        file_note = "These are some notes"
        col_labels = ["mychar label","mynum label", "mydate label", "dtime label", None, "myord label", "mytime label"]
        path = os.path.join(self.write_folder, "basic_write.zsav")
        pyreadstat.write_sav(self.df_pandas, path, file_label=file_label, column_labels=col_labels, compress=True, note=file_note)
        df, meta = pyreadstat.read_sav(path)
        self.assertTrue(df.equals(self.df_pandas))
        self.assertEqual(meta.file_label, file_label)
        self.assertListEqual(meta.column_labels, col_labels)
        self.assertEqual(meta.notes[0], file_note)

    def test_dta_write_basic(self):

        #if sys.version_info[0] < 3:
        #    return

        df_pandas = self.df_pandas.copy()
        df_pandas["myord"] = df_pandas["myord"].astype(np.int32)
        df_pandas["mylabl"] = df_pandas["mylabl"].astype(np.int32)

        file_label = "basic write"
        col_labels = ["mychar label","mynum label", "mydate label", "dtime label", None, "myord label", "mytime label"]
        path = os.path.join(self.write_folder, "basic_write.dta")
        pyreadstat.write_dta(df_pandas, path, file_label=file_label, column_labels=col_labels, version=12)
        df, meta = pyreadstat.read_dta(path)

        df_pandas["myord"] = df_pandas["myord"].astype(np.int64)
        df_pandas["mylabl"] = df_pandas["mylabl"].astype(np.int64)

        self.assertTrue(df.equals(df_pandas))
        self.assertEqual(meta.file_label, file_label)
        self.assertListEqual(meta.column_labels, col_labels)

    def test_xport_write_basic(self):

        #if sys.version_info[0] < 3:
        #    return

        file_label = "basic write"
        table_name = "TEST"
        col_labels = ["mychar label","mynum label", "mydate label", "dtime label", None, "myord label", "mytime label"]
        path = os.path.join(self.write_folder, "write.xpt")
        pyreadstat.write_xport(self.df_pandas, path, file_label=file_label, column_labels=col_labels, table_name=table_name)
        df, meta = pyreadstat.read_xport(path)
        df.columns = [x.lower() for x in df.columns]

        self.assertTrue(df.equals(self.df_pandas))
        self.assertEqual(meta.file_label, file_label)
        self.assertListEqual(meta.column_labels, col_labels)
        self.assertEqual(table_name, meta.table_name)

    def test_sav_write_dates(self):

        #if sys.version_info[0] < 3:
        #    return

        path = os.path.join(self.write_folder, "dates_write.sav")
        pyreadstat.write_sav(self.df_sas_dates, path)
        df, meta = pyreadstat.read_sav(path)
        self.assertTrue(df.equals(self.df_sas_dates))

    def test_zsav_write_dates(self):

        #if sys.version_info[0] < 3:
        #    return

        path = os.path.join(self.write_folder, "dates_write.sav")
        pyreadstat.write_sav(self.df_sas_dates, path, compress=True)
        df, meta = pyreadstat.read_sav(path)
        self.assertTrue(df.equals(self.df_sas_dates))

    def test_dta_write_dates(self):

        #if sys.version_info[0] < 3:
        #    return

        path = os.path.join(self.write_folder, "dates_write.dta")
        pyreadstat.write_dta(self.df_sas_dates, path)
        df, meta = pyreadstat.read_dta(path)
        self.assertTrue(df.equals(self.df_sas_dates))

    def test_xport_write_dates(self):

        #if sys.version_info[0] < 3:
        #    return

        path = os.path.join(self.write_folder, "dates_write.xpt")
        pyreadstat.write_xport(self.df_sas_dates, path)
        df, meta = pyreadstat.read_xport(path)
        self.assertTrue(df.equals(self.df_sas_dates))
        

if __name__ == '__main__':

    import sys

    if "--inplace" in sys.argv:

        script_folder = os.path.split(os.path.split(os.path.realpath(__file__))[0])[0]
        sys.path.insert(0, script_folder)
        sys.argv.remove('--inplace')

    import pyreadstat

    print("package location:", pyreadstat.__file__)

    unittest.main()
