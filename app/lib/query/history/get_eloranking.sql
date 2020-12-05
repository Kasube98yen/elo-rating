SET search_path TO {0[0]};

WITH get_latest_game AS(
    SELECT
        userid,
        MAX(gameid) as latest_game
    FROM   
        users_scores
    GROUP BY
        userid
)
SELECT
    ROW_NUMBER() OVER (ORDER BY elo DESC) AS 順位,
    username,
    ROUND(elo)
FROM
    users_scores AS usc 
    LEFT OUTER JOIN users AS usr ON usc.userid = usr.userid
    LEFT OUTER JOIN get_latest_game AS glg ON usr.userid = glg.userid 
WHERE
    usc.gameid = glg.latest_game