-- Find datasets that were not linked to data files, for a particular project.
-- Effectively checks for missing data files (from the structured_data dir).
-- Usage: Manually fill in the last line of this query with the project's name.
-- Inspect orphaned_dataset_if_null column in results.

SELECT ds.id as dataset_id, pt.id as orphaned_dataset_if_null, ds.*, et.*, s.*, pt.*
FROM donor d,
	donor_metadata dm,
	donor_property dp,
    sample s,
    experiment_type et,
    dataset ds LEFT OUTER JOIN public_track pt on (ds.id = pt.dataset_id)
WHERE dm.donor_id = d.id
  and dm.donor_property_id = dp.id
  and s.donor_id = d.id
  and ds.sample_id = s.id
  and et.id = ds.experiment_type_id
  and dp.property = 'project_name'
  and dm.value like 'EMC_Brain%'
;