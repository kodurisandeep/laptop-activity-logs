# laptop-activity-logs
Daily anonymized laptop activity logs

Repository contains daily anonymized activity logs (`logs/`) only. Local helper scripts (such as the activity collector) are kept locally and are not published here.

Log rotation: logs are stored as newline-delimited JSON entries in files named `activity-log-N.json`. Each file is appended daily until it reaches 50 MB, then a new file `activity-log-(N+1).json` is created.
