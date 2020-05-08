-- Find unlinked public_tracks.
-- Usage: Manually fill in the last line of this query with the project's name.

SELECT 
    pt.*
FROM
    public_track pt
WHERE
--    pt.assembly = 'hg38' and pt.id >= 2859 -- These are the newly inserted EMC tracks, aligned to hg38
  dataset_id IS NULL
--   AND path LIKE 'EMC_Mature_Adipocytes%'
--   AND path LIKE 'EMC_Brain%'
  AND path LIKE 'EMC_CageKid%'
--   AND path LIKE 'EMC_iPSC%'

;