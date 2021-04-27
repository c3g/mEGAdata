# Get dumps of absolutely everything SUBMITTED to EGA, from all submissions
# Can parse for EGA accessions later...

# Login to prod SP, get the token from the settings.ini file and paste it here.
# python send.py pass

# Samples
curl -X GET -H "X-Token: b658b4d4-08bb-48d4-9372-b4fa35263ad4" "https://ega-archive.org/submission-api/v1/samples?status=SUBMITTED&skip=0&limit=0" > samples.json

# Experiments
curl -X GET -H "X-Token: b658b4d4-08bb-48d4-9372-b4fa35263ad4" "https://ega-archive.org/submission-api/v1/experiments?status=SUBMITTED&skip=0&limit=0" > experiments.json

# Runs
curl -X GET -H "X-Token: b658b4d4-08bb-48d4-9372-b4fa35263ad4" "https://ega-archive.org/submission-api/v1/runs?status=SUBMITTED&skip=0&limit=0" > runs.json

# Datasets
curl -X GET -H "X-Token: b658b4d4-08bb-48d4-9372-b4fa35263ad4" "https://ega-archive.org/submission-api/v1/datasets?status=SUBMITTED&skip=0&limit=0" > datasets.json

# Submissions
curl -X GET -H "X-Token: b658b4d4-08bb-48d4-9372-b4fa35263ad4" "https://ega-archive.org/submission-api/v1/submissions?status=SUBMITTED&skip=0&limit=0" > submissions.json

# Studies
curl -X GET -H "X-Token: b658b4d4-08bb-48d4-9372-b4fa35263ad4" "https://ega-archive.org/submission-api/v1/studies?status=SUBMITTED&skip=0&limit=0" > studies.json

# Policies
curl -X GET -H "X-Token: b658b4d4-08bb-48d4-9372-b4fa35263ad4" "https://ega-archive.org/submission-api/v1/policies?status=SUBMITTED&skip=0&limit=0" > policies.json

# DAC
curl -X GET -H "X-Token: b658b4d4-08bb-48d4-9372-b4fa35263ad4" "https://ega-archive.org/submission-api/v1/dacs?status=SUBMITTED&skip=0&limit=0" > dacs.json
