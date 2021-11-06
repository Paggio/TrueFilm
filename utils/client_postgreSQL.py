from __future__ import print_function
import datetime
import logging
import psycopg2
from psycopg2 import sql
import pandas as pd
from random import randint
from sqlalchemy import create_engine


class ClientPostgreSQL:
    """
    The postgreSQL administration could be achieved using python lib psycopg2 - but this is not our target
    """

    def __init__(
        self,
        username: str,
        password: str,
        database: str = None,
        hostname: str = "localhost",
        port: str = "5432",
    ):

        self.__hostname = hostname
        self.__username = username
        self.__password = password
        self.__database = database
        self.__port = port

        logging.debug("Connecting to database...")
        self.connection = psycopg2.connect(
            host=self.__hostname, user=self.__username, password=self.__password
        )
        logging.debug("postgreSQL connected!")

    def set_database(self, database):
        self.__database = database
        self.connection = psycopg2.connect(
            host=self.__hostname,
            user=self.__username,
            password=self.__password,
            database=self.__database,
        )

    def get_database(self):
        return self.__database

    # [...]

    def set_port(self, port):
        self.__port = port

    def get_port(self):
        return self.__port

    # [...]

    def __check_exists_database(self, database: str) -> bool:
        """
        Check if a database exists in postreSQL
        """

        logging.debug(f"Checking if database {database} exists...")
        cur = self.connection.cursor()
        cur.execute("SELECT datname FROM pg_database;")
        list_database = cur.fetchall()

        return (database,) in list_database

    def __create_ifne_database(self, database: str) -> None:
        """
        Create database if not exists
        """

        logging.debug(f"Creating database {database}...")
        self.connection.set_isolation_level(
            psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT
        )
        cur = self.connection.cursor()
        cur.execute(sql.SQL(f"CREATE DATABASE {database}"))

        return

    def __check_exists_table(self, table: "str", database: "str") -> bool:
        """
        Check if table exists - working only for tables in tables schema = 'public'
        We have to first connect to the interested db!
        """
        if not self.__check_exists_database(database=database):
            # If database does not exist, so does not the table
            return False
        if self.__database != database:
            self.set_database(database)
        cur = self.connection.cursor()
        cur.execute(
            f"SELECT EXISTS (SELECT * FROM information_schema.tables WHERE  table_schema = 'public' AND table_name = '{table}' AND table_catalog = '{database}');"
        )
        return cur.fetchall()[0][0]

    def upload_df(
        self,
        df: pd.DataFrame,
        database: "str",
        table: "str",
        mode="append",
        add_timestamp: bool = True,
    ) -> None:
        """
        Function to upload pandas dataframe into postrgreSQL DB
        """
        assert mode in ["append", "replace", "fail"]

        if not self.__check_exists_database(database):
            logging.debug(f"{database} does not exists, creating!")
            self.__create_ifne_database(database)

        if self.__database != database:
            self.set_database(database)

        # We need to cast column names into lower()
        df.columns = [x.lower() for x in df.columns]

        # If timestamp flag is true, we need to add a timestamp column
        if add_timestamp:
            df["timestamp_insertion"] = pd.Series(
                [datetime.datetime.now()] * len(df.index)
            )

        # With psycopg2 the time would be higher (?)
        logging.debug("Loading the dataframe on the postgreSQL...")
        engine = create_engine(
            f"postgresql://{self.__username}:{self.__password}@{self.__hostname}:{self.__port}/{self.__database}"
        )
        df.to_sql(name=table, con=engine, if_exists=mode, index=False)

    def read_table(self, database: "str", table: "str") -> pd.DataFrame:
        """
        Read table from postgreSQL, and return it as pandas DataFrame
        """

        if not self.__check_exists_database(database):
            logging.error(
                f"{database} DB does not exists, but we are trying to read from it!"
            )
            raise Exception
        if not self.__check_exists_table(database=database, table=table):
            logging.error(
                f"{table} from {database} does not exists, but we are trying to read from it!"
            )
            raise Exception

        if self.__database != database:
            self.set_database(database)

        engine = create_engine(
            f"postgresql://{self.__username}:{self.__password}@{self.__hostname}:{self.__port}/{self.__database}"
        )

        df = pd.read_sql_query(f'select * from "{table}"', con=engine)

        return df

    def check_table_exists(self, table: str, database: str) -> bool:
        """
        I implement an interface for checking if a table exists, since it can be usefull to have it as public method
        """
        return self.__check_exists_table(table=table, database=database)
