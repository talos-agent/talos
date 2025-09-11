import os
import json
from datetime import datetime
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

load_dotenv()
package_dir = Path(__file__).parent.parent.parent

def save_json_file_to_datastore(filename: str, data: dict):
    """
    Save a dictionary as json file to the datastore directory

    Parameters
    ----------
    filename : str
        filename of json.
    data : dict
        dictionary of data.

    """
    filepath = os.path.join(
        package_dir,
        'data_store',
        filename
    )

    with open(filepath, 'w') as f:
        json.dump(data, f)


def save_csv_to_datastore(filename: str, dataframe):
    """
    For a given filename, save pandas dataframe as a csv to datastore

    Parameters
    ----------
    filename : str
        name of file.
    dataframe : pd.DataFrame
        pandas dataframe

    """

    archive_filepath = os.path.join(
        package_dir,
        "data_store",
        filename
    )

    if os.path.exists(archive_filepath):
        archive = pd.read_csv(
            archive_filepath
        )

        dataframe = pd.concat(
            [archive, dataframe]
        )

    dataframe.to_csv(
        os.path.join(
            package_dir,
            "data_store",
            filename
        ),
        index=False
    )


def make_timestamped_dataframe(data):
    """
    Add a new column to a given dataframe with a column for timestamp

    Parameters
    ----------
    data : pd.DataFrame
        dataframe to add timestamp column to.

    """
    dataframe = pd.DataFrame(data, index=[0])
    dataframe['timestamp'] = datetime.now()

    return dataframe
