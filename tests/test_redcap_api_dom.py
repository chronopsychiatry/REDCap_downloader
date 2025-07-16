import pandas as pd
import tempfile
import os

from redcap_downloader.redcap_api.dom import Report, Variables, DataMixin
from redcap_downloader.storage.path_resolver import PathResolver


class TestReport:

    test_report = pd.read_csv('./tests/data/test_report.csv')
    test_dir = tempfile.TemporaryDirectory()
    paths = PathResolver(test_dir.name)

    def test_initialization(self):
        report = Report(self.test_report)
        assert isinstance(report, Report)
        assert isinstance(report, DataMixin)
        assert report.raw_data.equals(self.test_report)

    def test_save_cleaned_data(self):
        report = Report(self.test_report)
        report.data = pd.DataFrame({
            'study_id': ['1', '2', '3'],
            'redcap_event_name': ['event1', 'event2', 'event3'],
            'consent_contact': ['1', '1', '1']
        })
        report.save_cleaned_data(self.paths, by=['study_id', 'redcap_event_name'])
        assert os.path.exists(self.paths.get_subject_questionnaire(subject_id='1', event_name='event1'))

    def test_save_raw_data(self):
        report = Report(self.test_report)
        report.save_raw_data(self.paths)
        assert os.path.exists(self.paths.get_raw_report_file())

    def test_split(self):
        report = Report(self.test_report)
        test_list = report.split(by=['study_id', 'redcap_event_name'])
        assert isinstance(test_list, list)
        assert len(test_list) > 0
        for df in test_list:
            assert isinstance(df, pd.DataFrame)
            assert 'study_id' in df.columns
            assert 'redcap_event_name' in df.columns


class TestVariables:

    test_variables = pd.read_csv('./tests/data/test_variables.csv')
    test_dir = tempfile.TemporaryDirectory()
    paths = PathResolver(test_dir.name)

    def test_initialization(self):
        variables = Variables(self.test_variables)
        assert isinstance(variables, Variables)
        assert isinstance(variables, DataMixin)
        assert variables.raw_data.equals(self.test_variables)

    def test_save_cleaned_data(self):
        variables = Variables(self.test_variables)
        variables.data = pd.DataFrame({
            'form_name': ['screening', 'baseline'],
            'field_name': ['field1', 'field2'],
            'empty_column': [None, None]
        })
        variables.save_cleaned_data(self.paths)
        assert os.path.exists(self.paths.get_variables_file(form_name='screening'))

    def test_save_raw_data(self):
        variables = Variables(self.test_variables)
        variables.save_raw_data(self.paths)
        assert os.path.exists(self.paths.get_raw_variables_file())

    def test_split(self):
        variables = Variables(self.test_variables)
        test_list = variables.split(by=['form_name'])
        assert isinstance(test_list, list)
        assert len(test_list) > 0
        for df in test_list:
            assert isinstance(df, pd.DataFrame)
            assert 'form_name' in df.columns
            assert 'field_name' in df.columns
