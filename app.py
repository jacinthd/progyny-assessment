"""Crypto Interview Assessment Module."""

import os

from dotenv import find_dotenv, load_dotenv

import pymysql
import crypto_api
import crypto_sql
import logging

load_dotenv(find_dotenv(raise_error_if_not_found=True))

# You can access the environment variables as such, and any variables from the .env file will be loaded in for you to use.
# os.getenv("DB_HOST")

# Start Here
logging.basicConfig(
    filename='storage/logs/app.log',
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S'
)
# https://docs.python.org/3/howto/logging-cookbook.html
formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')
console_ch = logging.StreamHandler()
console_ch.setFormatter(formatter)
console_ch.setLevel(logging.INFO)
logging.getLogger('').addHandler(console_ch)


def connect_to_mysql():
    return pymysql.connect(
        #host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USERNAME"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_DATABASE"),
        port=int(os.getenv("DB_PORT")),
        cursorclass=pymysql.cursors.DictCursor
    )


if __name__ == "__main__":
    crypto_list = crypto_api.get_coins(3)

    connection = connect_to_mysql()
    crypto_sql.create_tables(connection)
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(crypto_sql.existing_coins)
            existing_coins_res = cursor.fetchall()
            existing_coins_set = set([coin['symbol'] for coin in existing_coins_res])

            coin_prices = []
            purchases = []
            new_coins = []
            for coin in crypto_list:
                symbol, curr_price, name, coin_id = coin['symbol'], coin['current_price'], coin['name'], coin['id']
                history = [price for (_, price) in crypto_api.get_coin_price_history(coin_id)]
                avg_coin_price = sum(history) / len(history)
                coin_prices.append([symbol, curr_price, avg_coin_price])

                if curr_price < avg_coin_price:
                    buy_price = crypto_api.submit_order(coin_id, 1, curr_price)
                    loss_gain = ((curr_price - buy_price) / buy_price) * 100
                    purchases.append([symbol, buy_price, curr_price, loss_gain])

                # edge case: haven't encoded business rules when coin information changes
                if symbol not in existing_coins_set:
                    new_coins.append([symbol, name])

            # edge case: should check for length of symbol and price because might exceed database column length
            logging.info(f'coin prices obtained from api: {coin_prices}')
            cursor.executemany(crypto_sql.insert_coin_prices, coin_prices)

            # enter new coins into database
            if new_coins:
                # edge case: should check for length of symbol and name because might exceed database column length
                logging.info(f'new coins encountered: {new_coins}')
                cursor.executemany(crypto_sql.insert_coins, new_coins)

            # enter purchases into portfolio
            if purchases:
                logging.info(f'coins purchased: {purchases}')
                cursor.executemany(crypto_sql.insert_portfolio, purchases)

            cursor.execute(crypto_sql.current_portfolio)
            result_current_portfolio = cursor.fetchall()
            logging.info(f'current portfolio held: {result_current_portfolio}')

            # sketch of further steps
            '''
            - portfolio needs to be updated after each invocation 
            - Get the coins held at present. Get their current prices
            - update the table with current price. Also calculate loss/gain% and update that
            - If coins are sold, then make necessary update to the table
            - to optimize this, we can get current prices of coins held and top 3 coins together
            '''

        # connection is not autocommit by default. So commit to save changes.
        connection.commit()

        '''
        # for checking result
        with connection.cursor() as cursor:
            cursor.execute(crypto_sql.existing_coins)
            result_coins = cursor.fetchall()

            cursor.execute(crypto_sql.existing_coin_prices)
            result_coin_prices = cursor.fetchall()

            cursor.execute(crypto_sql.existing_portfolio)
            result_portfolio = cursor.fetchall()

            print(result_coins)
            print(result_coin_prices)
            print(result_portfolio)
        '''
