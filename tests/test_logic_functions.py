import pytest
import unittest
import logging

from main import unzipping, generate_dataframe

# The imports are always relative to the directory where pytest is runned.


class LogicFunctionTests(unittest.TestCase):
    def test_unzipping(self):

        logging.basicConfig(level=logging.DEBUG)
        unzipping()

    def test_df_consistency(self):

        logging.basicConfig(level=logging.DEBUG)
        unzipping()
        df = generate_dataframe()

        # Arbitrary control on final dataframe, i.e. check that at least 50% of films match a wikipedia page
        dict_values = {k: v for k, v in zip(df.columns, df.count().values)}
        assert dict_values["wiki_urls"] / len(df.index) > 0.5
