# Quant-Intellect
Quant intellect is a full stack trading app built on python, SQL for the database, and Alpaca's API for the updated stock information.  

# Outline by file:
- create_bd.py -> SQLite database was created in this script. It creates a stock table and a stock price table and executes it from python.
- populates_stocks.py -> It calls Alpaca API functions, in particular, the list of assets they keep up to date for us. All of these assets are looped through and inserted into our database if they are active and tradable. This is then commited into the database. There is a cron job set to once everyday or as needed to update new stock information.
- (side note: you can visit sqlitebrowser.org, which makes it easy to browse our database for free.)
