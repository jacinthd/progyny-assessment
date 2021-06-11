# how to run it
- sudo make init to build the docker file
- python app.py to run the script
- output added to logs and std output

# A technical walkthrough of the code and how it works
- app.py has calls to crypto_api.py. It gets top 3 coins, then compares them against last average of last 10 prices for each coin
- 1 of the coin is purchased if current price is less than average of last 10 prices 
- all SQL code and related functionality is in crypto_sql.py file 
- used crontab for scheduling hourly run of script. cron logs in /var/log/cron/log

# design decisions
- stuck with poetry as package manager because it was set up
- didn't use any new package, wasn't required
- mysql used. 3 tables created
    - coin prices is fact table to track coin prices that we get from api
    - coins table is dimension table to track name and symbol of coins. It will make it easier to add information 
      about coins in the future without updating fields or schema in other tables 
    - portfolio table tracks current and past holdings in portfolio with gain/loss percentage and current vs buy and 
      sell price

# what can be improved - code and business logic
- Portfolio should be updated after each invocation of application. I added sketch of the solution
- Edge cases can be covered to make application robust
    - haven't encoded business rules in the app when coin information changes. Will require update to relevant tables
    - can handle case when coin price, name and other data exceed database column length
- The output in stdout and app.log can be made more meaningful. Currently it is just printing out returned rows
- The cron solution is somewhat dirty, can be streamlined. cron logging can be done in app.log
- can set limits around how many coins to buy per day 
- it is possible to set stop loss on portfolio that makes sure that loss% is less than value
- can set profit goal on each coin transaction. Can sell after gain% on coin is realized