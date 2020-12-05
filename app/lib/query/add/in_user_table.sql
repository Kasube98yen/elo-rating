SET search_path TO {0[0]};

SELECT
    *
FROM
    users
WHERE
    username LIKE '%{0[1]}%'
;