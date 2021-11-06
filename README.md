# TrueFilm

<b>TO BE UPDATED</b>

### Instructions to run the code

In first place, we have to set up the postreSQL through Docker, on our local host.

In order to do thath, we shall download and install Docker Desktop, then (i am currently referring to Windows OS), through the PowerShell:

* docker pull postgres:alpine
* docker run --name postgres_db -e POSTGRES_PASSWORD=abcd1234 -d -p 5432:5432 postgres:alpine

With the first command, we download to local the image that we need, with the second command we use that image in order to run a container. With the second command, we create and run the container, setting the password of the postgres along with the exposed port.
Now, we have a postreSQL running on our local machine.

Then, we need to create a directory in the root path, TrueFilm\dataOrigin\, in which we have to put the two compressed files which are the starting point of the project. So, we'll need to download the files from https://docs.google.com/document/d/1X17nvlKN4BvSgdGT6Yhjvu30fnk4xJQ1TKH3HlBAILA/edit?usp=sharing and https://www.kaggle.com/rounakbanik/the-movies-dataset/version/7#movies_metadata.csv (we will call this file, for example, archive.zip), and place the files as dataOrigin\enwiki-latest-abstract.xml.gz and dataOrigin\archive.zip. Moreover, a folder named dataOrigin/extractions must be created. Those paths can are customizable, as long as we also modify the file config.cfg. 

The we can run the main.py module (after the installation of the requirements.txt):

* pip3 install -r requirements.txt
* python3 main.py

Once we have done this, we have effectivaely uploaded our table into the previously activated postgreSQL, and we can look into our postgreSQL by running, through PowerShell, and always with Docker Desktop running. We are gonna enter the bash of the file system which contains the postgreSQL, and then logging as standard user, entering the database 'movie_database' (the standard name that we gave to the db) and running a SQL query on the table that we have just created (the name of the table is in this case hard coded):

* docker exec -it postgres_db bash
* psql -U postgres
* \c movie_database
* SELECT * FROM ratings_ratio;

There could have been different ways to interrogate this db, maybe in a more programmatic way. The python's library psycopg2, which is also present in this project, is a way.

### Comments

Films with the same title will link to the same page.

Films that have non-univoque titles will associates the wrong page... Unfortunately

I don't think we can download automatically the imdbs, which is the really interesting thing: the wiki pages won't change very often...

![TransromerImage](https://i.ytimg.com/vi/3LBNM1eYVnY/maxresdefault.jpg)
