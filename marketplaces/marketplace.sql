CREATE DATABASE marketplaces;

USE marketplaces;

CREATE TABLE market (
    marketplace_id INT NOT NULL PRIMARY KEY,
    marketplace_coords JSON NOT NULL,
    marketplace_creation_date DATE
);

CREATE TABLE goods (
    goods_id INT NOT NULL AUTO_INCREMENT  PRIMARY KEY,
    market_id INT NOT NULL,
    goods VARCHAR(50) NOT NULL,
    stock INT NOT NULL,

    FOREIGN KEY (market_id)
        REFERENCES market(marketplace_id)
);
