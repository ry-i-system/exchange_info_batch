CREATE TABLE IF NOT EXISTS eip_latest_rate_his (
    ex_cd VARCHAR(3) NOT NULL,
    ask INT,
    bid INT,
    high INT,
    last INT,
    low INT,
    symbol VARCHAR(7) NOT NULL,
    datetime TIMESTAMP NOT NULL,
    volume DOUBLE,
    PRIMARY KEY(
        ex_cd,
        symbol,
        datetime
    )
)