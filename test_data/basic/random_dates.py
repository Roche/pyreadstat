"""
CAREFUL WITH THIS SCRIPT:
IT CAN DESTROY THE TESTS

It is mean to tbe run manually line by line !!!!

Purpose: generate a csv with random dates.
That has to be brought into SAS manually.

"""

import os
import random
from datetime import datetime

import pandas as pd

# Generate dates

basic_data_folder = "/home/bceuser/fajardoo/PyCharm_Projects/pyreadstat/test_data/basic"

max = 8e9
min = max * -1

dates = list()

for x in range(50):

    rand = int(random.uniform(min, max))
    dt = datetime.utcfromtimestamp(rand)
    dates.append(pd.to_datetime(dt))

df = pd.DataFrame.from_dict({"date":dates, "dtime":dates, "time":dates})
df["date"] = df["date"].apply(lambda x: x.date())
df["time"] = df["time"].apply(lambda x: x.time())

# save as csv
date_format = "%Y-%m-%dT%H:%M:%S.%f"
df.to_csv(os.path.join(basic_data_folder, "dates.csv"), index=False, date_format=date_format)

# #
#
# Now you import into SAS to generate the dates.sas7bdat

##
# Some manual testing
csv = os.path.join(basic_data_folder, "dates.csv")
df2 = pd.read_csv(csv)
df2["date"] = pd.to_datetime(df2["date"])
df2["dtime"] = pd.to_datetime(df2["dtime"])
df2["time"] = pd.to_datetime(df2["time"])
df2["time"] = df2["time"].apply(lambda x: x.time())

df3 = df2.copy()
df3["date"] = df3["date"].apply(lambda x: x.date())
df3["time"] = df3["time"].apply(lambda x: x.time())


import pyreadstat
sas_file = os.path.join(basic_data_folder, "dates.sas7bdat")
df_sas,meta = pyreadstat.read_sas7bdat(sas_file)
df_sas.equals(df3)

df_sas,meta = pyreadstat.read_sas7bdat(sas_file, dates_as_pandas_datetime=True)
df_sas.equals(df2)


for col in df2.columns:
    if not df2[col].equals(df_sas[col]):
        for indx, (pa, sas) in enumerate(zip(df2[col], df_sas[col])):
            if pa != sas:
                print(indx, pa, sas)