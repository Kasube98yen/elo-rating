SET search_path TO {0[0]};

INSERT INTO users(jobid, username, registered_at)

WITH matched_job AS(
    SELECT
        jobid
    FROM
        jobs
    WHERE
        jobname = '{0[2]}'
)

SELECT
    m.jobid,
    '{0[1]}',
    clock_timestamp
FROM
    matched_job as m,
    clock_timestamp()
;