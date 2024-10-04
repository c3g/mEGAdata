# Get a dump of absolutely everything SUBMITTED to EGA, from all submissions
# Can parse for EGA accessions later...

# Login to prod SP, get the token from the settings.ini file and paste it here.
# python send.py pass

# Samples
curl -X GET -H "X-Token: be228304-da7b-4f57-88b0-6e8d7c5e44c2" "https://ega-archive.org/submission-api/v1/samples?status=SUBMITTED&skip=0&limit=0" > samples.json

# Experiments
curl -X GET -H "X-Token: 421cbd6a-4171-4001-9650-bfdb2c877c47" "https://ega-archive.org/submission-api/v1/experiments?status=SUBMITTED&skip=0&limit=0" > experiments.json

# Runs
curl -X GET -H "X-Token: 421cbd6a-4171-4001-9650-bfdb2c877c47" "https://ega-archive.org/submission-api/v1/runs?status=SUBMITTED&skip=0&limit=0" > runs.json

# Datasets
curl -X GET -H "X-Token: 421cbd6a-4171-4001-9650-bfdb2c877c47" "https://ega-archive.org/submission-api/v1/datasets?status=SUBMITTED&skip=0&limit=0" > datasets.json

# Submissions
curl -X GET -H "X-Token: 421cbd6a-4171-4001-9650-bfdb2c877c47" "https://ega-archive.org/submission-api/v1/submissions?status=SUBMITTED&skip=0&limit=0" > submissions.json

# Studies
curl -X GET -H "X-Token: 421cbd6a-4171-4001-9650-bfdb2c877c47" "https://ega-archive.org/submission-api/v1/studies?status=SUBMITTED&skip=0&limit=0" > studies.json

# Policies
curl -X GET -H "X-Token: 421cbd6a-4171-4001-9650-bfdb2c877c47" "https://ega-archive.org/submission-api/v1/policies?status=SUBMITTED&skip=0&limit=0" > policies.json

# DAC
curl -X GET -H "X-Token: 421cbd6a-4171-4001-9650-bfdb2c877c47" "https://ega-archive.org/submission-api/v1/dacs?status=SUBMITTED&skip=0&limit=0" > dacs.json

# No API path for Files objects exists.

# Get the Samples from submission1 to be referenced from submission2
curl -X GET -H "X-Token: 5616773c-e31d-4e7b-81bf-f04600b4b114" "https://ega-archive.org/submission-api/v1/submissions/619b421398e252000107d809/samples?status=SUBMITTED&skip=0&limit=0" > B2_samples.json
