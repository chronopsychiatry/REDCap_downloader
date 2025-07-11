import logging
import os

import pkg_resources


def main():
    # Configure the logger
    if not os.path.exists(properties.download_folder):
        os.makedirs(properties.download_folder)
    logging.basicConfig(
        level=logging.INFO,  # Set the log level
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Log format
        handlers=[
            logging.FileHandler(os.path.join(properties.download_folder, "download.log")),  # Log to a file
            logging.StreamHandler()  # Log to console
        ]
    )

    logger = logging.getLogger('main')
    version = pkg_resources.require("redcap_downloader")[0].version
    logger.info(f'Running redcap_downloader version {version}')


if __name__ == '__main__':
    main()
