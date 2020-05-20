CREATE TABLE IF NOT EXISTS eip_trade_config (
    ex_cd VARCHAR(3) NOT NULL,
    symbol VARCHAR(7) NOT NULL,
    coin_size DECIMAL(5, 2) NOT NULL,
    spread INT NOT NULL,
    price_range INT NOT NULL,
    PRIMARY KEY(
        ex_cd,
        symbol
    )
)