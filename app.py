from flask import Flask, render_template, request
import traceback
import logging
from threading import Thread
from random import randrange
from main import *
import datetime
from utils.client_postgreSQL import ClientPostgreSQL

app = Flask(__name__)

global config

config = configparser.RawConfigParser()
config.read("./config.cfg")

# We run this code with

@app.route('/params_test')
def params_entry():
    app.logger.debug('test params input')
    return {'result' : 'This is the argument that you have passed : ' + request.args.get('test_param', 'PARAMATER_MISSING')}

@app.route('/')
def entry():
    app.logger.debug('test debug...')
    return {'result' : 'OK'}

@app.route('/load_postgreSQL', methods = ['GET'])
def load_postgreSQL():

    db_spec = dict(config.items("DB_SPEC"))

    def upload_into_postgreSQL(client : ClientPostgreSQL, df : pd.DataFrame, process_number : str) -> None:
        app.logger.debug('Starting the loading process...')
        try:
            main()
            df_logging = pd.DataFrame({'process_number' : [process_number], 'state' : ['FINISHED'], 'time' : [datetime.datetime.now()]})
            client.upload_df(df_logging, database = db_spec['tech_table_db'], table = db_spec['tech_table_name'])
        except:
            app.logger.warning('Error in the loading process')
            df_logging = pd.DataFrame({'process_number' : [process_number], 'state' : ['ERROR'], 'time' : [datetime.datetime.now()]})
            client.upload_df(df_logging, database = db_spec['tech_table_db'], table = db_spec['tech_table_name'])

    # In first place, we check the connection to the postgreSQL
    try:
        app.logger.debug('Checking postgreSQL connection')
        client_psql = ClientPostgreSQL(
            db_spec['postgres_username'], password=db_spec['postgres_password']
        )
    except Exception as e:
        app.logger.warning('Error in postgreSQL connection')
        return {'status' : 'KO', 'step' : 'Database connection', 'exception' : str(e)}

    # In second place, we check if another process is currently running
    if not client_psql.check_table_exists(table = db_spec['tech_table_name'], database = db_spec['tech_table_db']):
        app.logger.debug('First ingestion process!')
    else:
        df_process = client_psql.read_table(table = db_spec['tech_table_name'], database = db_spec['tech_table_db'])
        most_recent_log = df_process.loc[df_process['timestamp_insertion'] == df_process['timestamp_insertion'].max()]
        if most_recent_log['state'][0] == 'STARTED':
            app.logger.debug('Ingestion is actually happening!')
            return {'status' : 'Ingestion already in progress', 'process_number' : most_recent_log['process_number'][0]}

    # Then, we start the uploading process
    process_number = str(randrange(1000000))
    try:
        app.logger.debug(f'Starting process with process_number {process_number}')
        df_logging = pd.DataFrame({'process_number' : [process_number], 'state' : ['STARTED'], 'time' : [datetime.datetime.now()]})
        client_psql.upload_df(df_logging, database = db_spec['tech_table_db'], table = db_spec['tech_table_name'])
        thread = Thread(target=upload_into_postgreSQL, 
                        kwargs={'client': client_psql, 'df' : df_logging, 'process_number' : process_number})
        thread.start()
    except Exception as e:
        return {'status' : 'KO', 'step' : 'thread inizialization', 'exception' : str(e), 'traceback' : traceback.format_exc()}    
    return {'status' : 'OK', 'process_id' : process_number}

@app.route('/process_status')
def process_status():

    db_spec = dict(config.items("DB_SPEC"))

    # We expect process_number as state parameter
    client_psql = ClientPostgreSQL(
        db_spec['postgres_username'], password=db_spec['postgres_password'], database=db_spec['database_name']
    )
    process_number = str(request.args.get('process_number', None))
    if process_number is None:
        return {'status' : 'KO', 'info' : 'process_number param is required!'}
    if not client_psql.check_table_exists(table = db_spec['tech_table_name'], database = db_spec['tech_table_db']):
        return {'status' : 'KO', 'info' : 'Technical table does not exists yet!'}
    else:
        df_process = client_psql.read_table(table = db_spec['tech_table_name'], database = db_spec['tech_table_db'])
        interesting_data = df_process.loc[df_process['process_number'] == process_number]
        if interesting_data.shape[0] == 0:
            return {'status' : 'KO', 'process_number' : process_number, 'info' : 'No processes with that number'}
        status = interesting_data.loc[interesting_data['timestamp_insertion'] == interesting_data['timestamp_insertion'].max()]['state'].iloc[0]
        max_timestamp = interesting_data['timestamp_insertion'].max()
        return {'status' : 'OK', 'process_number' : process_number, 'last_state' : status, 'timestamp' : max_timestamp}

# import requests
# url = 'http://192.168.3.45:8080/api/v2/event/log'
# data = {"eventType": "AAS_PORTAL_START", "data": {"uid": "hfe3hf45huf33545", "aid": "1", "vid": "1"}}
# params = {'sessionKey': '9ebbd0b25760557393a43064a92bae539d962103', 'format': 'xml', 'platformId': 1}
# requests.post(url, params=params, json=data)

if __name__ == '__main__':

    print('Starting microservice...')
    app.run(debug = True)

# We can run this module, or 'python -m flask run'