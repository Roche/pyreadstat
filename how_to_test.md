# How to test pyreadstat

## Dependencies for testing

Additional dependencies for testing can be installed with:

```shell
pip install --group dev --group test
```

## Running tests

If you have installed pyreadstat on your environment, enter this folder and do:

```shell
python3 tests/test_basic.py
python3 tests/test_narwhalified.py --backend=pandas
python3 tests/test_narwhalified.py --backend=polars
python3 tests/test_http_integration.py
```

If you have built in place, do:

```shell
python3 tests/test_basic.py --inplace
python3 tests/test_narwhalified.py --inplace --backend=pandas
python3 tests/test_narwhalified.py --inplace --backend=polars
python3 tests/test_http_integration.py --inplace
```

Type hint tests can be run with:

```shell
pytest tests/test_typing.yml --mypy-ini-file=tests/test_mypy_setup.ini
```

To run all tests in place, do:

```shell
python tests/test_basic.py --inplace && python tests/test_narwhalified.py --inplace --backend=pandas && python tests/test_narwhalified.py --inplace --backend=polars && python tests/test_http_integration.py --inplace && pytest tests/test_typing.yml --mypy-ini-file=tests/test_mypy_setup.ini
```
