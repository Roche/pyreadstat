#-*- coding: utf-8 -*-
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

from datetime import datetime, timedelta, date
import unittest
import os
import sys
import shutil

import pandas as pd
import numpy as np

is_pathlib_available = False
try:
    from pathlib import Path
    is_pathlib_available = True
except:
    pass


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
        self.mr_data_folder = os.path.join(self.data_folder, "multiple_response")
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
        df_dates1["time"] = pd.to_datetime(df_dates1["time"], format='%H:%M:%S')
        df_dates1["time"] = df_dates1["time"].apply(lambda x: x.time())
        self.df_sas_dates_as_pandas = df_dates1

        df_dates2 = df_dates1.copy()
        df_dates2["date"] = df_dates2["date"].apply(lambda x: x.date())
        self.df_sas_dates = df_dates2
        self.df_sas_dates2 = pd.concat([self.df_sas_dates, pd.DataFrame([[np.nan, pd.NaT, np.nan]],columns=["date", "dtime", "time"])], ignore_index=True)

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

        # character column with nan and object column with nan (object pyreadstat writer doesn't know what to do with)
        self.df_charnan = pd.DataFrame([[0,np.nan,np.nan],[1,"test", timedelta]], columns = ["integer", "string", "object"])

        # xport files v5 vs v8
        self.xptv5v8 = pd.DataFrame([[float(x)] for x in range(1,11)], columns=["i"])

        # long string

        self.df_longstr = pd.DataFrame({
                "v1": {
                    "10001": """Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas ac pretium sem. Fusce aliquet
                    augue rhoncus consequat pulvinar. In est ex, porta congue diam sed, laoreet suscipit purus. Phasellus mollis
                    lobortis tellus at vehicula. Etiam egestas augue id massa bibendum volutpat id et ipsum. Praesent ut lorem
                    rhoncus, pharetra risus sed, pharetra sem. In pulvinar egestas erat, id condimentum tortor tempus sed. Duis
                    ornare lacus ut ligula congue, non convallis urna dignissim. Etiam vehicula turpis sit amet nisi finibus
                    laoreet. Duis molestie consequat nulla, non lobortis est tempus sit amet. Quisque elit est,
                    congue non commodo vitae, porttitor ac erat. """,
                    "10002": "fgsdghshsgh",
                    "10003": "gsfdgsdg",
                },
                "v2": {
                    "10001": "gsfdgsfdgsfg",
                    "10002": "fgsdghshsgh",
                    "10003": "gsfdgsdg",
                },

            })

    def setUp(self):

        # set paths
        self._prepare_data()

    def test_sas7bdat(self):
        df, meta = pyreadstat.read_sas7bdat(os.path.join(self.basic_data_folder, "sample.sas7bdat"))
        self.assertTrue(df.equals(self.df_pandas))
        self.assertTrue(meta.number_columns == len(self.df_pandas.columns))
        self.assertTrue(meta.number_rows == len(self.df_pandas))
        #self.assertTrue(meta.creation_time==datetime(2018, 8, 16, 18, 21, 52))
        #self.assertTrue(meta.modification_time==datetime(2018, 8, 16, 18, 21, 52))

    def test_sas7bdat_bincompressed(self):
        df, meta = pyreadstat.read_sas7bdat(os.path.join(self.basic_data_folder, "sample_bincompressed.sas7bdat"))
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
        self.assertTrue(meta.readstat_variable_types["mychar"]=="string")
        self.assertTrue(meta.readstat_variable_types["myord"]=="double")
        self.assertTrue(meta.readstat_variable_types["dtime"]=="double")

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

    def test_sas7bdat_chunk(self):
        df, meta = pyreadstat.read_sas7bdat(os.path.join(self.basic_data_folder, "sample.sas7bdat"), row_limit = 2, row_offset =1)
        df_pandas = self.df_pandas.iloc[1:3,:].reset_index(drop=True)
        df_pandas["dtime"] = pd.to_datetime(df_pandas["dtime"])
        self.assertTrue(df.equals(df_pandas))
        self.assertTrue(meta.number_columns == len(self.df_pandas.columns))
        self.assertTrue(meta.number_rows == len(df_pandas))

    def test_xport(self):
        df, meta = pyreadstat.read_xport(os.path.join(self.basic_data_folder, "sample.xpt"))
        df.columns = [x.lower() for x in df.columns]
        self.assertTrue(df.equals(self.df_pandas))
        self.assertTrue(meta.number_columns == len(self.df_pandas.columns))
        self.assertTrue(meta.number_rows == len(self.df_pandas))
        self.assertTrue(meta.number_rows==len(df))
        #self.assertTrue(meta.creation_time==datetime(2018, 8, 14, 10, 55, 46))
        #self.assertTrue(meta.modification_time==datetime(2018, 8, 14, 10, 55, 46))

    def test_xport_v5(self):
        df, meta = pyreadstat.read_xport(os.path.join(self.basic_data_folder, "sas.xpt5"))
        df.columns = [x.lower() for x in df.columns]
        self.assertTrue(df.equals(self.xptv5v8))
        self.assertTrue(meta.number_rows==len(df))

    def test_xport_v8(self):
        df, meta = pyreadstat.read_xport(os.path.join(self.basic_data_folder, "sas.xpt8"))
        self.assertTrue(df.equals(self.xptv5v8))
        self.assertTrue(meta.number_rows==len(df))

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

    def test_xport_chunks(self):
        df, meta = pyreadstat.read_xport(os.path.join(self.basic_data_folder, "sample.xpt"), row_limit = 2, row_offset =1)
        df.columns = [x.lower() for x in df.columns]
        df_pandas = self.df_pandas.iloc[1:3,:].reset_index(drop=True)
        df_pandas["dtime"] = pd.to_datetime(df_pandas["dtime"])
        self.assertTrue(df.equals(df_pandas))
        self.assertTrue(meta.number_columns == len(self.df_pandas.columns))
        self.assertTrue(meta.number_rows == len(df_pandas))

    def test_dta(self):
        # discard dtime and arrange time
        df, meta = pyreadstat.read_dta(os.path.join(self.basic_data_folder, "sample.dta"))
        df_pandas = self.df_pandas.copy()
        df_pandas["myord"] = df_pandas["myord"].astype(np.int64)
        df_pandas["mylabl"] = df_pandas["mylabl"].astype(np.int64)
        self.assertTrue(df.equals(df_pandas))
        self.assertTrue(meta.number_columns == len(df_pandas.columns))
        self.assertTrue(meta.number_rows == len(df_pandas))
        self.assertTrue(meta.readstat_variable_types["mychar"]=="string")
        self.assertTrue(meta.readstat_variable_types["myord"]=="int8")
        self.assertTrue(meta.readstat_variable_types["dtime"]=="double")
        #self.assertTrue(meta.creation_time==datetime(2018, 12, 17, 14, 53))
        #self.assertTrue(meta.modification_time==datetime(2018, 12, 17, 14, 53))

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

    def test_dta_chunks(self):
        # discard dtime and arrange time
        df, meta = pyreadstat.read_dta(os.path.join(self.basic_data_folder, "sample.dta"), row_limit = 2, row_offset =1)
        df_pandas = self.df_pandas.iloc[1:3,:].reset_index(drop=True)
        df_pandas["dtime"] = pd.to_datetime(df_pandas["dtime"])
        df_pandas["myord"] = df_pandas["myord"].astype(np.int64)
        df_pandas["mylabl"] = df_pandas["mylabl"].astype(np.int64)
        self.assertTrue(df.equals(df_pandas))
        self.assertTrue(meta.number_columns == len(df_pandas.columns))
        self.assertTrue(meta.number_rows == len(df_pandas))

    def test_sav(self):
        df, meta = pyreadstat.read_sav(os.path.join(self.basic_data_folder, "sample.sav"))
        self.assertTrue(df.equals(self.df_pandas))
        self.assertTrue(meta.number_columns == len(self.df_pandas.columns))
        self.assertTrue(meta.number_rows == len(self.df_pandas))
        self.assertTrue(len(meta.notes)>0)
        self.assertTrue(meta.variable_display_width["mychar"]==9)
        self.assertTrue(meta.variable_storage_width["mychar"] == 8)
        self.assertTrue(meta.variable_measure["mychar"]=="nominal")
        self.assertTrue(meta.readstat_variable_types["mychar"]=="string")
        self.assertTrue(meta.readstat_variable_types["myord"]=="double")
        #self.assertTrue(meta.creation_time==datetime(2018, 8, 16, 17, 22, 33))
        #self.assertTrue(meta.modification_time==datetime(2018, 8, 16, 17, 22, 33))

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
        #import pdb; pdb.set_trace()
        self.assertTrue(df.equals(self.df_nodates_spss))

    def test_sav_chunks(self):
        df, meta = pyreadstat.read_sav(os.path.join(self.basic_data_folder, "sample.sav"), row_limit = 2, row_offset =1)
        df_pandas = self.df_pandas.iloc[1:3,:].reset_index(drop=True)
        df_pandas["dtime"] = pd.to_datetime(df_pandas["dtime"])
        self.assertTrue(df.equals(df_pandas))
        self.assertTrue(meta.number_columns == len(df_pandas.columns))
        self.assertTrue(meta.number_rows == len(df_pandas))
        self.assertTrue(len(meta.notes)>0)
        self.assertTrue(meta.variable_display_width["mychar"]==9)
        self.assertTrue(meta.variable_storage_width["mychar"] == 8)
        self.assertTrue(meta.variable_measure["mychar"]=="nominal")
    
    def test_sav_expand(self):
        src = os.path.join(self.basic_data_folder, "sample.sav")
        dst = "~/sample.sav"
        shutil.copyfile(src, os.path.expanduser(dst))
        df, meta = pyreadstat.read_sav(dst)
        os.remove(os.path.expanduser(dst))
        self.assertTrue(df.equals(self.df_pandas))

       
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

    def test_zsav_chunks(self):
        df, meta = pyreadstat.read_sav(os.path.join(self.basic_data_folder, "sample.zsav"), row_limit = 2, row_offset =1)
        df_pandas = self.df_pandas.iloc[1:3,:].reset_index(drop=True)
        df_pandas["dtime"] = pd.to_datetime(df_pandas["dtime"])
        self.assertTrue(df.equals(df_pandas))
        self.assertTrue(meta.number_columns == len(df_pandas.columns))
        self.assertTrue(meta.number_rows == len(df_pandas))
        self.assertTrue(len(meta.notes)>0)
        self.assertTrue(meta.variable_display_width["mychar"]==9)
        self.assertTrue(meta.variable_storage_width["mychar"] == 8)
        self.assertTrue(meta.variable_measure["mychar"]=="nominal")

    def test_por(self):
        df, meta = pyreadstat.read_por(os.path.join(self.basic_data_folder, "sample.por"))
        df_pandas_por = self.df_pandas.copy()
        df.columns = [x.lower() for x in df.columns]
        self.assertTrue(df.equals(df_pandas_por))
        self.assertTrue(meta.number_columns == len(self.df_pandas.columns))
        self.assertTrue(meta.number_rows == len(df_pandas_por))
        self.assertTrue(len(meta.notes) > 0)
        #self.assertTrue(meta.creation_time==datetime(2018, 12, 16, 17, 28, 21))
        #self.assertTrue(meta.modification_time==datetime(2018, 12, 16, 17, 28, 21))

    def test_por_formatted(self):
        df, meta = pyreadstat.read_por(os.path.join(self.basic_data_folder, "sample.por"), apply_value_formats=True, formats_as_category=True)
        df_pandas_por = self.df_pandas_formatted.copy()
        df.columns = [x.lower() for x in df.columns]
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

    def test_por_chunks(self):
        df, meta = pyreadstat.read_por(os.path.join(self.basic_data_folder, "sample.por"), row_limit = 2, row_offset =1)
        df_pandas_por = self.df_pandas.iloc[1:3,:].reset_index(drop=True)
        df_pandas_por['dtime'] = pd.to_datetime(df_pandas_por.dtime)
        df.columns = [x.lower() for x in df.columns]
        self.assertTrue(df.equals(df_pandas_por))
        self.assertTrue(meta.number_columns == len(self.df_pandas.columns))
        self.assertTrue(meta.number_rows == len(df_pandas_por))
        self.assertTrue(len(meta.notes) > 0)

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
        missing_user_values = {'var1':['A'],'var2': ['B'], 'var3':['C'], 'var4':['X'], 'var5':['Y'], 
        'var6':['Z'], 'var7':['_']}
        self.assertDictEqual(meta.missing_user_values, missing_user_values)

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
        missing_user_values = {'var1':['a'],'var2': ['b'], 'var3':['c'], 'var4':['x'], 'var5':['y'], 'var6':['z']}
        self.assertDictEqual(meta.missing_user_values, missing_user_values)
        
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
        df_sas.loc[1, 'var1'] = int(df_sas['var1'][1])
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
    
    # test reading metadata for multiple response data

    def test_sav_multiple_response(self):
        """Assert MR data is correctly read from sav into metadata."""
        _, meta = pyreadstat.read_sav(os.path.join(self.mr_data_folder, "simple_alltypes.sav"))
        assert meta.mr_sets == {
            "categorical_array": {
                "type": "C",
                "is_dichotomy": False,
                "counted_value": None,
                "label": "",
                "variable_list": ["ca_subvar_1", "ca_subvar_2", "ca_subvar_3"]
            },
            "mymrset": {
                "type": "D",
                "is_dichotomy": True,
                "counted_value": 1,
                "label": "My multiple response set",
                "variable_list": ["bool1", "bool2", "bool3"]
            }
        }
    
    def test_sav_without_multiple_response(self):
        """Assert MR data is read as empty dict when not present in sav."""
        _, meta = pyreadstat.read_sav(os.path.join(self.missing_data_folder, "missing_char.sav"))
        assert meta.mr_sets == {}

    # read in chunks

    def test_chunk_reader(self):
        fpath = os.path.join(self.basic_data_folder, "sample.sas7bdat")
        reader = pyreadstat.read_file_in_chunks(pyreadstat.read_sas7bdat, fpath, chunksize= 2, offset=1, limit=2, disable_datetime_conversion=True)
        
        for df, meta in reader:
            pass
        
        currow = self.df_nodates_sastata.iloc[1:3,:].reset_index(drop=True)
        self.assertTrue(df.equals(currow))

    # read multiprocessing

    def test_multiprocess_reader(self):
        fpath = os.path.join(self.basic_data_folder, "sample_large.sav")
        df_multi, meta_multi = pyreadstat.read_file_multiprocessing(pyreadstat.read_sav, fpath) 
        df_single, meta_single = pyreadstat.read_sav(fpath)
        self.assertTrue(df_multi.equals(df_single))
        self.assertEqual(meta_multi.number_rows, meta_single.number_rows)

    def test_chunk_reader_multiprocess(self):
        fpath = os.path.join(self.basic_data_folder, "sample_large.sav")
        reader = pyreadstat.read_file_in_chunks(pyreadstat.read_sav, fpath, chunksize= 50, multiprocess=True)
        alldfs = list()
        for df, meta in reader:
            alldfs.append(df)
        df_multi = pd.concat(alldfs, axis=0, ignore_index=True) 
        df_single, meta_single = pyreadstat.read_sav(fpath)
        self.assertTrue(df_multi.equals(df_single))

    def test_chunk_reader_multiprocess_dict(self):
        fpath = os.path.join(self.basic_data_folder, "sample_large.sav")
        reader = pyreadstat.read_file_in_chunks(pyreadstat.read_sav, fpath, chunksize= 50, multiprocess=True, output_format='dict')
        alldfs = list()
        for chunkdict, meta in reader:
            df = pd.DataFrame(chunkdict)
            alldfs.append(df)
        df_multi = pd.concat(alldfs, axis=0, ignore_index=True) 
        df_single, meta_single = pyreadstat.read_sav(fpath)
        self.assertTrue(df_multi.equals(df_single))


    def test_multiprocess_reader_xport(self):
        fpath = os.path.join(self.basic_data_folder, "sample.xpt")
        df_multi, meta_multi = pyreadstat.read_file_multiprocessing(pyreadstat.read_xport, fpath, num_rows=1000) 
        df_single, meta_single = pyreadstat.read_xport(fpath)
        self.assertTrue(df_multi.equals(df_single))

    # writing

    def test_sav_write_basic(self):
        file_label = "basic write"
        file_note = "These are some notes"
        col_labels = ["mychar label","mynum label", "mydate label", "dtime label", None, "myord label", "mytime label"]
        variable_value_labels = {'mylabl': {1.0: 'Male', 2.0: 'Female'}, 'myord': {1.0: 'low', 2.0: 'medium', 3.0: 'high'}}
        missing_ranges = {'mychar':['a'], 'myord': [{'hi':2, 'lo':1}]}
        #variable_alignment = {'mychar':"center", 'myord':"right"}
        variable_display_width = {'mychar':20}
        variable_measure = {"mychar": "nominal"}
        path = os.path.join(self.write_folder, "basic_write.sav")
        pyreadstat.write_sav(self.df_pandas, path, file_label=file_label, column_labels=col_labels, note=file_note, 
            variable_value_labels=variable_value_labels, missing_ranges=missing_ranges, variable_display_width=variable_display_width,
            variable_measure=variable_measure) #, variable_alignment=variable_alignment)
        df, meta = pyreadstat.read_sav(path, user_missing=True)
        self.assertTrue(df.equals(self.df_pandas))
        self.assertEqual(meta.file_label, file_label)
        self.assertListEqual(meta.column_labels, col_labels)
        self.assertEqual(meta.notes[0], file_note)
        self.assertDictEqual(meta.variable_value_labels, variable_value_labels)
        self.assertEqual(meta.variable_display_width['mychar'], variable_display_width['mychar'])
        #self.assertDictEqual(meta.variable_alignment, variable_alignment)
        self.assertEqual(meta.variable_measure["mychar"], variable_measure["mychar"])

    def test_sav_write_basic_expanduser(self):
        file_label = "basic write"
        file_note = "These are some notes"
        col_labels = ["mychar label","mynum label", "mydate label", "dtime label", None, "myord label", "mytime label"]
        variable_value_labels = {'mylabl': {1.0: 'Male', 2.0: 'Female'}, 'myord': {1.0: 'low', 2.0: 'medium', 3.0: 'high'}}
        missing_ranges = {'mychar':['a'], 'myord': [{'hi':2, 'lo':1}]}
        #variable_alignment = {'mychar':"center", 'myord':"right"}
        variable_display_width = {'mychar':20}
        variable_measure = {"mychar": "nominal"}
        path = "~/sav_expand.sav" 
        pyreadstat.write_sav(self.df_pandas, path, file_label=file_label, column_labels=col_labels, note=file_note, 
            variable_value_labels=variable_value_labels, missing_ranges=missing_ranges, variable_display_width=variable_display_width,
            variable_measure=variable_measure) #, variable_alignment=variable_alignment)
        df, meta = pyreadstat.read_sav(path, user_missing=True)
        os.remove(os.path.expanduser(path))
        self.assertTrue(df.equals(self.df_pandas))

    def test_zsav_write_basic(self):
        file_label = "basic write"
        file_note = "These are some notes"
        col_labels = ["mychar label","mynum label", "mydate label", "dtime label", None, "myord label", "mytime label"]
        variable_value_labels = {'mylabl': {1.0: 'Male', 2.0: 'Female'}, 'myord': {1.0: 'low', 2.0: 'medium', 3.0: 'high'}}
        missing_ranges = {'mychar':['a'], 'myord': [{'hi':2, 'lo':1}]}
        path = os.path.join(self.write_folder, "basic_write.zsav")
        pyreadstat.write_sav(self.df_pandas, path, file_label=file_label, column_labels=col_labels, compress=True, note=file_note,
                     variable_value_labels=variable_value_labels, missing_ranges=missing_ranges)
        df, meta = pyreadstat.read_sav(path, user_missing=True)
        self.assertTrue(df.equals(self.df_pandas))
        self.assertEqual(meta.file_label, file_label)
        self.assertListEqual(meta.column_labels, col_labels)
        self.assertEqual(meta.notes[0], file_note)
        self.assertDictEqual(meta.variable_value_labels, variable_value_labels)

    def test_dta_write_basic(self):
        df_pandas = self.df_pandas.copy()
        df_pandas["myord"] = df_pandas["myord"].astype(np.int32)
        df_pandas["mylabl"] = df_pandas["mylabl"].astype(np.int32)

        file_label = "basic write"
        col_labels = ["mychar label","mynum label", "mydate label", "dtime label", None, "myord label", "mytime label"]
        variable_value_labels = {'mylabl': {1: 'Male', 2: 'Female'}, 'myord': {1: 'low', 2: 'medium', 3: 'high'}}
        path = os.path.join(self.write_folder, "basic_write.dta")
        pyreadstat.write_dta(df_pandas, path, file_label=file_label, column_labels=col_labels, version=12, variable_value_labels=variable_value_labels)
        df, meta = pyreadstat.read_dta(path)

        df_pandas["myord"] = df_pandas["myord"].astype(np.int64)
        df_pandas["mylabl"] = df_pandas["mylabl"].astype(np.int64)

        self.assertTrue(df.equals(df_pandas))
        self.assertEqual(meta.file_label, file_label)
        self.assertListEqual(meta.column_labels, col_labels)
        self.assertDictEqual(meta.variable_value_labels, variable_value_labels)

    def test_dta_write_user_missing(self):
        df_csv = pd.DataFrame([[3,"a"],["a","b"]], columns=["Var1", "Var2"])
        df_csv2 = pd.DataFrame([[3,"a"],["labeled","b"]], columns=["Var1", "Var2"])

        missing_user_values = {'Var1': ['a']}
        variable_value_labels = {'Var1':{'a':'labeled'}}
        path = os.path.join(self.write_folder, "user_missing_write.dta")
        pyreadstat.write_dta(df_csv, path, version=12, missing_user_values=missing_user_values, variable_value_labels=variable_value_labels)
        
        df_dta, meta = pyreadstat.read_dta(path, user_missing=True)
        self.assertTrue(df_csv.equals(df_dta))
        self.assertDictEqual(meta.missing_user_values, missing_user_values)
        
        df_dta2, meta2 = pyreadstat.read_dta(path, user_missing=True, apply_value_formats=True, formats_as_category=False)
        self.assertTrue(df_csv2.equals(df_dta2))

    def test_xport_write_basic_v8(self):
        file_label = "basic write"
        table_name = "TEST"
        col_labels = ["mychar label","mynum label", "mydate label", "dtime label", None, "myord label", "mytime label"]
        path = os.path.join(self.write_folder, "write.xpt")
        pyreadstat.write_xport(self.df_pandas, path, file_label=file_label, column_labels=col_labels, table_name=table_name, file_format_version=8)
        df, meta = pyreadstat.read_xport(path)
        df.columns = [x.lower() for x in df.columns]

        self.assertTrue(df.equals(self.df_pandas))
        self.assertEqual(meta.file_label, file_label)
        self.assertListEqual(meta.column_labels, col_labels)
        self.assertEqual(table_name, meta.table_name)

    def test_xport_write_basic_v5(self):
        file_label = "basic write"
        table_name = "TEST"
        col_labels = ["mychar label","mynum label", "mydate label", "dtime label", None, "myord label", "mytime label"]
        path = os.path.join(self.write_folder, "write.xpt")
        pyreadstat.write_xport(self.df_pandas, path, file_label=file_label, column_labels=col_labels, table_name=table_name, file_format_version=5)
        df, meta = pyreadstat.read_xport(path)
        df.columns = [x.lower() for x in df.columns]

        self.assertTrue(df.equals(self.df_pandas))
        self.assertEqual(meta.file_label, file_label)
        self.assertListEqual(meta.column_labels, col_labels)
        self.assertEqual(table_name, meta.table_name)

    def test_por_write_basic(self):

        file_label = "basic write"
        #file_note = "These are some notes"
        col_labels = ["mychar label","mynum label", "mydate label", "dtime label", None, "myord label", "mytime label"]
        path = os.path.join(self.write_folder, "write.por")
        pyreadstat.write_por(self.df_pandas, path, file_label=file_label, column_labels=col_labels) #, note=file_note)
        df, meta = pyreadstat.read_por(path)
        df.columns = [x.lower() for x in df.columns]
        self.assertTrue(df.equals(self.df_pandas))
        self.assertEqual(meta.file_label, file_label)
        self.assertListEqual(meta.column_labels, col_labels)
        #self.assertEqual(meta.notes[0], file_note)

    def test_sav_write_dates(self):

        path = os.path.join(self.write_folder, "dates_write.sav")
        pyreadstat.write_sav(self.df_sas_dates2, path)
        df, meta = pyreadstat.read_sav(path)
        self.assertTrue(df.equals(self.df_sas_dates2))

    def test_zsav_write_dates(self):

        path = os.path.join(self.write_folder, "dates_write_zsav.sav")
        pyreadstat.write_sav(self.df_sas_dates2, path, compress=True)
        df, meta = pyreadstat.read_sav(path)
        self.assertTrue(df.equals(self.df_sas_dates2))

    def test_dta_write_dates(self):

        path = os.path.join(self.write_folder, "dates_write.dta")
        pyreadstat.write_dta(self.df_sas_dates, path)
        df, meta = pyreadstat.read_dta(path)
        self.assertTrue(df.equals(self.df_sas_dates))

    def test_xport_write_dates(self):

        path = os.path.join(self.write_folder, "dates_write.xpt")
        pyreadstat.write_xport(self.df_sas_dates2, path)
        df, meta = pyreadstat.read_xport(path)
        #import pdb;pdb.set_trace()
        self.assertTrue(df.equals(self.df_sas_dates2))

    def test_sav_write_charnan(self):
        path = os.path.join(self.write_folder, "charnan.sav")
        pyreadstat.write_sav(self.df_charnan, path)
        df, meta = pyreadstat.read_sav(path)
        df2 = self.df_charnan
        df2.iloc[0,1] = ""
        df2.iloc[0,2] = ""
        df2['integer'] = df2["integer"].astype(float)
        df2['object'] = df2['object'].astype(str)
        self.assertTrue(df2.equals(df))

    def test_zsav_write_charnan(self):
        path = os.path.join(self.write_folder, "charnan_zsav.sav")
        pyreadstat.write_sav(self.df_charnan, path, compress=True)
        df, meta = pyreadstat.read_sav(path)
        df2 = self.df_charnan
        df2.iloc[0,1] = ""
        df2.iloc[0,2] = ""
        df2['integer'] = df2["integer"].astype(float)
        df2['object'] = df2['object'].astype(str)
        self.assertTrue(df2.equals(df))

    def test_xport_write_charnan(self):
        path = os.path.join(self.write_folder, "charnan.xpt")
        pyreadstat.write_xport(self.df_charnan, path)
        df, meta = pyreadstat.read_xport(path)
        df2 = self.df_charnan
        df2.iloc[0,1] = ""
        df2.iloc[0,2] = ""
        df2['integer'] = df2["integer"].astype(float)
        df2['object'] = df2['object'].astype(str)
        self.assertTrue(df2.equals(df))

    def test_por_write_charnan(self):
        path = os.path.join(self.write_folder, "charnan_zsav.por")
        pyreadstat.write_por(self.df_charnan, path)
        df, meta = pyreadstat.read_por(path)
        df.columns = [x.lower() for x in df.columns]
        df2 = self.df_charnan
        df2.iloc[0,1] = ""
        df2.iloc[0,2] = ""
        df2['integer'] = df2["integer"].astype(float)
        df2['object'] = df2['object'].astype(str)
        self.assertTrue(df2.equals(df))

    def test_dta_write_charnan(self):
        path = os.path.join(self.write_folder, "charnan.dta")
        pyreadstat.write_dta(self.df_charnan, path)
        df, meta = pyreadstat.read_dta(path)
        df2 = self.df_charnan
        df2.iloc[0,1] = ""
        df2.iloc[0,2] = ""
        df2['integer'] = df2["integer"].astype(float)
        df2['object'] = df2['object'].astype(str)
        self.assertTrue(df2.equals(df))

    def test_set_value_labels(self):

        df, meta = pyreadstat.read_sav(os.path.join(self.basic_data_folder, "sample.sav"))
        df_formatted = pyreadstat.set_value_labels(df, meta, formats_as_category=True)
        #df.columns = self.df_pandas_formatted.columns
        self.assertTrue(df_formatted.equals(self.df_pandas_formatted))
        # partial
        sub1_raw = df[['myord']]
        sub1 = pyreadstat.set_value_labels(sub1_raw, meta, formats_as_category=True)
        sub2 = self.df_pandas_formatted[['myord']]
        self.assertTrue(sub1.equals(sub2))
        
    def test_update_delete_file(self):
    
        df, meta = pyreadstat.read_sav(os.path.join(self.basic_data_folder, "sample.sav"))
        dst_path = os.path.join(self.write_folder, "update_test.sav")
        pyreadstat.write_sav(df, dst_path, variable_value_labels = meta.variable_value_labels)
        # update
        meta.variable_value_labels.update({'mylabl':{1.0:"Gents", 2.0:"Ladies"}})
        pyreadstat.write_sav(df, dst_path, variable_value_labels = meta.variable_value_labels)
        df2, meta2 = pyreadstat.read_sav(dst_path)
        self.assertDictEqual(meta2.variable_value_labels, meta.variable_value_labels)
        os.remove(dst_path)

    def test_xport_write_dates2_v8(self):
        # this sas7bdat file has features that are not compatible with v5
        df, meta = pyreadstat.read_sas7bdat(os.path.join(self.basic_data_folder, "dates_xpt.sas7bdat"))
        dst_path = os.path.join(self.write_folder, "dates_xptv8.xpt")
        pyreadstat.write_xport(df, dst_path, file_format_version=8)
        df2, meta2 = pyreadstat.read_xport(dst_path)
        self.assertTrue(df.equals(df2))

    def test_xport_dates2_v8(self):
        # this sas7bdat file has features that are not compatible with v5
        df, meta = pyreadstat.read_sas7bdat(os.path.join(self.basic_data_folder, "dates_xpt.sas7bdat"))
        # this xpt file was written in SAS from the sas7bdat file
        df2, meta2 = pyreadstat.read_xport(os.path.join(self.basic_data_folder, "dates_xpt_v8.xpt"))
        self.assertTrue(df.equals(df2))
        self.assertListEqual(meta.column_labels, meta2.column_labels)

    def test_sav_international_utf8_char_value(self):
        # a file that has a value with international characters and the file is coded in utf-8
        df, meta = pyreadstat.read_sav(os.path.join(self.basic_data_folder, "tegulu.sav"))
        self.assertTrue(df.iloc[0,1] == "నేను గతంలో వాడిన బ")

    def test_sav_international_varname(self):
        # a file with a varname with international characters
        df, meta = pyreadstat.read_sav(os.path.join(self.basic_data_folder, "hebrews.sav"))
        self.assertTrue(df.columns[0] == "ותק_ב")

    def test_sav_original_var_types(self):
        # a file with a varname with international characters
        df, meta = pyreadstat.read_sav(os.path.join(self.basic_data_folder, "test_width.sav"))
        self.assertEqual(meta.original_variable_types['StartDate'],'A1024')
        self.assertEqual(meta.original_variable_types['ResponseId'],'A18')
        self.assertEqual(meta.original_variable_types['Duration__in_seconds_'],'F40.2')
        self.assertEqual(meta.original_variable_types['Finished'],'F1.0')
        self.assertEqual(meta.readstat_variable_types['Finished'],'double')

    def test_sav_write_longstr(self):
        path = os.path.join(self.write_folder, "longstr.sav")
        pyreadstat.write_sav(self.df_longstr, path, variable_display_width={"v1": 1000})
        df, meta = pyreadstat.read_sav(path)
        self.assertTrue(meta.variable_display_width['v1']==1000)
        self.assertTrue(len(df.iloc[0,0])==781)

    def test_dta_write_longstr(self):
        path = os.path.join(self.write_folder, "longstr.dta")
        df_longstr = self.df_longstr
        # for dta string ref the threshold is 2045, so we need to make the string longer
        df_longstr.iloc[0,0] = df_longstr.iloc[0,0]*3
        pyreadstat.write_dta(self.df_longstr, path)
        df, meta = pyreadstat.read_dta(path)
        self.assertTrue(df.equals(df_longstr.reset_index(drop=True)))
        
        
    def test_sas7bdat_file_label_linux(self):
        "testing file label for file produced on linux"
        path = os.path.join(self.basic_data_folder, "test_file_label_linux.sas7bdat")
        df, meta = pyreadstat.read_sas7bdat(path)
        self.assertEqual(meta.file_label, "mytest label")
        self.assertEqual(meta.table_name, "TEST_DATA")

    def test_sas7bdat_extra_date_formats(self):
        "testing extra date format argument"
        path = os.path.join(self.basic_data_folder, "date_test.sas7bdat")
        df, meta = pyreadstat.read_sas7bdat(path, extra_date_formats=["MMYY", "YEAR"])
        self.assertEqual(df['yr'].iloc[0], date(2023,1,1))
        self.assertEqual(df['dtc4'].iloc[0], date(2023,7,1))

    def test_sas7bdat_file_label_windows(self):
        "testing file label for file produced on windows"
        path = os.path.join(self.basic_data_folder, "test_file_label_win.sas7bdat")
        df, meta = pyreadstat.read_sas7bdat(path)
        self.assertEqual(meta.file_label, "mytest label")
        self.assertEqual(meta.table_name, "TEST_DATA")

    def test_sav_write_variable_formats(self):
        "testing variable formats for SAV files"
        path = os.path.join(self.write_folder, "variable_format.sav")
        df = pd.DataFrame({'restricted':[1023, 10], 'integer':[1,2]})
        formats = {'restricted':'restricted_integer', 'integer':'integer'}
        pyreadstat.write_sav(df, path, variable_format=formats)
        df2, meta2 = pyreadstat.read_sav(path)
        self.assertEqual(meta2.original_variable_types['restricted'], "N4")
        self.assertEqual(meta2.original_variable_types['integer'], "F1.0")

    def test_sav_ordered_categories(self):
        path = os.path.join(self.basic_data_folder, "ordered_category.sav")
        df, meta = pyreadstat.read_sav(path, apply_value_formats=True, formats_as_ordered_category=True)
        self.assertTrue(df.Col1.cat.ordered)
        self.assertListEqual(list(df.Col1.cat.categories), ['high', 'low', 'medium'])

    def test_sav_pathlib(self):
        if is_pathlib_available:
            path = Path(self.basic_data_folder).joinpath("sample.sav")
            df, meta = pyreadstat.read_sav(path)
            self.assertTrue(df.equals(self.df_pandas))

    def test_sav_write_pathlib(self):
        if is_pathlib_available:
            file_label = "basic write"
            file_note = "These are some notes"
            col_labels = ["mychar label","mynum label", "mydate label", "dtime label", None, "myord label", "mytime label"]
            variable_value_labels = {'mylabl': {1.0: 'Male', 2.0: 'Female'}, 'myord': {1.0: 'low', 2.0: 'medium', 3.0: 'high'}}
            missing_ranges = {'mychar':['a'], 'myord': [{'hi':2, 'lo':1}]}
            #variable_alignment = {'mychar':"center", 'myord':"right"}
            variable_display_width = {'mychar':20}
            variable_measure = {"mychar": "nominal"}
            path = Path(self.write_folder).joinpath('pathlib_write.sav')
            pyreadstat.write_sav(self.df_pandas, path, file_label=file_label, column_labels=col_labels, note=file_note, 
                variable_value_labels=variable_value_labels, missing_ranges=missing_ranges, variable_display_width=variable_display_width,
                variable_measure=variable_measure) #, variable_alignment=variable_alignment)
            df, meta = pyreadstat.read_sav(path, user_missing=True)
            self.assertTrue(df.equals(self.df_pandas))
            self.assertEqual(meta.file_label, file_label)
            self.assertListEqual(meta.column_labels, col_labels)
            self.assertEqual(meta.notes[0], file_note)
            self.assertDictEqual(meta.variable_value_labels, variable_value_labels)
            self.assertEqual(meta.variable_display_width['mychar'], variable_display_width['mychar'])
            #self.assertDictEqual(meta.variable_alignment, variable_alignment)
            self.assertEqual(meta.variable_measure["mychar"], variable_measure["mychar"])

    def test_sav_write_dictlabels(self):
        col_names = ["mychar", "mynum", "mydate", "dtime", "mylabl", "myord", "mytime"]
        col_labels = ["mychar label","mynum label", "mydate label", "dtime label", None, "myord label", "mytime label"]
        col_lab_dict = {k:v for k,v in zip(col_names, col_labels) if v}
        variable_value_labels = {'mylabl': {1.0: 'Male', 2.0: 'Female'}, 'myord': {1.0: 'low', 2.0: 'medium', 3.0: 'high'}}
        missing_ranges = {'mychar':['a'], 'myord': [{'hi':2, 'lo':1}]}
        path = os.path.join(self.write_folder, "dictlabel_write.sav")
        pyreadstat.write_sav(self.df_pandas, path, column_labels=col_lab_dict)
        df, meta = pyreadstat.read_sav(path, user_missing=True)
        self.assertTrue(df.equals(self.df_pandas))
        self.assertListEqual(meta.column_labels, col_labels)
    
    def test_dta_write_single_value_user_missing(self):
        df = pd.DataFrame({"var": ["a", "a", "a", "a"]})
        missing_user_values = {"var": ["a"]}
        path = os.path.join(self.write_folder, "singleusermissing.dta")
        pyreadstat.write_dta(df=df, dst_path=path, missing_user_values=missing_user_values,version=12) 
        df2, meta2 = pyreadstat.read_dta(path, user_missing=True)
        self.assertTrue(df.equals(df2))

    def test_dta_write_only_missing_and_user_missing(self):
        df = pd.DataFrame({"var": [np.nan, "a", "b"]})
        path = os.path.join(self.write_folder, "onlymissing_and_usermissing.dta")
        variable_value_labels={"var": {1: "Val 1", 2: "Val 2", 3: "Val 3", "a": "Missing A", "b": "Missing B", } }
        missing_user_values={"var": ["a", "b"]}
        pyreadstat.write_dta(df, path, variable_value_labels=variable_value_labels, missing_user_values=missing_user_values,version=12)
        df2, meta2 = pyreadstat.read_dta(path, user_missing=True, )
        self.assertTrue(df.equals(df2))

    def test_sav_outputformat_dict(self):
        df, meta = pyreadstat.read_sav(os.path.join(self.basic_data_folder, "sample.sav"), output_format='dict')
        self.assertTrue(meta.number_columns == len(self.df_pandas.columns))
        self.assertTrue(meta.number_rows == len(self.df_pandas))
        self.assertTrue(len(meta.notes)>0)
        self.assertTrue(meta.variable_display_width["mychar"]==9)
        self.assertTrue(meta.variable_storage_width["mychar"] == 8)
        self.assertTrue(meta.variable_measure["mychar"]=="nominal")
        self.assertTrue(meta.readstat_variable_types["mychar"]=="string")
        self.assertTrue(meta.readstat_variable_types["myord"]=="double")
        padic = self.df_pandas.to_dict(orient='list')
        #import pdb;pdb.set_trace()
        for colname, data in df.items():
            curdfcol = df[colname]
            for indx, val in enumerate(data):
                if pd.isna(val) and pd.isna(curdfcol[indx]):
                    continue
                self.assertTrue(val==curdfcol[indx])

    def test_sav_write_rowcompression(self):
        file_label = "row compression write"
        file_note = "These are some notes"
        col_labels = ["mychar label","mynum label", "mydate label", "dtime label", None, "myord label", "mytime label"]
        variable_value_labels = {'mylabl': {1.0: 'Male', 2.0: 'Female'}, 'myord': {1.0: 'low', 2.0: 'medium', 3.0: 'high'}}
        missing_ranges = {'mychar':['a'], 'myord': [{'hi':2, 'lo':1}]}
        #variable_alignment = {'mychar':"center", 'myord':"right"}
        variable_display_width = {'mychar':20}
        variable_measure = {"mychar": "nominal"}
        path = os.path.join(self.write_folder, "rowcompression_write.sav")
        pyreadstat.write_sav(self.df_pandas, path, file_label=file_label, column_labels=col_labels, note=file_note, 
            variable_value_labels=variable_value_labels, missing_ranges=missing_ranges, variable_display_width=variable_display_width,
            variable_measure=variable_measure, row_compress=True) #, variable_alignment=variable_alignment)
        df, meta = pyreadstat.read_sav(path, user_missing=True)
        self.assertTrue(df.equals(self.df_pandas))
        self.assertEqual(meta.file_label, file_label)
        self.assertListEqual(meta.column_labels, col_labels)
        self.assertEqual(meta.notes[0], file_note)
        self.assertDictEqual(meta.variable_value_labels, variable_value_labels)
        self.assertEqual(meta.variable_display_width['mychar'], variable_display_width['mychar'])
        #self.assertDictEqual(meta.variable_alignment, variable_alignment)
        self.assertEqual(meta.variable_measure["mychar"], variable_measure["mychar"])

if __name__ == '__main__':

    import sys

    if "--inplace" in sys.argv:

        script_folder = os.path.split(os.path.split(os.path.realpath(__file__))[0])[0]
        sys.path.insert(0, script_folder)
        sys.argv.remove('--inplace')

    import pyreadstat

    print("package location:", pyreadstat.__file__)

    unittest.main()
