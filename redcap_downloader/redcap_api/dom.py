import logging
import os

from redcap_downloader.data_cleaning.helpers import drop_empty_columns


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

    def split(self, by):
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
    def __init__(self, report_data):
        super().__init__()
        self.data = report_data
        self.raw_data = report_data

    def __str__(self):
        return f"Report with {self.data.shape[0]} entries and {self.data.shape[1]} columns"

    def save_cleaned_data(self, paths, by=None, remove_empty_columns=True):
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
            file_path = paths.get_subject_questionnaire(subject_id=df.study_id.iloc[0],
                                                        event_name=df.redcap_event_name.iloc[0])
            df.to_csv(file_path, index=False)
            self._logger.debug(f'Saved cleaned report data to {file_path}')

    def save_raw_data(self, paths):
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
    def __init__(self, variables_data):
        super().__init__()
        self.raw_data = variables_data
        self.data = variables_data

    def __str__(self):
        return f"Variables with {self.raw_data.shape[0]} entries"

    def save_cleaned_data(self, paths, by=None, remove_empty_columns=True):
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
            self._logger.debug(f'Saving {len(df)} variables for form: {df.form_name.iloc[0]}')
            file_path = os.path.join(paths.get_meta_dir(), f"{df.form_name.iloc[0]}.csv")
            df.to_csv(file_path, index=False)
            self._logger.debug(f'Saved cleaned variables data to {file_path}')

    def save_raw_data(self, paths):
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
