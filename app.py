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

create_coin_prices = """
    CREATE TABLE IF NOT EXISTS `coin_prices` (
        `symbol` varchar(20) COLLATE utf8_bin NOT NULL,
        `date` DATE NOT NULL,
        `current_price` DECIMAL NOT NULL,
        `history_avg_prices` DECIMAL NOT NULL,
        PRIMARY KEY (`symbol`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
"""

create_portfolio = """
    CREATE TABLE IF NOT EXISTS `portfolio` (
        `id` int(11) NOT NULL AUTO_INCREMENT,
        `symbol` varchar(20) COLLATE utf8_bin NOT NULL,
        `date_purchased` DATE NOT NULL,
        `buy_price` DECIMAL NOT NULL,
        `current_or_sell_price` DECIMAL NOT NULL,
        `sold` TINYINT(1) NULL,
        `current_loss_gain` FLOAT NOT NULL,
        PRIMARY KEY (`id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin 
    AUTO_INCREMENT=1;
"""

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
        insert_coins = "INSERT INTO `coins` (`symbol`, `name`) VALUES (%s, %s)"
        existing_coins = "SELECT * FROM `coins`"
        with connection.cursor() as cursor:
            cursor.execute(existing_coins)
            existing_coins_res = cursor.fetchall()
            existing_coins_set = set([coin['symbol'] for coin in existing_coins_res])

            coins_data = []
            new_coins = []
            for coin in crypto_list:
                symbol, curr_price, name = coin['symbol'], coin['current_price'], coin['name']
                history = [price for (_, price) in crypto_api.get_coin_price_history(coin['id'])]
                avg_coin_price = sum(history) / len(history)
                coins_data.append([symbol, name, curr_price, avg_coin_price, curr_price < avg_coin_price])
                if symbol not in existing_coins_set:
                    new_coins.append([symbol, name])

            # enter new coins into database
            if new_coins:
                # edge case: should check for length of symbol and name because might exceed database column length
                cursor.executemany(insert_coins, coins_data)

        # connection is not autocommit by default. So you must commit to save
        # your changes.
        connection.commit()

        # for checking result
        with connection.cursor() as cursor:
            cursor.execute(existing_coins)
            result = cursor.fetchall()
            print(result)
