import logging

from redcap_downloader.redcap_api.redcap import REDCap
from redcap_downloader.storage.path_resolver import PathResolver


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
        variables.save_cleaned_data(paths=self.paths, by='form_name', remove_empty_columns=True)
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
        reports.save_cleaned_data(self.paths, by=['study_id', 'redcap_event_name'], remove_empty_columns=True)
        self._logger.info(f'Saved cleaned questionnaire reports to {self.paths.get_reports_dir()}.')

    def clean_variables(self, variables):
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

    def clean_reports(self, reports):
        """
        Clean-up the reports DataFrame.

        Args:
            reports (Report): Report instance containing raw data.

        Returns:
            Report: Report instance with cleaned data added.
        """
        cleaned_reports = (reports
                           .data
                           .assign(redcap_event_name=lambda df:
                                   df.redcap_event_name.str.replace('_arm_1', ''))
                           .query('redcap_event_name != "initial_contact"')
                           )
        reports.data = cleaned_reports
        return reports

    def clean_variables_form_names(self, df):
        """
        Replace form names by human-readable names and merge researcher and participant forms.

        Args:
            df (pd.DataFrame): DataFrame containing variable data.

        Returns:
            pd.DataFrame: DataFrame with cleaned form names.
        """
        return df.assign(
            form_name=lambda x: (
                x.form_name
                .replace('participant_information', 'initial_contact')
                .replace('baseline_researcher_cb', 'baseline')
                .replace('baseline_participant_questionnaire', 'baseline')
                .replace('postbaseline_researcher_admin', 'baseline')
                .replace('m_followup_researcher_questionnaire', '6month_followup')
                .replace('m_followup_participant_questionnaire', '6month_followup')
                .replace('m_followup_researcher_questionnaire_e70e', '12month_followup')
                .replace('m_followup_participant_questionnaire_6517', '12month_followup')
                .replace('m_followup_researcher_questionnaire_df3a', '18month_followup')
                .replace('m_followup_participant_questionnaire_13e1', '18month_followup')
            )
        )

    def filter_variables_columns(self, df):
        """
        Remove unnecessary columns from the DataFrame.

        Args:
            df (pd.DataFrame): DataFrame to be processed.

        Returns:
            pd.DataFrame: DataFrame with unnecessary columns removed.
        """
        keep_cols = ['field_name', 'form_name', 'section_header', 'field_type', 'field_label']
        return df[keep_cols].copy()

    def remove_html_tags(self, df):
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
