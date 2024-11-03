# Job_search_engine_using_flask
I've made this project using the Flask library of python. This simple project uses a the nyc_jobs.csv dataset and you can search of jobs on and save your job preferences on it and based on those preferences it recommends you jobs as well. It was a simple project which i made for my end Sem.





#It is important to know this:
If you want to run this project on your device you'll need to first do some configurations manually like connecting the "flaskserver2.py" file to you MYSQL database from line 8: put the password, database, host, user, by yourself i mean c'mon? this is basic you should know this, how to connect to the database, don't you? 

#Also to start/initialize the home page 
you need to run the "flaskserver2.py" on your command prompt this file will activate the page on a localhost and just click the link this would be displayed on the terminal after the "flaskserver2.py" is successfully run.

#Anddd don't forget
You also need to feed your a MYSQL database the NYC_jobs.csv dataset you can import the .csv file directly into the database using the file import wizard, but in my case i wasn't able to import NYC_jobs.csv directly so i used this code below and pasted on the MYSQL Gui terminal---

LOAD DATA INFILE 'path_to_cleaned_file_utf8.csv'
INTO TABLE nyc_jobs
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(column1, column2, column3, ...)
CHARACTER SET utf8;
~ p.s you'll need to create a table in your database having the columns from the NYC_jobs.csv 

That's all i can help if you need more help then...
Help yourself using the mighty Google search engine

Also if your able to figure out how to run this then you can change the dataset and remake this project into somethin else i won't mind ;) 
just remember to be humble and tell them it's not your code....



