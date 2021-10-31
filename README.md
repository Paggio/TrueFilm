# TrueFilm

### Future developments & comments

- In first place I have to say that I don't think we can download automatically the imdb's database (since i needed to login in order to download it), which is the really interesting thing: the wiki pages won't change very often (actually i could have spent more time investigating this circumenstance, but those have been very busy days). 
Thus, we shall always start with the manual action of placing the zipped file into a target directory.

- Second and most important thing: <b>i want to structure all the project as a very basic micorservice written through Flask and Deockerized</b>. I have still to write the appropriate code, but what i foundamentally want to end up with is:

    1. An endpoint which starts the process of loading data into the postgreSQL, ind immediately return OK (and an operation identifier) or KO, if the operation started. 
    The operation will start only if in the meantime another upload is in progress. 
    As backend, we will use the same PostgreSQL (for semplicity, but we could without any problem use any other DB), where we will have a technical table where each time the starting time of an upload will be noted, as its final status (handling the exception of the operations with a standard try/except).
    2. An endpoint which will allows for the control of the status (through the ID) of an operation previuosly started.
    3. An endpoint which will return the last time that the table has been updated, getting this information through the technical table.

- The last thing is a correction that i want to try in the mechanism of the data manipulation: <b>very likely, for many films, the correct name of the wikipedia page is probabably 'Film Name (year XXX)'</b>. We could get many more links to the films wikipedia's page by considering this fact (the year of production can be easily found in IMDB database).

### Overview of the project

This code rapresents a mechanism which allows, programmatically, to extract the target data from the starting databaeses, and insert them in a postgreSQL.

It can be considered as finished, in its core components. Still, it lacks the microservice structure, on which i will work on an apposite branch - I hope to find the time.

It is a python 3 code, which relys on Docker for what concerns the postgreSQL, and on two main libraries besides the python 3 standard ones: pandas (for the DataFrames' manipulation) and psycopg2 (as a client library to the postgreSQL). In a second moment, as i will explain, also Flask could be involved.

The code is not implemented as a Python's library: since it serves to a really accurate task, i didn't see the necessity to pack itas a library to scale its reprodocibility. In case, anyway, it could be quite immediate, since i have already sliced the code in main logical functions inside the main.py, and i have placed the utils function in a dedicate directory.  

The code can also run in debug mode.

### Instructions to run the code & query the results

In first place, we have to set up the postreSQL through Docker, on our local host.

In order to do thath, we shall download and install Docker Desktop, then, through the PowerShell (i am currently referring to Windows OS, but here the main concept is to run a Docker container, which I assume to be pretty standard):

* docker pull postgres:alpine
* docker run --name postgres_db -e POSTGRES_PASSWORD=abcd1234 -d -p 5432:5432 postgres:alpine

With the first command, we download to local the image that we need, with the second command we use that image in order to run a container. With the second command, we create and run the container, setting the password of the postgres along with the exposed port.
Now, we have a postreSQL running on our local machine.

Then, we need to create a directory in the root path, TrueFilm\dataOrigin\, in which we have to put the two compressed files which are the starting point of the project. So, we'll need to download the files from https://docs.google.com/document/d/1X17nvlKN4BvSgdGT6Yhjvu30fnk4xJQ1TKH3HlBAILA/edit?usp=sharing and https://www.kaggle.com/rounakbanik/the-movies-dataset/version/7#movies_metadata.csv (we will call this file, for example, archive.zip), and place the files as dataOrigin\enwiki-latest-abstract.xml.gz and dataOrigin\archive.zip. Moreover, a folder named dataOrigin/extractions must be created. Those paths can are customizable, as long as we also modify the file config.cfg. 

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

- We have a ./tests directory. In our case, those tests will only test for the correctness of the unzipping module which will start the project, and a mild check about the correctness of the DataFrame (in particular, we check that at least the 50% of the films associate a Wikipedia page link). The tests itself could be more significant (it is basically something which is ruled by the data consumers), but the very concept of having a tests section is important, as a preliminary check to the production deploy. This test can be run as (it is important to run this command in the root directory path, as all the relative path are intended to start from here):

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
