# REDCap_downloader

Python script to download, clean-up and organise data from REDCap

## Running the downloader

The package is not uploaded on PyPI for the moment, so it must be installed from source. To do so:

- Clone the github repository
- In a terminal, navigate to the repository
- Install the package with pip: `python pip install .`

Accessing REDCap data requires having an API token. This must be requested through the REDCap platform, and stored in a .txt file on a computer. **Do not** store the token in the cloned github repository, to avoid accidental upload.

Edit the "REDCap_downloader.properties" file (in the cloned repository):

- `token-file`: the path to the text file containing your REDCap API token
- `download-dir`: path to the directory where the REDCap data will be downloaded
- `report-id`: ID of the report to download. For Ambient-BD questionnaire data, use 159
- `log-level`: set to INFO by default. Change to DEBUG if you have an issue with the downloader and want more info on what is happening

Finally, run the following command from the directory that contains the properties file:

```bash
redcap_download
```

## Folder structure

The program will create the following folder structure:

```markdown
├── download.log
├── meta
│   ├── 12month_followup.csv
│   ├── 18month_followup.csv
│   ├── 6month_followup.csv
│   ├── baseline.csv
│   ├── initial_contact.csv
│   └── screening.csv
├── raw
│   ├── Report_raw.csv
│   └── Variables_raw.csv
└── reports
    ├── ABD001
    │   ├── ABD001_baseline.csv
    │   ├── ABD001_initial_contact.csv
    │   └── ABD001_screening.csv
    ├── ABD002
    │   ├── ABD002_baseline.csv
    │   ├── ABD002_initial_contact.csv
    │   └── ABD002_screening.csv
    ├── ABD003
    ...
```

- `download.log`: contains a log of the program run
- `meta`: questionnaire metadata. Contains one .csv file per questionnaire. Each .csv file contains a list of all variables in the questionnaire (as found in the reports), along with a description
- `raw`: raw data as obtained from REDCap, without any cleaning done. There are two file:
  - `Report_raw.csv`: questionnaire results for all participants, and all questionnaires
  - `Variables_raw.csv`: list of variables for all questionnaires
- `reports`: cleaned-up questionnaire data, split by participant and questionnaire type (one .csv file for each)

## Ambient-BD questionnaires

The Ambient-BD study uses 6 different questionnaires:

- Initial contact
- Screening
- Baseline
- 6-month followup
- 12-month followup
- 18-month followup
