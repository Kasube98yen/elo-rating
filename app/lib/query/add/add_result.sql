SET search_path TO {0[0]};

INSERT INTO results(battled_at, which_was_won) 
SELECT
    clock_timestamp(),
    {0[1]}
FROM
    clock_timestamp();