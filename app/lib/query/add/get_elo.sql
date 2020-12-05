SET search_path TO {0[0]};

WITH get_userid AS(
    SELECT
        userid
    FROM
        users
    WHERE
        username = '{0[1]}'

)
SELECT
    us.elo
FROM
    users_scores us,
    get_userid gu
WHERE
    us.userid = gu.userid
ORDER BY
    us.scoreid DESC
LIMIT 1
;

