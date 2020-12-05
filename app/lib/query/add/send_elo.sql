SET search_path TO {0[0]};

INSERT INTO users_scores(userid, gameid, elo)

WITH get_userid AS(
    SELECT
        userid
    FROM
        users
    WHERE
        username LIKE '%{0[1]}%'
), get_gameid AS(
    SELECT
        MAX(gameid) AS max_gameid
    FROM
        results
)
SELECT
    gu.userid,
    gg.max_gameid,
    {0[2]}
FROM
    get_userid gu,
    get_gameid gg
;