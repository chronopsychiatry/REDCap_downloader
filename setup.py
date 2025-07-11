from setuptools import setup, find_packages

setup(
    name='redcap_downloader',
    version='0.0.1',
    description='Download, clean-up and organise data from REDCap',
    long_description_content_type="text/markdown",
    url='https://github.com/chronopsychiatry/REDCap_downloader',
    packages=find_packages(),
    python_requires='>=3.10',
    install_requires=[
        'pandas>=2.3.0',
        'requests>=2.32.0'
    ]
)
