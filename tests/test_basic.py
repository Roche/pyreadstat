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

import pandas as pd


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

    def setUp(self):

        # set paths
        self._prepare_data()

    def test_sas7bdat(self):

        df, meta = pyreadstat.read_sas7bdat(os.path.join(self.basic_data_folder, "sample.sas7bdat"))
        self.assertTrue(df.equals(self.df_pandas))
        self.assertTrue(meta.number_columns == len(self.df_pandas.columns))
        self.assertTrue(meta.number_rows == len(self.df_pandas))

    def test_sas7bdat_buffer(self):

        buf = open(os.path.join(self.basic_data_folder, "sample.sas7bdat")).read()
        df, _ = pyreadstat.read_sas7bdat(data=buf)
        self.assertTrue(df.equals(self.df_pandas))
        
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

    def test_xport(self):

        df, meta = pyreadstat.read_xport(os.path.join(self.basic_data_folder, "sample.xpt"))
        df.columns = [x.lower() for x in df.columns]
        self.assertTrue(df.equals(self.df_pandas))
        self.assertTrue(meta.number_columns == len(self.df_pandas.columns))
        self.assertTrue(meta.number_rows == len(self.df_pandas))


    def test_xport_buffer(self):

        buf = open(os.path.join(self.basic_data_folder, "sample.xpt")).read()
        df, _ = pyreadstat.read_xport(data=buf)
        df.columns = [x.lower() for x in df.columns]
        self.assertTrue(df.equals(self.df_pandas))

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

    def test_dta(self):

        # discard dtime and arrange time
        df, meta = pyreadstat.read_dta(os.path.join(self.basic_data_folder, "sample.dta"))
        df_pandas_dta = self.df_pandas.drop(labels="dtime", axis=1)
        df_dta = df.drop(labels="dtime", axis=1)
        df_dta["mytime"] = [datetime.strptime(x, '%H:%M:%S').time() if x else float('nan') for x in df_dta["mytime"]]
        self.assertTrue(df_dta.equals(df_pandas_dta))
        self.assertTrue(meta.number_columns - 1 == len(df_pandas_dta.columns))
        self.assertTrue(meta.number_rows == len(df_pandas_dta))

    def test_dta_buffer(self):

        buf = open(os.path.join(self.basic_data_folder, "sample.dta")).read()
        df, _ = pyreadstat.read_dta(data=buf)
        df_pandas_dta = self.df_pandas.drop(labels="dtime", axis=1)
        df_dta = df.drop(labels="dtime", axis=1)
        df_dta["mytime"] = [datetime.strptime(x, '%H:%M:%S').time() if x else float('nan') for x in df_dta["mytime"]]
        self.assertTrue(df_dta.equals(df_pandas_dta))

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
        self.assertTrue(df.equals(self.df_usecols))
        self.assertTrue(meta.number_columns == len(self.usecols))
        self.assertTrue(meta.column_names == self.usecols)

    def test_sav(self):

        df, meta = pyreadstat.read_sav(os.path.join(self.basic_data_folder, "sample.sav"))
        self.assertTrue(df.equals(self.df_pandas))
        self.assertTrue(meta.number_columns == len(self.df_pandas.columns))
        self.assertTrue(meta.number_rows == len(self.df_pandas))
        self.assertTrue(len(meta.notes)>0)
        self.assertTrue(meta.variable_display_width["mychar"]==9)
        self.assertTrue(meta.variable_storage_width["mychar"] == 8)
        self.assertTrue(meta.variable_measure["mychar"]=="nominal")
    
    def test_sav_buffer(self):

        buf = open(os.path.join(self.basic_data_folder, "sample.sav")).read()
        df, _ = pyreadstat.read_sav(data=buf)
        self.assertTrue(df.equals(self.df_pandas))

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

    def test_zsav(self):

        df, meta = pyreadstat.read_sav(os.path.join(self.basic_data_folder, "sample.zsav"))
        self.assertTrue(df.equals(self.df_pandas))
        self.assertTrue(meta.number_columns == len(self.df_pandas.columns))
        self.assertTrue(meta.number_rows == len(self.df_pandas))
        self.assertTrue(len(meta.notes) > 0)
    
    def test_zsav_buffer(self):

        buf = open(os.path.join(self.basic_data_folder, "sample.zsav")).read()
        df, _ = pyreadstat.read_sav("sample.zsav", data=buf)
        self.assertTrue(df.equals(self.df_pandas))

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
        #df.columns = self.df_pandas_formatted.columns
        self.assertTrue(df.equals(self.df_pandas_formatted))
        self.assertTrue(meta.number_columns == len(self.df_pandas_formatted.columns))
        self.assertTrue(meta.number_rows == len(self.df_pandas_formatted))
        self.assertTrue(len(meta.notes) > 0)

    def test_zsav_usecols(self):
        df, meta = pyreadstat.read_sav(os.path.join(self.basic_data_folder, "sample.zsav"), usecols=self.usecols)
        self.assertTrue(df.equals(self.df_usecols))
        self.assertTrue(meta.number_columns == len(self.usecols))
        self.assertTrue(meta.column_names == self.usecols)

    def test_por(self):

        df, meta = pyreadstat.read_por(os.path.join(self.basic_data_folder, "sample.por"))
        df_pandas_por = self.df_pandas[["mychar", "mynum"]]
        df.columns = [x.lower() for x in df.columns]
        #df.columns = df_pandas_por.columns
        self.assertTrue(df.equals(df_pandas_por))
        self.assertTrue(meta.number_columns == len(df_pandas_por.columns))
        self.assertTrue(meta.number_rows == len(df_pandas_por))
        self.assertTrue(len(meta.notes) > 0)

    def test_por_buffer(self):

        buf = open(os.path.join(self.basic_data_folder, "sample.por")).read()
        df, _ = pyreadstat.read_por(data=buf)
        df_pandas_por = self.df_pandas[["mychar", "mynum"]]
        df.columns = [x.lower() for x in df.columns]
        self.assertTrue(df.equals(df_pandas_por))

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

    def test_sas_catalog_win(self):

        dat = os.path.join(self.catalog_data_folder, "test_data_win.sas7bdat")
        cat = os.path.join(self.catalog_data_folder, "test_formats_win.sas7bcat")
        df, meta = pyreadstat.read_sas7bdat(dat, catalog_file=cat)
        self.assertTrue(df.equals(self.df_sas_format))

    def test_sas_catalog_win_buffer(self):

        dat = open(os.path.join(self.catalog_data_folder, "test_data_win.sas7bdat")).read()
        cat = open(os.path.join(self.catalog_data_folder, "test_formats_win.sas7bcat")).read()
        df, _ = pyreadstat.read_sas7bdat(data=dat, catalog_data=cat)
        self.assertTrue(df.equals(self.df_sas_format))

    def test_sas_dates(self):

        sas_file = os.path.join(self.basic_data_folder, "dates.sas7bdat")
        df_sas, meta = pyreadstat.read_sas7bdat(sas_file)
        self.assertTrue(df_sas.equals(self.df_sas_dates))

    def test_sas_dates_as_pandas(self):

        sas_file = os.path.join(self.basic_data_folder, "dates.sas7bdat")
        df_sas, meta = pyreadstat.read_sas7bdat(sas_file, dates_as_pandas_datetime=True)
        self.assertTrue(df_sas.equals(self.df_sas_dates_as_pandas))


if __name__ == '__main__':

    import sys

    if "--inplace" in sys.argv:

        script_folder = os.path.split(os.path.split(os.path.realpath(__file__))[0])[0]
        sys.path.insert(0, script_folder)
        sys.argv.remove('--inplace')

    import pyreadstat

    print("package location:", pyreadstat.__file__)

    unittest.main()
