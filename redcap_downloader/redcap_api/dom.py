import logging
import os


class DataMixin:
    def __init__(self):
        self._logger = logging.getLogger(self.__class__.__name__)

    def save_raw_data(self, path):
        """
        Save raw data to a specified path.

        Args:
            data (pd.DataFrame): DataFrame containing the raw data.
            path (str): Path where the raw data will be saved.
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
        """
        if self.list is None:
            self._logger.warning('No cleaned variables data to save.')
        for df in self.list:
            self._logger.debug(f'Saving variables with shape: {df.shape}')
            file_path = os.path.join(paths.get_meta_dir(), f"{df.form_name.iloc[0]}.csv")
            df.to_csv(file_path, index=False)
            self._logger.debug(f'Saved cleaned variables data to {file_path}')
