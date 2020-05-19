-- Find unlinked public_tracks.
-- Usage: Manually fill in the project name at the end of this query.

SELECT 
    pt.*
FROM
    public_track pt
WHERE
--    pt.assembly = 'hg38' and pt.id >= 2859 -- These are the newly inserted EMC tracks, aligned to hg38
  dataset_id IS NULL
  AND path like 'EMC_%'  -- Select all projects.
--   AND path LIKE 'EMC_Asthma%'
--   AND path LIKE 'EMC_BluePrint%'
--   AND path LIKE 'EMC_BrainBank%'
--   AND path LIKE 'EMC_CageKid%'
--   AND path LIKE 'EMC_iPSC%'
--   AND path LIKE 'EMC_Leukemia%'
--   AND path LIKE 'EMC_Mature_Adipocytes%'
--   AND path LIKE 'EMC_Mitochondrial_Disease%'
--   AND path LIKE 'EMC_MSCs%'
--   AND path LIKE 'EMC_SARDs%'
--   AND path LIKE 'EMC_Temporal_Change%'  -- Specify project name.

;