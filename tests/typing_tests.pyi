# Run with `mypy tests/typing_tests.py`

import io
from pathlib import Path
from typing import reveal_type

import numpy as np
import pandas as pd
import polars as pl

from pyreadstat import *

def test_read_sav_default() -> None:
    df: pd.DataFrame | pl.DataFrame | dict[str, np.ndarray]

    df, meta = read_sav("file.sav")
    reveal_type(df)  # pandas.core.frame.DataFrame
    reveal_type(meta)  # metadata_container

    df, meta = read_sav("file.sav", output_format="pandas")
    reveal_type(df)  # pandas.core.frame.DataFrame

    df, meta = read_sav("file.sav", output_format="polars")
    reveal_type(df)  # polars.dataframe.frame.DataFrame

    df, meta = read_sav("file.sav", output_format="dict")
    reveal_type(df)  # dict[str, ndarray]

    buffer = io.BytesIO()
    df, meta = read_sav(buffer)

def test_read_dta_types() -> None:
    df: pd.DataFrame | pl.DataFrame | dict[str, np.ndarray]

    df, meta = read_dta("file.dta")
    reveal_type(df)  # pandas.core.frame.DataFrame
    reveal_type(meta)  # metadata_container

    df, meta = read_dta("file.dta", output_format="pandas")
    reveal_type(df)  # pandas.core.frame.DataFrame

    df, meta = read_dta("file.dta", output_format="polars")
    reveal_type(df)  # polars.dataframe.frame.DataFrame

    df, meta = read_dta("file.dta", output_format="dict")
    reveal_type(df)  # dict[str, ndarray]

    buffer = io.BytesIO()
    df, meta = read_dta(buffer)

def test_read_por_types() -> None:
    df: pd.DataFrame | pl.DataFrame | dict[str, np.ndarray]

    df, meta = read_por("file.por")
    reveal_type(df)  # pandas.core.frame.DataFrame
    reveal_type(meta)  # metadata_container

    df, meta = read_por("file.por", output_format="pandas")
    reveal_type(df)  # pandas.core.frame.DataFrame

    df, meta = read_por("file.por", output_format="polars")
    reveal_type(df)  # polars.dataframe.frame.DataFrame

    df, meta = read_por("file.por", output_format="dict")
    reveal_type(df)  # dict[str, ndarray]

    buffer = io.BytesIO()
    df, meta = read_por(buffer)

def test_read_sas7bdat_types() -> None:
    df: pd.DataFrame | pl.DataFrame | dict[str, np.ndarray]

    df, meta = read_sas7bdat("file.sas7bdat")
    reveal_type(df)  # pandas.core.frame.DataFrame
    reveal_type(meta)  # metadata_container

    df, meta = read_sas7bdat("file.sas7bdat", output_format="pandas")
    reveal_type(df)  # pandas.core.frame.DataFrame

    df, meta = read_sas7bdat("file.sas7bdat", output_format="polars")
    reveal_type(df)  # polars.dataframe.frame.DataFrame

    df, meta = read_sas7bdat("file.sas7bdat", output_format="dict")
    reveal_type(df)  # dict[str, ndarray]

    buffer = io.BytesIO()
    df, meta = read_sas7bdat(buffer)

def test_read_xport_types() -> None:
    df: pd.DataFrame | pl.DataFrame | dict[str, np.ndarray]

    df, meta = read_xport("file.xpt")
    reveal_type(df)  # pandas.core.frame.DataFrame
    reveal_type(meta)  # metadata_container

    df, meta = read_xport("file.xpt", output_format="pandas")
    reveal_type(df)  # pandas.core.frame.DataFrame

    df, meta = read_xport("file.xpt", output_format="polars")
    reveal_type(df)  # polars.dataframe.frame.DataFrame

    df, meta = read_xport("file.xpt", output_format="dict")
    reveal_type(df)  # dict[str, ndarray]

    buffer = io.BytesIO()
    df, meta = read_xport(buffer)

