CREATE SCHEMA test;
SET search_path TO test;

CREATE TABLE users(
    username    varchar,
    registered_at   datetime
);