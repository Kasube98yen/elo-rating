CREATE SCHEMA develop;

USE pvp;

CREATE TABLE users(
    userid  INT,
    jobid   INT,
    authorityid    INT,
    username    varchar,
    registered_at   datetime
)

CREATE TABLE authrities(
    authorityid INT,
    can_watch_rankings  boolean,
    can_add_players boolean
)

CREATE TABLE jobs(
    jobid   INT,
    jobname varchar
)

CREATE TABLE results(
    gameid  INT,
    battled_at  datetime,
    which_team_won_the_game   varchar
)

CREATE TABLE battles_teamside(
    playid  INT,
    userid  INT,
    gameid  INT,
    team VARCHAR
)

CREATE TABLE users_scores(
    playid  INT,
    userid  INT,
    gameid  INT,
    elo VARCHAR
);