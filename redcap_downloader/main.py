import logging
import os
import pkg_resources

from redcap_downloader.config.properties import load_application_properties
from redcap_downloader.storage.path_resolver import PathResolver
from redcap_downloader.redcap_api.redcap import REDCap
from redcap_downloader.data_cleaning.data_cleaner import DataCleaner


def main():
    # Load properties
    properties = load_application_properties()

    # Configure the logger
    if not os.path.exists(properties.download_folder):
        os.makedirs(properties.download_folder)
    logging.basicConfig(
        level=logging.DEBUG if properties.log_level == 'DEBUG' else logging.INFO,  # Set the log level
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Log format
        handlers=[
            logging.FileHandler(os.path.join(properties.download_folder, "download.log")),  # Log to a file
            logging.StreamHandler()  # Log to console
        ]
    )

    logger = logging.getLogger('main')
    version = pkg_resources.require("redcap_downloader")[0].version
    logger.info(f'Running redcap_downloader version {version}')

    paths = PathResolver(properties.download_folder)

    redcap = REDCap(properties)

    cleaner = DataCleaner(redcap, paths)

    cleaner.save_questionnaire_variables()
    cleaner.save_questionnaire_reports()


if __name__ == '__main__':
    main()
