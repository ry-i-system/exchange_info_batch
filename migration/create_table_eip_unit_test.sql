CREATE TABLE IF NOT EXISTS eip_unit_test (
    test_id VARCHAR(3) NOT NULL,
    test_text VARCHAR(3) NOT NULL,
    datetime TIMESTAMP NOT NULL,
    PRIMARY KEY(
        test_id
    )
)