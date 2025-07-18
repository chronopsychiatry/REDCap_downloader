from os.path import join, exists, isdir, abspath
from os import makedirs, listdir
from datetime import datetime
import logging
import sys


class PathResolver:
    """
    Resolves file paths for storing downloaded data.

    Attributes:
        _main_dir (str): Main directory for storing downloaded data.

    Methods:
        set_main_dir(path): Sets the main directory for storing data.
        get_main_dir(): Returns the main directory path.
        get_raw_dir(): Returns the path for raw data storage.
        get_meta_dir(): Returns the path for metadata storage.
        get_reports_dir(): Returns the path for reports storage.
        get_subject_dir(subject_id): Returns the path for a specific subject's data.
        get_raw_variables_file(): Returns the path for raw variables data.
        get_raw_report_file(): Returns the path for raw report data.
        get_variables_file(form_name): Returns the path for a specific form's variables data.
        get_subject_questionnaire(subject_id, event_name): Returns the path for a subject's questionnaire data.
    """
    def __init__(self, path=join('..', 'downloaded_data')):
        self._logger = logging.getLogger('PathsResolver')
        self.timestamp = datetime.now().strftime('%Y%m%d')
        self._main_dir = None
        self.set_main_dir(path)

    def set_main_dir(self, path):
        if not exists(path):
            makedirs(path)
        if not isdir(path):
            raise ValueError(f'Main storage: {path} is not a directory')
        if len(listdir(path)) > 1:
            self._logger.warning(f'Main storage: {path} is not empty.')
            response = input('Continue? (y/n): ').strip().lower()
            if response != 'y':
                self._logger.info('Main storage path is not empty and user chose not to continue. '
                                  'Exiting without downloading data.')
                sys.exit(1)
        self._main_dir = path
        self._logger.info(f'Downloading data to: {abspath(self._main_dir)}')

    def get_main_dir(self):
        return self._main_dir

    def get_raw_dir(self):
        raw_dir = join(self._main_dir, 'raw')
        if not exists(raw_dir):
            makedirs(raw_dir)
        return raw_dir

    def get_meta_dir(self):
        meta_dir = join(self._main_dir, 'meta')
        if not exists(meta_dir):
            makedirs(meta_dir)
        return meta_dir

    def get_reports_dir(self):
        reports_dir = join(self._main_dir, 'reports')
        if not exists(reports_dir):
            makedirs(reports_dir)
        return reports_dir

    def get_subject_dir(self, subject_id):
        subject_dir = join(self.get_reports_dir(), subject_id)
        if not exists(subject_dir):
            makedirs(subject_dir)
        return subject_dir

    def get_raw_variables_file(self):
        return join(self.get_raw_dir(), f'Variables_raw_{self.timestamp}.csv')

    def get_raw_report_file(self):
        return join(self.get_raw_dir(), f'Report_raw_{self.timestamp}.csv')

    def get_variables_file(self, form_name):
        return join(self.get_meta_dir(), f'{form_name}_variables_{self.timestamp}.csv')

    def get_subject_questionnaire(self, subject_id, event_name):
        return join(self.get_subject_dir(subject_id), f'{subject_id}_PROM-{event_name}_{self.timestamp}.csv')
