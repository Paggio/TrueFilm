# TrueFilm

### Comments about the project

- This project can be run in two ways - both of which need the support of Docker. The first one is as a python script, that basically consists running the main.py file. The second one is to build a microservice and use http requests in order to trigger and monitor the data upload into the postgreSQL. Both ways are explained in this README.

- I don't think we that we can download automatically the imdb's database (since i needed to login in order to download it), which is the really interesting thing: the wiki pages won't change very often (actually i could have spent more time investigating this circumenstance, but those have been very busy days). 
Thus, we shall always start with the manual action of placing the zipped file into a target directory, for both the execution modes.

- The last thing is a correction that one could try in the mechanism of the data manipulation: <b>very likely, for many films, the correct name of the wikipedia page is probabably 'Film Name (year XXX)'</b>. We could get many more links to the films wikipedia's page by considering this fact (the year of production can be easily found in IMDB database).

<em>Be also sure to read the last comments, at the end of this README.md</em>

### Overview of the project

This code rapresents a mechanism which allows, programmatically, to extract the target data from the starting databaeses, and insert them in a postgreSQL.

It can be considered as finished, in its core components. Still, it lacks the microservice structure, on which i will work on an apposite branch - I hope to find the time.

It is a python 3 code, which relys on Docker for what concerns the postgreSQL, and on two main libraries besides the python 3 standard ones: pandas (for the DataFrames' manipulation) and psycopg2 (as a client library to the postgreSQL). In a second moment, as i will explain, also Flask could be involved.

The code is not implemented as a Python's library: since it serves to a really accurate task, i didn't see the necessity to pack itas a library to scale its reprodocibility. In case, anyway, it could be quite immediate, since i have already sliced the code in main logical functions inside the main.py, and i have placed the utils function in a dedicate directory.  

The code can also run in debug mode.

### Instructions to run the code as Microservice & query the results

We need to create a directory in the root path, TrueFilm\dataOrigin\, in which we have to put the two compressed files which are the starting point of the project. So, we'll need to download the files from https://docs.google.com/document/d/1X17nvlKN4BvSgdGT6Yhjvu30fnk4xJQ1TKH3HlBAILA/edit?usp=sharing and https://www.kaggle.com/rounakbanik/the-movies-dataset/version/7#movies_metadata.csv (we will call this file, for example, archive.zip, and contains seven .csv files, as ratings.csv, keywords.csv, links.csv...), and place the files as dataOrigin\enwiki-latest-abstract.xml.gz and dataOrigin\archive.zip. Moreover, a folder named dataOrigin/extractions/ must be created. Those paths can are customizable, as long as we also modify the file config.cfg. 

Then, we shall run a docker-compose command (in the root directory of this project):

* docker-compose up -d

At this point, we will have avaiable, at the port 5000 of our local machine where Docker is raining, an app, for which we have mainly two endpoints - one for triggering the process, the other one for monitoring the execution.

- http://127.0.0.1/load_postgreSQL - GET
This endpoint will return {"status": "OK", "process_id": process_number} if the uploading process has started without any problem. In case of execution/connection problem, it will return an error report. If an uploading operation is already in progress, it will return return {"status": "Ingestion already in progress", "process_number": process_number}.
Thus in order to start the ingestion, we will need to run (for exmple with python code):
```sh
r = requests.get('http://127.0.0.1:5000/load_postgreSQL')
assert r.json()['status'] == 'OK'
print('Process number : ' + r.json()['process_number'])
```

- http://127.0.0.1/process_status
Once we have triggered the execution (or we've been told that an uploading is already in progress), we can use the process number associated to monitor its progress. We have to interrogate this endpoint, adding the process_number as parameter. When the process will finish, will obtain a response such as {"status": "OK", "process_number": process_number, "last_state": "COMPLETED", "timestamp": max_timestamp}. In case of error, we will receive specific error messages. A sample python code in order to await for the upload end would be:

```sh
process_number = 123456
process_end = False
while not process_end:
    r = requests.get('http://127.0.0.1:5000/process_status', params = {'process_number' : process_number})
    assert r.status_code == 200, 'Something went wrong in http communication...'
    assert r.json()['last_state'] in ['STARTED', 'COMPLETED'], 'Something went wrong in the uploading process...'
    if r.json()['last_state'] == 'COMPLETED':
        print(r.json())
        process_end = True
```

Once a process has ended succesfully, we can look into our postgreSQL by running, through PowerShell, and always with Docker Desktop running. We are gonna enter the bash of the file system which contains the postgreSQL, and then logging as standard user, entering the database 'movie_database' (the standard name that we gave to the db) and running a SQL query on the table that we have just created (the name of the table is in this case hard coded):

* docker exec -it postgres_db bash
* psql -U postgres
* \c movie_database
* SELECT * FROM ratings_ratio;

There could have been different ways to interrogate this db, maybe in a more programmatic way. The python's library psycopg2, which is also present in this project, is a way.

### Instructions to run the code as python script & query the results

In first place, we have to set up the postreSQL through Docker, on our local host.

In order to do thath, we shall download and install Docker Desktop, then, through the PowerShell (i am currently referring to Windows OS, but here the main concept is to run a Docker container, which I assume to be pretty standard):

* docker pull postgres:alpine
* docker run --name postgres_db -e POSTGRES_PASSWORD=abcd1234 -d -p 5432:5432 postgres:alpine

With the first command, we download to local the image that we need, with the second command we use that image in order to run a container. With the second command, we create and run the container, setting the password of the postgres along with the exposed port.
Now, we have a postreSQL running on our local machine.

Then, we need to create a directory in the root path, TrueFilm\dataOrigin\, in which we have to put the two compressed files which are the starting point of the project. So, we'll need to download the files from https://docs.google.com/document/d/1X17nvlKN4BvSgdGT6Yhjvu30fnk4xJQ1TKH3HlBAILA/edit?usp=sharing and https://www.kaggle.com/rounakbanik/the-movies-dataset/version/7#movies_metadata.csv (we will call this file, for example, archive.zip and contains seven .csv files, as ratings.csv, keywords.csv, links.csv...), and place the files as dataOrigin\enwiki-latest-abstract.xml.gz and dataOrigin\archive.zip. Moreover, a folder named dataOrigin/extractions/ must be created. Those paths can are customizable, as long as we also modify the file config.cfg. 

The we can run the main.py module (after the installation of the requirements.txt):

* pip3 install -r requirements.txt
* python3 main.py (--debug for the debug mode)

Once we have done this, we have effectivaely uploaded our table into the previously activated postgreSQL, and we can look into our postgreSQL by running, through PowerShell, and always with Docker Desktop running. We are gonna enter the bash of the file system which contains the postgreSQL, and then logging as standard user, entering the database 'movie_database' (the standard name that we gave to the db) and running a SQL query on the table that we have just created (the name of the table is in this case hard coded):

* docker exec -it postgres_db bash
* psql -U postgres
* \c movie_database
* SELECT * FROM ratings_ratio;

There could have been different ways to interrogate this db, maybe in a more programmatic way. The python's library psycopg2, which is also present in this project, is a way.

### Comments on the code

Some point:

- About the 'Microservice' structure (which of course could be implemented in a much more production-mature way, and documented trough OpenAPI): i have stored the tecnical table (which actually keep trace of the state of the upload) in the same postgreSQL in which i upload the data. We could decouple it, and use any other database as the backend of the microservice. This would be a definitely better way, because it would allow us to parametrically pass (thorugh http communication) the postgreSQL address where we want to upload data. 

- We have a ./tests directory. In our case, those tests will only test for the correctness of the unzipping module which will start the project, and a mild check about the correctness of the DataFrame (in particular, we check that at least the 50% of the films associate a Wikipedia page link). The tests itself could be more significant (it is basically something which is ruled by the data consumers), but the very concept of having a tests section is important, as a preliminary check to the production deploy. <em>More tests should be added, anyway</em>. This test can be run as (it is important to run this command in the root directory path, as all the relative path are intended to start from here):

    - pip3 install -r requirements.txt
    - python3 -m pytest ./tests -s 


- The DataFrame manipulation itself was quite straigthforward, at least for the IMDBs part - we have a group by on the filmd id and an averaging in order to extract the rates, and a join with the budget data with an intermediate table. The extraction of the wikipedia data from XML was quite rude: i have scanned each line, and when i found a Title reference, the i knew that the next line would contains an url to the WIkipedia page (i have more that 6 millions record in this dataframe). I create a dataframe with this informations and the i simply join to the imdbs dataframe. This implies that:

    1. Films with the same title will link to the same page.
    2. Films that have non-univoque titles will associates the wrong Wikipedia page, unfortunately.
    3. There are films which does not redirect to the correct Wikipedia page - i have to conclude that for those films there is not wikipedia page, or the name of the page is not the exact name of the film on the imdb page. Still, more accurate controls would be needed on this point.
    4. The films which get a rating_over_budget equal to -1 are the films which results to have a budget of 0 or 1 - which, of course, would have invalidated the overall analysis. The cutoff is arbitrary, we could've set it a little bit higher.

&nbsp;
&nbsp;
&nbsp;


![TransromerImage](https://i.ytimg.com/vi/3LBNM1eYVnY/maxresdefault.jpg)
