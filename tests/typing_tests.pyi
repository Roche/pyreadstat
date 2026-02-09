# Run with `mypy tests/typing_tests.py`

import io
from pathlib import Path
from typing import reveal_type

import pandas as pd
import polars as pl

from pyreadstat import *

def test_read_sav_default() -> None:
    df, meta = read_sav("file.sav")
    reveal_type(df)  # pandas.core.frame.DataFrame
    reveal_type(meta)  # metadata_container

def test_read_sav_pandas_type() -> None:
    df, meta = read_sav("file.sav", output_format="pandas")
    reveal_type(df)  # pandas.core.frame.DataFrame

def test_read_sav_polars_type() -> None:
    df, meta = read_sav("file.sav", output_format="polars")
    reveal_type(df)  # polars.dataframe.frame.DataFrame

def test_read_sav_dict_type() -> None:
    df, meta = read_sav("file.sav", output_format="dict")
    reveal_type(df)  # dict[str, ndarray]

def test_read_sav_buffer_type() -> None:
    buffer = io.BytesIO()
    df, meta = read_sav(buffer)

def test_write_sav_types() -> None:
    pandas_df = pd.DataFrame()
    polars_df = pl.DataFrame()
    write_sav(pandas_df, "file.sav")
    write_sav(polars_df, "file.sav")
    write_sav(pandas_df, Path("file.sav"))

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
