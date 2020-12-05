CREATE SCHEMA deploy;
SET search_path TO deploy;

CREATE TABLE users(
    userid  SERIAL,
    jobid   INT,
    authorityid    INT,
    username    varchar,
    registered_at   timestamp
);

CREATE TABLE jobs(
    jobid   SERIAL,
    jobname varchar
);

CREATE TABLE results(
    gameid  SERIAL,
    battled_at  timestamp,
    which_was_won   varchar
);

CREATE TABLE battles_teamside(
    playid  SERIAL,
    userid  INT,
    gameid  INT,
    team VARCHAR
);

CREATE TABLE users_scores(
    scoreid  SERIAL,
    userid  INT,
    gameid  INT,
    elo INT
);

CREATE TABLE authorities(
    discordid INT,
    can_watch_rankings  boolean,
    can_add_players boolean
);