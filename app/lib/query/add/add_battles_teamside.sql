SET search_path TO {0[0]};

INSERT INTO battles_teamside(userid, gameid, team)

WITH matched_userid AS(
    SELECT
        userid
    FROM
        users
    WHERE
        username LIKE '%{0[1]}%'
)

SELECT
    MAX(u.userid),
    MAX(r.gameid),
    {0[2]}
FROM
    matched_userid as u,
    results as r
;