-- Find one project's sample names.
-- Good for discerning the public_track.file_name prefix to be used to match against sample.private_name.
-- Usage: Manually fill in the last line of this query with the project's name.

SELECT s.*
FROM donor d,
	donor_metadata dm,
	donor_property dp,
    sample s
WHERE dm.donor_id = d.id
  and dm.donor_property_id = dp.id
  and s.donor_id = d.id
  and dp.property = 'project_name'
--   and dm.value like 'EMC_Mature_Adipocytes%'  -- Specify project name.
  and dm.value like 'EMC_BrainBank%'  -- Specify project name.
--   and dm.value like 'EMC_CageKid%'  -- Specify project name.
--   and dm.value like 'EMC_iPSC%'  -- Specify project name.
;