import configparser
import os


class Properties():
    """
    Represents the properties of the REDCap downloader application, read from a configuration file.

    Attributes:
        redcap_token_file (str): Path to the file containing the REDCap API token.
        download_folder (str): Directory where downloaded data will be stored.
        report_id (int): ID of the report to fetch from REDCap.
        log_level (str): Logging level for the application.
    """
    def __init__(self,
                 redcap_token_file=None,
                 download_folder='../downloaded_data',
                 report_id=None,
                 log_level='INFO'
                 ):

        self.redcap_token_file = redcap_token_file or './redcap_token.txt'
        self.download_folder = download_folder or '../downloaded_data'
        self.report_id = report_id
        self.log_level = log_level
        with open(redcap_token_file, 'r') as f:
            self.redcap_token = f.readline().strip(' \t\n\r')

    def __str__(self):
        return f"Properties(redcap_token_file={self.redcap_token_file}, " \
               f"download_folder={self.download_folder}, report_id={self.report_id}, " \
               f"log_level={self.log_level})"


def load_application_properties(file_path='./REDCap_downloader.properties'):
    """
    Load application properties from a configuration file.

    Args:
        file_path (str): Path to the properties file.

    Returns:
        Properties: An instance of the Properties class containing the loaded properties.

    Raises:
        ValueError: If the properties file does not exist or is not readable.
    """
    config = configparser.ConfigParser()
    if os.path.exists(file_path):
        config.read(file_path)
    else:
        raise ValueError(f"Properties file not found: {file_path}.")
    return Properties(
        redcap_token_file=config['DEFAULT'].get('token-file', None),
        download_folder=config['DEFAULT'].get('download-dir', None),
        report_id=config['DEFAULT'].get('report-id', None),
        log_level=config['DEFAULT'].get('log-level', 'INFO')
    )
