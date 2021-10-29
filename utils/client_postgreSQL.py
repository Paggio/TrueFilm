from __future__ import print_function
import datetime
import logging
import psycopg2
from psycopg2 import sql
import pandas as pd
from random import randint
from sqlalchemy import create_engine

class ClientPostgreSQL():
    """
    The postgreSQL administration could be achieved using python lib psycopg2 - but this is not our target
    """

    def __init__(self, username : str, password : str, database : str = None, hostname : str = 'localhost', port : str = '5432'):

        self.__hostname__ = hostname
        self.__username__ = username
        self.__password__ = password
        self.__database__ = database
        self.__port__ = port

        logging.debug('Connecting to database...')
        self.connection = psycopg2.connect( 
            host=self.__hostname__, 
            user=self.__username__, 
            password=self.__password__
        )
        logging.debug('Database connected!')

    def set_database(self, database):
        self.__database__ = database
    
    def get_database(self):
        return self.__database__

    # [...]

    def set_port(self, port):
        self.__port__ = port
    
    def get_port(self):
        return self.__port__

    def __check_exists_database__(self, database : str) -> bool:
        """
        Check if a database exists in postreSQL
        """

        logging.debug(f'Checking if database {database} exists...')
        self.connection.autocommit = True
        cur = self.connection.cursor()
        cur.execute("SELECT datname FROM pg_database;")
        list_database = cur.fetchall()

        return (database,) in list_database

    def __create_ifne_database__(self, database : str) -> None:
        """
        Create database if not exists
        """

        logging.debug(f'Creating database {database}...')
        self.connection.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        cur = self.connection.cursor()
        cur.execute(sql.SQL(f"CREATE DATABASE {database}"))

        return

    def upload_df(self, df : pd.DataFrame, database : 'str', table : 'str', mode = 'append', add_timestamp : bool = True) -> None:
        """
        Function to upload pandas dataframe into postrgreSQL DB
        """
        assert mode in ['append', 'replace', 'fail']

        if not self.__check_exists_database__(database):
            logging.debug(f'{database} does not exists, creating!')
            self.__create_ifne_database__(database)

        if self.__database__ != database:
            self.set_database(database)
        
        # We need to cast column names into lower()
        df.columns = [x.lower() for x in df.columns]

        # If timestamp flag is true, we need to add a timestamp column
        if add_timestamp:
            df['timestamp_insertion'] = pd.Series([datetime.datetime.now()] * len(df.index))

        # With psycopg2 the time would be higher (?)
        logging.debug('Loading the dataframe on the postgreSQL...')
        engine = create_engine(f'postgresql://{self.__username__}:{self.__password__}@{self.__hostname__}:{self.__port__}/{self.__database__}')
        df.to_sql(name = table, con = engine, if_exists = mode, index = False)