def test_read_sas7bcat_types() -> None:
    df: pd.DataFrame | pl.DataFrame | dict[str, np.ndarray]

    df, meta = read_sas7bcat("file.sas7bcat")
    reveal_type(
        df
    )  # pandas.core.frame.DataFrame | polars.dataframe.frame.DataFrame | dict[str, ndarray]
    reveal_type(meta)  # metadata_container

    df, meta = read_sas7bcat("file.sas7bcat", output_format="pandas")
    reveal_type(df)  # pandas.core.frame.DataFrame

    df, meta = read_sas7bcat("file.sas7bcat", output_format="polars")
    reveal_type(df)  # polars.dataframe.frame.DataFrame

    df, meta = read_sas7bcat("file.sas7bcat", output_format="dict")
    reveal_type(df)  # dict[str, ndarray]

    buffer = io.BytesIO()
    df, meta = read_sas7bcat(buffer)

def test_read_multiprocessing() -> None:
    df: pd.DataFrame | pl.DataFrame
    def noop(a: int, /) -> int:
        return a

    df, meta = read_file_multiprocessing(read_sav, "file.sav", metadataonly=True)
    reveal_type(df)  # pandas.core.frame.DataFrame

    df, meta = read_file_multiprocessing(
        read_sav, "file.sav", metadataonly=True, output_format="polars"
    )
    reveal_type(df)  # polars.dataframe.frame.DataFrame

    read_file_multiprocessing(noop, "file.sav", 1, 1)  # wrong callable, should error

def test_read_file_in_chunks() -> None:
    df: pd.DataFrame | pl.DataFrame
    def noop(a: int, /) -> int:
        return a

    for df, meta in read_file_in_chunks(read_sav, "file.sav", metadataonly=True):
        reveal_type(df)  # pandas.core.frame.DataFrame

    for df, meta in read_file_in_chunks(
        read_sav, "file.sav", metadataonly=True, output_format="polars"
    ):
        reveal_type(df)  # polars.dataframe.frame.DataFrame

    read_file_in_chunks(noop, "file.sav", 1, 1)  # wrong callable, should error

def test_write_sav_types() -> None:
    pandas_df = pd.DataFrame()
    polars_df = pl.DataFrame()
    # Test writing with pandas DataFrame and string path
    write_sav(pandas_df, "file.sav")
    # Test writing with polars DataFrame and string path
    write_sav(polars_df, "file.sav")
    # Test writing with pandas DataFrame and Path object
    write_sav(pandas_df, Path("file.sav"))
    # Test writing with pandas DataFrame and BytesIO buffer
    buffer = io.BytesIO()
    write_sav(pandas_df, buffer)

def test_write_dta_types() -> None:
    pandas_df = pd.DataFrame()
    polars_df = pl.DataFrame()
    # Test writing with pandas DataFrame and string path
    write_dta(pandas_df, "file.dta")
    # Test writing with polars DataFrame and string path
    write_dta(polars_df, "file.dta")
    # Test writing with pandas DataFrame and Path object
    write_dta(pandas_df, Path("file.dta"))
    # Test writing with pandas DataFrame and BytesIO buffer
    buffer = io.BytesIO()
    write_dta(pandas_df, buffer)

def test_write_xport_types() -> None:
    pandas_df = pd.DataFrame()
    polars_df = pl.DataFrame()
    # Test writing with pandas DataFrame and string path
    write_xport(pandas_df, "file.xpt")
    # Test writing with polars DataFrame and string path
    write_xport(polars_df, "file.xpt")
    # Test writing with pandas DataFrame and Path object
    write_xport(pandas_df, Path("file.xpt"))
    # Test writing with pandas DataFrame and BytesIO buffer
    buffer = io.BytesIO()
    write_xport(pandas_df, buffer)

def test_write_por_types() -> None:
    pandas_df = pd.DataFrame()
    polars_df = pl.DataFrame()
    # Test writing with pandas DataFrame and string path
    write_por(pandas_df, "file.por")
    # Test writing with polars DataFrame and string path
    write_por(polars_df, "file.por")
    # Test writing with pandas DataFrame and Path object
    write_por(pandas_df, Path("file.por"))
    # Test writing with pandas DataFrame and BytesIO buffer
    buffer = io.BytesIO()
    write_por(pandas_df, buffer)
