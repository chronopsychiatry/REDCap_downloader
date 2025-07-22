from functools import reduce
import logging
import numpy as np
import pandas as pd

from ..redcap_api.redcap import REDCap, Variables, Report
from ..storage.path_resolver import PathResolver
from .helpers import replace_strings, merge_duplicate_columns
from .replacements import FORM_NAME_REPLACEMENTS, FIELD_NAME_REPLACEMENTS, ARM_NAME_REPLACEMENTS


class DataCleaner:
    """
    Handles the cleaning and saving of questionnaire data from REDCap.

    Attributes:
        redcap (REDCap): Instance of the REDCap API client.
        paths (PathResolver): Instance of PathResolver to manage file paths.

    Methods:
        save_questionnaire_variables(): Cleans and saves questionnaire variables.
        save_questionnaire_reports(): Cleans and saves questionnaire reports.
    """
    def __init__(self, redcap: REDCap, paths: PathResolver):
        self._logger = logging.getLogger('DataCleaner')
        self.redcap = redcap
        self.paths = paths

    def save_questionnaire_variables(self):
        """
        Clean-up and save questionnaire variables from REDCap.

        Args:
            None

        Returns:
            None

        """
        variables = self.redcap.get_questionnaire_variables()
        variables.save_raw_data(paths=self.paths)

        variables = self.clean_variables(variables)
        variables.save_cleaned_data(paths=self.paths, by='output_form', remove_empty_columns=True)
        self._logger.info(f'Saved cleaned questionnaire variables to {self.paths.get_meta_dir()}.')

    def save_questionnaire_reports(self):
        """
        Clean-up and save questionnaire reports from REDCap.

        Args:
            None

        Returns:
            None
        """
        reports = self.redcap.get_questionnaire_report()
        reports.save_raw_data(paths=self.paths)

        reports = self.clean_reports(reports)
        reports.save_cleaned_data(self.paths, by=['participant_id', 'output_form'], remove_empty_columns=True)
        self._logger.info(f'Saved cleaned questionnaire reports to {self.paths.get_reports_dir()}.')

    def clean_variables(self, variables: Variables) -> Variables:
        """
        Clean-up the variables DataFrame.

        Args:
            variables (Variables): Variables instance containing raw data.

        Returns:
            Variables: Variables instance with cleaned data added.
        """
        cleaned_var = (variables
                       .data
                       .query('form_name != "participant_information"')
                       .pipe(self.remove_html_tags)
                       .pipe(self.filter_variables_columns)
                       .pipe(self.clean_variables_form_names)
                       )
        variables.data = cleaned_var
        return variables

    def clean_reports(self, reports: Report) -> Report:
        """
        Clean-up the reports DataFrame.

        Args:
            reports (Report): Report instance containing raw data.

        Returns:
            Report: Report instance with cleaned data added.
        """
        cleaned_reports = (reports
                           .data
                           .pipe(self.clean_reports_form_names)
                           .query('redcap_event_name != "initial_contact"')
                           )
        reports.data = cleaned_reports
        return reports

    def clean_variables_form_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Replace form names by human-readable names and merge researcher and participant forms.

        Args:
            df (pd.DataFrame): DataFrame containing variable data.

        Returns:
            pd.DataFrame: DataFrame with cleaned form names.
        """
        return (df
                .assign(
                    form_name=lambda df: replace_strings(df.form_name, FORM_NAME_REPLACEMENTS),
                    field_name=lambda df: replace_strings(df.field_name, FIELD_NAME_REPLACEMENTS),
                    output_form=lambda df: np.where(df.form_name == 'Screening', 'Scre', 'Ques')
                )
                .pipe(merge_duplicate_columns)
                )

    def clean_reports_form_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean-up the form and column names of the reports DataFrame.

        Args:
            df (pd.DataFrame): DataFrame containing report data.

        Returns:
            pd.DataFrame: DataFrame with cleaned form and column names.
        """
        return (df
                .assign(redcap_event_name=lambda df: replace_strings(df.redcap_event_name, ARM_NAME_REPLACEMENTS),
                        output_form=lambda df: np.where(df.redcap_event_name == 'screening', 'Scre', 'Ques')
                        )
                .rename(columns=lambda df: (
                    reduce(lambda s, kv: s.replace(kv[0], kv[1]), FIELD_NAME_REPLACEMENTS.items(), df)
                ))
                .pipe(merge_duplicate_columns)
                )

    def filter_variables_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Remove unnecessary columns from the DataFrame.

        Args:
            df (pd.DataFrame): DataFrame to be processed.

        Returns:
            pd.DataFrame: DataFrame with unnecessary columns removed.
        """
        keep_cols = ['field_name', 'form_name', 'section_header', 'field_type', 'field_label']
        return df[keep_cols].copy()

    def remove_html_tags(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Remove HTML tags from all string cells in a DataFrame.

        Args:
            df (pd.DataFrame): DataFrame to be processed.

        Returns:
            pd.DataFrame: DataFrame with HTML tags removed from string cells.
        """
        return df.copy().assign(
            **df.select_dtypes(include=['object'])
            .replace(to_replace=r'<[^>]+>', value='', regex=True)
        )
