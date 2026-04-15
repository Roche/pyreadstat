"""Runtime type verification tests for pyreadstat.

Calls read/write functions with real test data and asserts that the actual
return types match the declared type annotations (overloads, metadata fields,
etc.).  This complements the static mypy checks in test_typing.yml.

Run after an in-place build:
    python tests/test_runtime_types.py --inplace

Run after install:
    python tests/test_runtime_types.py
"""

import os
import sys
import tempfile
import types
import unittest
from datetime import datetime
from typing import (
    Any,
    Literal,
    Union,
    get_args,
    get_origin,
    get_type_hints,
)


# ---------------------------------------------------------------------------
# Helper: runtime isinstance check that understands typing generics
# ---------------------------------------------------------------------------

def check_type(value: object, annotation: Any) -> bool:
    """Return True if *value* matches *annotation* at runtime.

    Handles: None, Union/X|Y, Literal, list[X], dict[K,V], tuple[...],
    plain classes, and nested combinations thereof.
    """
    # NoneType
    if annotation is type(None):
        return value is None

    origin = get_origin(annotation)
    args = get_args(annotation)

    # Union / X | Y  (includes Optional)
    if origin is Union or origin is types.UnionType:
        return any(check_type(value, a) for a in args)

    # Literal["pandas", "polars", ...]
    if origin is Literal:
        return value in args

    # list[X]
    if origin is list:
        if not isinstance(value, list):
            return False
        if not args:
            return True
        return all(check_type(item, args[0]) for item in value)

    # dict[K, V]
    if origin is dict:
        if not isinstance(value, dict):
            return False
        if not args:
            return True
        k_type, v_type = args
        return all(
            check_type(k, k_type) and check_type(v, v_type)
            for k, v in value.items()
        )

    # tuple[X, Y, ...]
    if origin is tuple:
        if not isinstance(value, tuple):
            return False
        if not args:
            return True
        if len(args) == 2 and args[1] is Ellipsis:
            return all(check_type(item, args[0]) for item in value)
        if len(value) != len(args):
            return False
        return all(check_type(v, a) for v, a in zip(value, args))

    # Plain class (str, int, datetime, metadata_container, pd.DataFrame, …)
    if isinstance(annotation, type):
        return isinstance(value, annotation)

    # Fallback: unrecognised annotation — accept anything
    return True


# ---------------------------------------------------------------------------
# Test suite
# ---------------------------------------------------------------------------

