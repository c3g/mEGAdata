-- Find unlinked public_tracks.
-- Usage: Manually fill in the last line of this query with the project's name.

SELECT 
    pt.*
FROM
    public_track pt
WHERE
    pt.assembly = 'hg38'
        AND dataset_id IS NULL
        AND path LIKE 'EMC_Brain%'
