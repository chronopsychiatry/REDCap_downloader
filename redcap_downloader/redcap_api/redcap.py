import requests
import pandas as pd
from io import StringIO
import logging

from redcap_downloader.redcap_api.dom import Variables, Report


class REDCap:
    """
    Represents a connection to a REDCap project.

    Attributes:
        token (str): API token for the REDCap project.
        base_url (str): Base URL for the REDCap API.
        report_id (int): ID of the report to fetch.

    Methods:
        get_questionnaire_variables(): Fetches the list of questionnaire variables from the REDCap API.
        get_questionnaire_report(): Fetches the questionnaire answers from the REDCap API.
    """
    def __init__(self, properties):
        self._logger = logging.getLogger('REDCap')
        self.token = properties.redcap_token
        self.base_url = 'https://redcap.usher.ed.ac.uk/api/'
        self.report_id = properties.report_id
        self.properties = properties

    def get_questionnaire_variables(self):
        """
        Fetch the list of questionnaire variables from the REDCap API.

        Args:
            None

        Returns:
            Variables: Variables instance containing the raw data.
        """
        data = {
            'token': self.token,
            'content': 'metadata',
            'format': 'csv',
            'returnFormat': 'json',
            'forms[0]': 'participant_information',
            'forms[1]': 'screening',
            'forms[2]': 'baseline_researcher_cb',
            'forms[3]': 'baseline_participant_questionnaire',
            'forms[4]': 'postbaseline_researcher_admin',
            'forms[5]': 'm_followup_researcher_questionnaire',
            'forms[6]': 'm_followup_participant_questionnaire',
            'forms[7]': 'm_followup_researcher_questionnaire_e70e',
            'forms[8]': 'm_followup_participant_questionnaire_6517',
            'forms[9]': 'm_followup_researcher_questionnaire_df3a',
            'forms[10]': 'm_followup_participant_questionnaire_13e1'
        }
        r = requests.post(self.base_url, data=data)
        if r.status_code != 200:
            self._logger.error(f"Failed to fetch variable dictionary: {r.text}")
            raise Exception(f"HTTP Error: {r.status_code}")
        self._logger.info('Accessing variable dictionary through the REDCap API.')
        return Variables(pd.read_csv(StringIO(r.text)))

    def get_questionnaire_report(self):
        """
        Fetch the questionnaire answers from the REDCap API.

        Args:
            None
        
        Returns:
            Report: Report instance containing the raw data.
        """
        data = {
            'token': self.token,
            'content': 'report',
            'format': 'csv',
            'report_id': self.report_id,
            'csvDelimiter': '',
            'rawOrLabel': 'raw',
            'rawOrLabelHeaders': 'raw',
            'exportCheckboxLabel': 'true',
            'returnFormat': 'json'
        }

        r = requests.post(self.base_url, data=data)
        if r.status_code != 200:
            self._logger.error(f"Failed to fetch report: {r.text}")
            raise Exception(f"HTTP Error: {r.status_code}")
        self._logger.info(f'Accessing report {self.report_id} through the REDCap API.')
        return Report(pd.read_csv(StringIO(r.text)))
