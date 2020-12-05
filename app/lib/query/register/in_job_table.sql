SET search_path TO {0[0]};

SELECT
    *
FROM
    jobs
WHERE
    jobname = '{0[1]}'
;