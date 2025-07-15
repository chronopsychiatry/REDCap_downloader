import logging
import os


class DataMixin:
    """
    Mixin class providing data handling methods for REDCap data objects.

    Attributes:
        raw_data (pd.DataFrame): The raw data.
        cleaned_data (pd.DataFrame): The cleaned data.

    Methods:
        save_raw_data(path): Saves the raw data to a specified path.
        split(by): Splits the DataFrame into a list of DataFrames based on the specified columns.
    """
    def __init__(self):
        self._logger = logging.getLogger(self.__class__.__name__)

    def save_raw_data(self, path):
        """
        Save raw data to a specified path.

        Args:
            data (pd.DataFrame): DataFrame containing the raw data.
            path (str): Path where the raw data will be saved.

        Returns:
            None
        """
        self.raw_data.to_csv(path, index=False)
        self._logger.info(f'Saved raw data to {path}')

    def split(self, by):
        """Split the DataFrame into a list of DataFrames based on the specified columns.

        Args:
            by (list): List of columns to split the DataFrame by.

        Returns:
            List[pd.DataFrame]: List of DataFrames, one for each unique group defined by 'by'.
        """
        if self.cleaned_data is None:
            self._logger.warning('No cleaned data to split.')
            return []
        return [group.copy() for _, group in self.cleaned_data.groupby(by)]


class Report(DataMixin):
    """
    Represents a report containing questionnaire answers, exported from REDCap.

    Attributes:
        raw_data (pd.DataFrame): The raw report data.
        cleaned_data (pd.DataFrame): The cleaned report data.
        list (list): List of DataFrames split by participant and event.

    Methods:
        save_cleaned_data(paths): Saves cleaned report data to disk.
    """
    def __init__(self, report_data):
        super().__init__()
        self.raw_data = report_data
        self.cleaned_data = None
        self.list = None

    def __str__(self):
        return f"Report with {len(self.raw_data)} entries and {len(self.raw_data.columns)} columns"

    def save_cleaned_data(self, paths):
        """
        Save cleaned questionnaire report data.

        Args:
            paths (PathResolver): PathResolver instance to get the save paths.

        Returns:
            None
        """
        if self.list is None:
            self._logger.warning('No cleaned report data to save.')
        for df in self.list:
            self._logger.debug(f'Saving report with shape: {df.shape}')
            file_path = paths.get_subject_questionnaire(subject_id=df.study_id.iloc[0],
                                                        event_name=df.redcap_event_name.iloc[0])
            df.to_csv(file_path, index=False)
            self._logger.debug(f'Saved cleaned report data to {file_path}')


class Variables(DataMixin):
    """
    Represents a set of variables from the questionnaires of a REDCap project.

    Attributes:
        raw_data (pd.DataFrame): The raw variables data.
        cleaned_data (pd.DataFrame): The cleaned variables data.
        list (list): List of DataFrames split by form name.

    Methods:
        save_cleaned_data(paths): Saves cleaned variables data to disk.
    """
    def __init__(self, variables_data):
        super().__init__()
        self.raw_data = variables_data
        self.cleaned_data = None
        self.list = None

    def __str__(self):
        return f"Variables with {len(self.raw_data)} entries"

    def save_cleaned_data(self, paths):
        """
        Save cleaned variables data.

        Args:
            paths (PathResolver): PathResolver instance to get the save paths.

        Returns:
            None
        """
        if self.list is None:
            self._logger.warning('No cleaned variables data to save.')
        for df in self.list:
            self._logger.debug(f'Saving {len(df)} variables for form: {df.form_name.iloc[0]}')
            file_path = os.path.join(paths.get_meta_dir(), f"{df.form_name.iloc[0]}.csv")
            df.to_csv(file_path, index=False)
            self._logger.debug(f'Saved cleaned variables data to {file_path}')
