# Quant-Intellect
Quant intellect is a full stack trading app built on python, postgreSQL and timescaleDB for the database, FastAPI web framework, Jinja's template engine, and Alpaca's REST api for making trades through their broker. 
# Outline by file:
- create_db.py -> creates database relations with postgreSQL/timescaledb. 
- populates_stocks.py -> It calls Alpaca API functions, in particular, the list of assets they keep up to date for us. All of these assets are looped through and inserted into our database if they are active and tradable. This is then commited into the database. There is a cron job set to once everyday or as needed to update new stock information.