class TestRuntimeTypes(unittest.TestCase):

    # -- paths ---------------------------------------------------------------

    def setUp(self):
        script_folder = os.path.dirname(os.path.realpath(__file__))
        parent_folder = os.path.split(script_folder)[0]
        data_folder = os.path.join(parent_folder, "test_data")
        basic = os.path.join(data_folder, "basic")
        catalog = os.path.join(data_folder, "sas_catalog")

        self.paths = {
            "read_sav": os.path.join(basic, "sample.sav"),
            "read_dta": os.path.join(basic, "sample.dta"),
            "read_sas7bdat": os.path.join(basic, "sample.sas7bdat"),
            "read_xport": os.path.join(basic, "sample.xpt"),
            "read_por": os.path.join(basic, "sample.por"),
            "read_sas7bcat": os.path.join(catalog, "test_formats_linux.sas7bcat"),
        }

    # -- helpers -------------------------------------------------------------

    def _assert_type(self, value, annotation, msg=""):
        self.assertTrue(
            check_type(value, annotation),
            f"Expected {annotation}, got {type(value)!r}{': ' + msg if msg else ''}",
        )

    # -- 1. Read functions: overloaded return types --------------------------

    def test_read_default_returns_pandas(self):
        """Default call (no output_format) returns (pd.DataFrame, metadata_container)."""
        import pandas as pd
        from pyreadstat import metadata_container

        for func_name, path in self.paths.items():
            func = getattr(pyreadstat, func_name)
            df, meta = func(path)
            self._assert_type(df, pd.DataFrame, f"{func_name} default → df")
            self._assert_type(meta, metadata_container, f"{func_name} default → meta")

    def test_read_output_pandas(self):
        import pandas as pd
        from pyreadstat import metadata_container

        for func_name, path in self.paths.items():
            func = getattr(pyreadstat, func_name)
            df, meta = func(path, output_format="pandas")
            self._assert_type(df, pd.DataFrame, f"{func_name} pandas → df")
            self._assert_type(meta, metadata_container, f"{func_name} pandas → meta")

    def test_read_output_polars(self):
        import polars as pl
        from pyreadstat import metadata_container

        for func_name, path in self.paths.items():
            func = getattr(pyreadstat, func_name)
            df, meta = func(path, output_format="polars")
            self._assert_type(df, pl.DataFrame, f"{func_name} polars → df")
            self._assert_type(meta, metadata_container, f"{func_name} polars → meta")

    def test_read_output_dict(self):
        from pyreadstat import metadata_container

        for func_name, path in self.paths.items():
            func = getattr(pyreadstat, func_name)
            df, meta = func(path, output_format="dict")
            self._assert_type(df, dict, f"{func_name} dict → df")
            # Verify dict shape: str keys, list values
            for k, v in df.items():
                self.assertIsInstance(k, str, f"{func_name} dict key type")
                self.assertIsInstance(v, list, f"{func_name} dict value type")
            self._assert_type(meta, metadata_container, f"{func_name} dict → meta")

    # -- 2. Write functions: return None -------------------------------------

    def test_write_returns_none(self):
        import pandas as pd

        df = pd.DataFrame({"col1": [1, 2], "col2": ["a", "b"]})
        writers = {
            "write_sav": ".sav",
            "write_dta": ".dta",
            "write_xport": ".xpt",
            "write_por": ".por",
        }
        for func_name, ext in writers.items():
            func = getattr(pyreadstat, func_name)
            with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
                tmp_path = tmp.name
            try:
                result = func(df, tmp_path)
                self.assertIsNone(result, f"{func_name} should return None")
            finally:
                os.unlink(tmp_path)

    # -- 3. metadata_container field types -----------------------------------

    def test_metadata_field_types(self):
        """Every field of metadata_container has a value matching its annotation."""
        from pyreadstat.pyclasses import metadata_container

        # Read a file that populates most metadata fields
        df, meta = pyreadstat.read_sav(self.paths["read_sav"])

        hints = get_type_hints(metadata_container, include_extras=True)
        for field_name, expected_type in hints.items():
            value = getattr(meta, field_name)
            self._assert_type(
                value,
                expected_type,
                f"metadata_container.{field_name}",
            )

    # -- 4. set_value_labels / set_catalog_to_sas ----------------------------

    def test_set_value_labels_pandas(self):
        import pandas as pd
        from pyreadstat import set_value_labels

        df, meta = pyreadstat.read_sav(
            self.paths["read_sav"], apply_value_formats=False,
        )
        result = set_value_labels(df, meta)
        self.assertIsInstance(result, pd.DataFrame)

    def test_set_value_labels_polars(self):
        import polars as pl
        from pyreadstat import set_value_labels

        df, meta = pyreadstat.read_sav(
            self.paths["read_sav"],
            apply_value_formats=False,
            output_format="polars",
        )
        result = set_value_labels(df, meta)
        self.assertIsInstance(result, pl.DataFrame)

    def test_set_catalog_to_sas_pandas(self):
        import pandas as pd
        from pyreadstat import set_catalog_to_sas

        sas_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "..", "test_data", "sas_catalog", "test_data_linux.sas7bdat",
        )
        cat_path = self.paths["read_sas7bcat"]
        sas_df, sas_meta = pyreadstat.read_sas7bdat(sas_path)
        _, cat_meta = pyreadstat.read_sas7bcat(cat_path)
        result_df, result_meta = set_catalog_to_sas(sas_df, sas_meta, cat_meta)
        self.assertIsInstance(result_df, pd.DataFrame)
        self.assertIsInstance(result_meta, pyreadstat.metadata_container)

    def test_set_catalog_to_sas_polars(self):
        import polars as pl
        from pyreadstat import set_catalog_to_sas

        sas_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "..", "test_data", "sas_catalog", "test_data_linux.sas7bdat",
        )
        cat_path = self.paths["read_sas7bcat"]
        sas_df, sas_meta = pyreadstat.read_sas7bdat(sas_path, output_format="polars")
        _, cat_meta = pyreadstat.read_sas7bcat(cat_path)
        result_df, result_meta = set_catalog_to_sas(sas_df, sas_meta, cat_meta)
        self.assertIsInstance(result_df, pl.DataFrame)
        self.assertIsInstance(result_meta, pyreadstat.metadata_container)

    # -- 5. read_file_multiprocessing ----------------------------------------

    def test_read_file_multiprocessing_types(self):
        import pandas as pd
        import polars as pl
        from pyreadstat import metadata_container, read_file_multiprocessing, read_sav

        path = self.paths["read_sav"]

        # default
        df, meta = read_file_multiprocessing(read_sav, path, num_processes=2)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertIsInstance(meta, metadata_container)

        # polars
        df, meta = read_file_multiprocessing(
            read_sav, path, num_processes=2, output_format="polars",
        )
        self.assertIsInstance(df, pl.DataFrame)

        # dict
        df, meta = read_file_multiprocessing(
            read_sav, path, num_processes=2, output_format="dict",
        )
        self.assertIsInstance(df, dict)

    # -- 6. read_file_in_chunks ----------------------------------------------

    def test_read_file_in_chunks_types(self):
        import pandas as pd
        import polars as pl
        from pyreadstat import metadata_container, read_file_in_chunks, read_sav

        path = self.paths["read_sav"]

        # default → pandas
        for df, meta in read_file_in_chunks(read_sav, path, chunksize=2):
            self.assertIsInstance(df, pd.DataFrame)
            self.assertIsInstance(meta, metadata_container)
            break  # one chunk is enough

        # polars
        for df, meta in read_file_in_chunks(
            read_sav, path, chunksize=2, output_format="polars",
        ):
            self.assertIsInstance(df, pl.DataFrame)
            break

        # dict
        for df, meta in read_file_in_chunks(
            read_sav, path, chunksize=2, output_format="dict",
        ):
            self.assertIsInstance(df, dict)
            break


# ---------------------------------------------------------------------------

if __name__ == "__main__":

    if "--inplace" in sys.argv:
        script_folder = os.path.split(os.path.split(os.path.realpath(__file__))[0])[0]
        sys.path.insert(0, script_folder)
        sys.argv.remove("--inplace")

    import pyreadstat

    print("package location:", pyreadstat.__file__)

    unittest.main()
