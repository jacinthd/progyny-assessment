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

existing_coins = "SELECT * FROM `coins`"
existing_coin_prices = "SELECT * FROM coin_prices"
existing_portfolio = "SELECT * FROM portfolio"

current_portfolio = """
select symbol, number_of_coins, round((100 * `profit/loss`/buy_price_total), 2) as `profit/loss %`
FROM (
SELECT symbol, count(*) as number_of_coins, sum(current_or_sell_price - buy_price) as `profit/loss`, 
sum(buy_price) buy_price_total FROM portfolio 
where sold != 1 or sold is null
group by symbol
) as p
"""


def create_tables(mysql_connection):
    with mysql_connection.cursor() as cursor_int:
        cursor_int.execute(create_coins)
        cursor_int.execute(create_coin_prices)
        cursor_int.execute(create_portfolio)

    mysql_connection.commit()