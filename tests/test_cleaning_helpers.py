import pandas as pd

from redcap_downloader.data_cleaning.helpers import drop_empty_columns


class TestCleaningHelpers:
    def test_drop_empty_columns(self):
        df = pd.DataFrame({
            'A': [1, 2, 3],
            'B': [None, None, None],
            'C': [4, 5, 6]
        })
        result = drop_empty_columns(df)
        expected = pd.DataFrame({
            'A': [1, 2, 3],
            'C': [4, 5, 6]
        })
        pd.testing.assert_frame_equal(result, expected)
