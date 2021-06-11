"""Crypto Interview Assessment Module."""

import os

from dotenv import find_dotenv, load_dotenv

import pymysql
import crypto_api

load_dotenv(find_dotenv(raise_error_if_not_found=True))

# You can access the environment variables as such, and any variables from the .env file will be loaded in for you to use.
# os.getenv("DB_HOST")

# Start Here
create_coins = """
    CREATE TABLE IF NOT EXISTS `coins` (
        `symbol` varchar(20) COLLATE utf8_bin NOT NULL,
        `name` varchar(255) COLLATE utf8_bin NOT NULL,
        PRIMARY KEY (`symbol`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
"""

insert_coins = "INSERT INTO `coins` (`symbol`, `name`) VALUES (%s, %s)"

create_coin_prices = """
    CREATE TABLE IF NOT EXISTS `coin_prices` (
        `id` int(11) NOT NULL AUTO_INCREMENT,
        `symbol` varchar(20) COLLATE utf8_bin NOT NULL,
        `current_price` DECIMAL(40,20) NOT NULL,
        `history_avg_prices` DECIMAL(40,20) NOT NULL,
        `query_datetime` DATETIME NOT NULL,
        PRIMARY KEY (`id`),
        UNIQUE KEY `symbol_and_query_datetime` (`symbol`, `query_datetime`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
"""

insert_coin_prices = "INSERT INTO `coin_prices` (`symbol`, `current_price`, `history_avg_prices`, `query_datetime`) " \
                     "VALUES (%s, %s, %s, now())"

create_portfolio = """
    CREATE TABLE IF NOT EXISTS `portfolio` (
        `id` int(11) NOT NULL AUTO_INCREMENT,
        `symbol` varchar(20) COLLATE utf8_bin NOT NULL,
        `buy_price` DECIMAL(40,20) NOT NULL,
        `current_or_sell_price` DECIMAL(40,20) NOT NULL,
        `sold` TINYINT(1) NULL,
        `current_loss_gain` DECIMAL(12,2) NOT NULL,
        `datetime_purchase` DATETIME NOT NULL,
        `datetime_sale` DATETIME NULL,
        PRIMARY KEY (`id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin 
    AUTO_INCREMENT=1;
"""

insert_portfolio = "INSERT INTO `portfolio` (`symbol`, `buy_price`, `current_or_sell_price`, `current_loss_gain`, `datetime_purchase`) " \
                    "VALUES (%s, %s, %s, %s, now())"


def create_tables(mysql_connection):
    with mysql_connection.cursor() as cursor_int:
        cursor_int.execute(create_coins)
        cursor_int.execute(create_coin_prices)
        cursor_int.execute(create_portfolio)

    mysql_connection.commit()


def connect_to_mysql():
    return pymysql.connect(
        #host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USERNAME"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_DATABASE"),
        port=int(os.getenv("DB_PORT")),
        #charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )


if __name__ == "__main__":
    crypto_list = crypto_api.get_coins(3)

    connection = connect_to_mysql()
    create_tables(connection)
    with connection:
        existing_coins = "SELECT * FROM `coins`"
        existing_coin_prices = "SELECT * FROM coin_prices"
        existing_portfolio = "SELECT * FROM portfolio"
        with connection.cursor() as cursor:
            cursor.execute(existing_coins)
            existing_coins_res = cursor.fetchall()
            existing_coins_set = set([coin['symbol'] for coin in existing_coins_res])

            coin_prices = []
            purchases = []
            new_coins = []
            for coin in crypto_list:
                symbol, curr_price, name, id = coin['symbol'], coin['current_price'], coin['name'], coin['id']
                history = [price for (_, price) in crypto_api.get_coin_price_history(id)]
                avg_coin_price = sum(history) / len(history)
                coin_prices.append([symbol, curr_price, avg_coin_price])

                if curr_price < avg_coin_price:
                    buy_price = crypto_api.submit_order(id, 1, curr_price)
                    loss_gain = ((curr_price - buy_price) / buy_price) * 100
                    purchases.append([symbol, buy_price, curr_price, loss_gain])
                    # symbol, buy_price, current_or_sell_price, current_loss_gain

                if symbol not in existing_coins_set:
                    new_coins.append([symbol, name])

            # edge case: should check for length of symbol and price because might exceed database column length
            cursor.executemany(insert_coin_prices, coin_prices)

            # enter new coins into database
            if new_coins:
                # edge case: should check for length of symbol and name because might exceed database column length
                cursor.executemany(insert_coins, new_coins)

            # enter purchases into portfolio
            if purchases:
                cursor.executemany(insert_portfolio, purchases)

        # connection is not autocommit by default. So you must commit to save
        # your changes.
        connection.commit()

        # for checking result
        with connection.cursor() as cursor:
            cursor.execute(existing_coins)
            result_coins = cursor.fetchall()

            cursor.execute(existing_coin_prices)
            result_coin_prices = cursor.fetchall()

            cursor.execute(existing_portfolio)
            result_portfolio = cursor.fetchall()

            print(result_coins)
            print(result_coin_prices)
            print(result_portfolio)
