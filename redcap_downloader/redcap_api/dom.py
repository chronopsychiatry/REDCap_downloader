import logging
import pandas as pd

from ..data_cleaning.helpers import drop_empty_columns
from ..storage.path_resolver import PathResolver


class DataMixin:
    """
    Mixin class providing data handling methods for REDCap data objects.

    Attributes:
        data (pd.DataFrame): The data.
        raw_data (pd.DataFrame): The raw data.

    Methods:
        split(by): Splits the DataFrame into a list of DataFrames based on the specified columns.
    """
    def __init__(self):
        self._logger = logging.getLogger(self.__class__.__name__)

    def split(self, by: list[str]) -> list[pd.DataFrame]:
        """Split the DataFrame into a list of DataFrames based on the specified columns.

        Args:
            by (list): List of columns to split the DataFrame by.

        Returns:
            List[pd.DataFrame]: List of DataFrames, one for each unique group defined by 'by'.
        """
        return [group.copy() for _, group in self.data.groupby(by)]


class Report(DataMixin):
    """
    Represents a report containing questionnaire answers, exported from REDCap.

    Attributes:
        raw_data (pd.DataFrame): The raw report data (will not get affected by data cleaning operations).
        data (pd.DataFrame): The report data (will be affected by data cleaning operations).

    Methods:
        save_cleaned_data(paths): Saves cleaned report data to disk.
    """
    def __init__(self, report_data: pd.DataFrame):
        super().__init__()
        self.data = report_data
        self.raw_data = report_data
        self._logger.info(f'Initialised report for {len(self.data.study_id.unique())} subjects.')
        self._logger.info(f'Number of questionnaires: \
                          {self.data.groupby("redcap_event_name").size().sort_values(ascending=False)}')
        self._logger.debug(f'Subject list: {self.data.study_id.unique()}')

    def __str__(self):
        return f"Report with {self.data.shape[0]} entries and {self.data.shape[1]} columns"

    def save_cleaned_data(self, paths: PathResolver, by: list[str] = None, remove_empty_columns: bool = True):
        """
        Save cleaned questionnaire report data after splitting it by the specified columns.

        Args:
            paths (PathResolver): PathResolver instance to get the save paths.
            by (list): List of columns to split the DataFrame by.
            remove_empty_columns (bool): Whether to remove empty columns before saving.

        Returns:
            None
        """
        df_list = [self.data] if by is None else self.split(by)
        if remove_empty_columns:
            df_list = [drop_empty_columns(df) for df in df_list]

        for df in df_list:
            self._logger.debug(f'Saving report with shape: {df.shape}')
            file_path = paths.get_subject_questionnaire(subject_id=df.participant_id.iloc[0],
                                                        event_name=df.output_form.iloc[0])
            df.drop(columns=['output_form']).to_csv(file_path, index=False)
            self._logger.debug(f'Saved cleaned report data to {file_path}')

    def save_raw_data(self, paths: PathResolver):
        """
        Save raw data to a specified path.

        Args:
            raw_data (pd.DataFrame): DataFrame containing the raw data.
            paths (PathResolver): PathResolver instance to get the save paths.

        Returns:
            None
        """
        self.raw_data.to_csv(paths.get_raw_report_file(), index=False)
        self._logger.info(f'Saved raw data to {paths.get_raw_report_file()}')


class Variables(DataMixin):
    """
    Represents a set of variables from the questionnaires of a REDCap project.

    Attributes:
        raw_data (pd.DataFrame): The raw variables data (will not get affected by data cleaning operations).
        data (pd.DataFrame): The variables data (will be affected by data cleaning operations).

    Methods:
        save_cleaned_data(paths): Saves cleaned variables data to disk.
    """
    def __init__(self, variables_data: pd.DataFrame):
        super().__init__()
        self.raw_data = variables_data
        self.data = variables_data
        self._logger.info(f'Initialised list of {len(self.data)} variables.')

    def __str__(self):
        return f"Variables with {self.raw_data.shape[0]} entries"

    def save_cleaned_data(self, paths: PathResolver, by: list[str] = None, remove_empty_columns: bool = True):
        """
        Save cleaned variables data.

        Args:
            paths (PathResolver): PathResolver instance to get the save paths.
            by (list): List of columns to split the DataFrame by.
            remove_empty_columns (bool): Whether to remove empty columns before saving.

        Returns:
            None
        """
        df_list = [self.data] if by is None else self.split(by)
        if remove_empty_columns:
            df_list = [drop_empty_columns(df) for df in df_list]

        for df in df_list:
            self._logger.debug(f'Saving {len(df)} variables for form: {df.output_form.iloc[0]}')
            file_path = paths.get_variables_file(form_name=df.output_form.iloc[0])
            df.drop(columns=['output_form']).to_csv(file_path, index=False)
            self._logger.debug(f'Saved cleaned variables data to {file_path}')

    def save_raw_data(self, paths: PathResolver):
        """
        Save raw data to a specified path.

        Args:
            raw_data (pd.DataFrame): DataFrame containing the raw data.
            paths (PathResolver): PathResolver instance to get the save paths.

        Returns:
            None
        """
        self.raw_data.to_csv(paths.get_raw_variables_file(), index=False)
        self._logger.info(f'Saved raw data to {paths.get_raw_variables_file()}')
