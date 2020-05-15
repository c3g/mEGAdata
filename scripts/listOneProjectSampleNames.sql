-- Find one project's sample names.
-- Good for discerning the public_track.file_name prefix to be used to match against sample.private_name.
-- Usage: Manually fill in the project name at the end of this query.

SELECT s.*
FROM donor d,
	donor_metadata dm,
	donor_property dp,
    sample s
WHERE dm.donor_id = d.id
  and dm.donor_property_id = dp.id
  and s.donor_id = d.id
  and dp.property = 'project_name'
--   and dm.value like 'EMC_Asthma%'
--   and dm.value like 'EMC_BluePrint%'
--   and dm.value like 'EMC_BrainBank%'
--   and dm.value like 'EMC_CageKid%'
--   and dm.value like 'EMC_iPSC%'
--   and dm.value like 'EMC_Leukemia%'
--   and dm.value like 'EMC_Mature_Adipocytes%'
--   and dm.value like 'EMC_Mitochondrial_Disease%'
--   and dm.value like 'EMC_MSCs%'
  and dm.value like 'EMC_SARDs%'  -- Specify project name.

;