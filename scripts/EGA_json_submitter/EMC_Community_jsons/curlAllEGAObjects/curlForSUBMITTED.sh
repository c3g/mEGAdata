# Get dumps of everything SUBMITTED to EGA - parse for EGA accessions later...

# Samples
curl -X GET -H "X-Token: 0be86cad-c5fd-4704-9d03-d9b1f75ce9f5" "https://ega-archive.org/submission-api/v1/samples?status=SUBMITTED&skip=0&limit=0" > samples.json

# Experiments
curl -X GET -H "X-Token: aade85f1-1b7b-4458-acc6-02351ba0a9fb" "https://ega-archive.org/submission-api/v1/experiments?status=SUBMITTED&skip=0&limit=0" > experiments.json

# Runs
curl -X GET -H "X-Token: aade85f1-1b7b-4458-acc6-02351ba0a9fb" "https://ega-archive.org/submission-api/v1/runs?status=SUBMITTED&skip=0&limit=0" > runs.json

# Datasets
curl -X GET -H "X-Token: aade85f1-1b7b-4458-acc6-02351ba0a9fb" "https://ega-archive.org/submission-api/v1/datasets?status=SUBMITTED&skip=0&limit=0" > datasets.json

# Submissions
curl -X GET -H "X-Token: aade85f1-1b7b-4458-acc6-02351ba0a9fb" "https://ega-archive.org/submission-api/v1/submissions?status=SUBMITTED&skip=0&limit=0" > submissions.json

