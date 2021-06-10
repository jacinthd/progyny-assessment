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
        `id` int(11) NOT NULL AUTO_INCREMENT,
        `symbol` varchar(20) COLLATE utf8_bin NOT NULL,
        `name` varchar(255) COLLATE utf8_bin NOT NULL,
        PRIMARY KEY (`id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin
    AUTO_INCREMENT=1;
"""


def create_tables(mysql_connection):
    with mysql_connection.cursor() as cursor_int:
        cursor_int.execute(create_coins)

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

    # Connect to the database
    connection = connect_to_mysql()

    create_tables(connection)
    with connection:
        with connection.cursor() as cursor:
            # Create a new record
            sql = "INSERT INTO `coins` (`symbol`, `name`) VALUES (%s, %s)"
            coins_data = [(coin['symbol'], coin['name']) for coin in crypto_list]

            # edge case: should check for length of symbol and name because might exceed database column length
            cursor.executemany(sql, coins_data)

        # connection is not autocommit by default. So you must commit to save
        # your changes.
        connection.commit()

        with connection.cursor() as cursor:
            # Read a single record
            sql = "SELECT * FROM `coins`"
            cursor.execute(sql)
            result = cursor.fetchall()
            print(result)
