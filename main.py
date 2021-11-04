import os
import sys
import logging
import argparse
import optparse
import traceback
import configparser
import pandas as pd
import numpy as np

from utils import unzip, client_postgreSQL
from utils.utils import *

global config
config = configparser.RawConfigParser()
config.read("./config.cfg")


def unzipping() -> None:

    paths_dict = dict(config.items("PATHS"))

    # Unzip idbm archive
    try:
        if not os.path.exists(
            paths_dict["output_imdb_file"] + paths_dict["check_name_file_imdb"]
        ):
            logging.debug("Unzipping imdb file...")
            unzip.unzip_file(
                type="zip",
                input_file=paths_dict["input_imdb_file"],
                output_dir=paths_dict["output_imdb_file"],
            )
        else:
            logging.debug("IMDB file already unzipped")

        if not os.path.exists(
            paths_dict["output_wiki_file"] + paths_dict["name_file_wiki"]
        ):
            logging.debug("Unzipping wiki file...")
            unzip.unzip_file(
                type="gz",
                input_file=paths_dict["input_wiki_file"],
                output_dir=paths_dict["output_wiki_file"],
            )
        else:
            logging.debug("Wiki file already unzipped")

    except Exception as e:
        print("Error in decompressing files")
        print("type error: " + str(e))
        print(traceback.format_exc())
        raise Exception()


def generate_dataframe() -> pd.DataFrame:

    # W load the necessary IMDB database and we extract the data that we need
    paths_dict = dict(config.items("PATHS"))
    target_file_ratings = paths_dict["output_imdb_file"] + "ratings.csv"
    target_file_metadata = paths_dict["output_imdb_file"] + "movies_metadata.csv"
    target_file_links = paths_dict["output_imdb_file"] + "links.csv"

    # We could improve this by defining the schema - little bit of work...
    df_ratings = pd.read_csv(target_file_ratings)
    df_metadata = pd.read_csv(target_file_metadata)
    df_links = pd.read_csv(target_file_links)

    # df_ratings groupBy 'movieId' and average rating
    df_ratings_ = df_ratings.groupby(["movieId"]).agg({"rating": [np.mean]})
    df_ratings_.columns = ["average_rating"]
    df_ratings_.reset_index(inplace=True)
    log_counts(df=df_ratings_, df_name="df_ratings")

    # We have to cast some fields into numeric, and we lose some rows - the badly formatted ones
    df_metadata__ = df_metadata[["id", "budget", "original_title"]].rename(
        columns={"id": "tmdbId"}
    )
    df_metadata__["tmdbId"] = pd.to_numeric(
        df_metadata__["tmdbId"], errors="coerce"
    )  # coerce -> invalid data will be set to NaN
    df_metadata__["budget"] = pd.to_numeric(
        df_metadata__["budget"], errors="coerce"
    )  # coerce -> invalid data will be set to NaN

    # We have to use the bridge table links, in order to pass IDs
    # We drop duplicates, beacuse in the metadata file happens to exists
    #    with the same budget and title, we call for it to be a duplicate
    pd_metadata_good_id = pd.merge(
        left=df_metadata__, right=df_links, on="tmdbId", how="left"
    )[["budget", "original_title", "movieId"]].drop_duplicates()
    log_counts(df=pd_metadata_good_id, df_name="df_metadata_after_bridge_link")

    # dropna will drop films for which we have ratings, but not budget
    df_imdb = pd.merge(
        left=df_ratings_, right=pd_metadata_good_id, on="movieId", how="left"
    ).dropna()
    log_counts(df=df_imdb, df_name="overall_imdb_df")

    tmp_col_ = df_imdb.apply(rating_over_budget, axis=1).to_frame()
    tmp_col_.columns = ["rating_over_budget"]

    df_final_imdb = pd.concat([tmp_col_, df_imdb], axis=1)

    ############### Interesting commands at this point #################

    # print(df_final_imdb.loc[df_final_imdb['budget'] > 1000000].sort_values(by=['rating_over_budget'], ascending=False))
    # We have errors in some budgets films, which are too low

    # We could implement some logging advice on the overall counts...
    # df_final_imdb[df_final_imdb.isna().any(axis=1)].count() per controllare i NaN
    # df_final_imdb[df_final_imdb.duplicated()] per i duplicati

    #####################################################################

    # We create a dataframe out of the wikipedia file
    df_wiki_urls = load_wiki_dataframe(
        xml_path=paths_dict["output_wiki_file"] + paths_dict["name_file_wiki"]
    )
    log_counts(df=df_wiki_urls, df_name="wiki_df")

    # Eventually, we join those two final databases
    # We drop duplicates, due to duplicates in the wikipedia pages' name
    df_tot = pd.merge(
        left=df_final_imdb, right=df_wiki_urls, on="original_title", how="left"
    ).drop_duplicates()
    log_counts(df=df_tot, df_name="final_df")

    return df_tot


def main():
    # Here I ahve to parametrically accept Postgres configurations...

    # In first place we unzip the files
    unzipping()

    # The we load and process the DataFrame with all the informations
    df = generate_dataframe()

    # Then we upload it on the postgreSQL
    db_spec = dict(config.items("DB_SPEC"))
    client_psql = client_postgreSQL.ClientPostgreSQL(
        username=db_spec['postgres_username'], password=db_spec['postgres_password'], database=db_spec['database_name']
    )
    client_psql.upload_df(df, database=db_spec['database_name'], table=db_spec['table_name'])


class CommandLine:
    def __init__(self):

        parser = optparse.OptionParser()
        parser.add_option(
            "-q",
            "--debug",
            action="store_true",
            dest="debug",
            help="debug parameters",
            default=False,
        )
        options, args = parser.parse_args()
        self.debug = options.debug


if __name__ == "__main__":

    input_settings = CommandLine()
    if input_settings.debug:
        print("Debug active!")
        logging.basicConfig(level=logging.DEBUG)

    main()
