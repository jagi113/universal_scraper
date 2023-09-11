# Books scraper

This is a simple app that asynchronously scrapes info about books sold at www.pantarhei.sk.

By running run.py file you will get users menu with books loaded from 5 pages as an example, where you can 
- list books by title
- list books by author
- list books by price
- search books by title or an author
- show details of next book        
It is not database based. Scraping is done in real-time, so it takes some time to load books info.            
                       

By running scrape_to_database.py file all records will be assigned to the database.              
You can choose number of pages you want to scrape and their entries save to database.    

Both files create logs shown in terminal (info level) and in log files (debug level).
                    
Database file called database.ini insert into folder db_config. Instance of ini file is: 
##################                  
[postgresql]                    
host=yourhostapi                    
port=databaseport                 
dbname=nameofdatabase                
user=nameofuser                
password=userspassword                
##################            

For creating database table "books" use postgresql query file "books_table.sql" in db_config.

