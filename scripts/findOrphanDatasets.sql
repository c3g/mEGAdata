-- Find datasets that were not linked to data files, for a particular project.
-- Effectively checks for missing data files (from the structured_data dir).
-- Usage: Manually fill in the last line of this query with the project's name.
-- Inspect orphaned_dataset_if_null column in results.

SELECT dm.value as project, ds.id as dataset_id, pt.id as orphaned_dataset_if_null, 'dataset', ds.*, 'experiment_type', et.*, 'sample', s.*, 'public_track', pt.*
FROM donor d,
	donor_metadata dm,
	donor_property dp,
    sample s,
    experiment_type et,
    dataset ds LEFT OUTER JOIN public_track pt on (ds.id = pt.dataset_id AND pt.assembly = 'hg38' AND pt.id >= 2859) -- These are the newly inserted (2020) EMC tracks, aligned to hg38, with the higher pt.id's.
WHERE dm.donor_id = d.id
--   and pt.assembly = 'hg38' and pt.id >= 2859 -- These are the newly inserted EMC tracks, aligned to hg38
  and dm.donor_property_id = dp.id
  and s.donor_id = d.id
  and ds.sample_id = s.id
  and et.id = ds.experiment_type_id
  and dp.property = 'project_name'

  and pt.id is null  -- Orphan datasets.
--   and pt.id is not null  -- Matched datasets.

--   and dm.value like 'EMC_%'  -- Use to select all projects.
--   and dm.value like 'EMC_Mature_Adipocytes%'  -- Specify project name.
--   and dm.value like 'EMC_Brain%'  -- Specify project name.
--   and dm.value like 'EMC_CageKid%'
--   and dm.value like 'EMC_iPSC%'
--   and dm.value like 'EMC_Leukemia%'
  and dm.value like 'EMC_Mitochondrial_Disease%'

;