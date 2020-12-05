SET search_path TO {0};

SELECT
    jobname
FROM
    jobs
WHERE
    jobname = {1}
;