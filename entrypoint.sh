#!/bin/bash

# from https://blog.knoldus.com/running-a-cron-job-in-docker-container/
# Start the run once job.
echo "Docker container has been started"

declare -p | grep -Ev 'BASHOPTS|BASH_VERSINFO|EUID|PPID|SHELLOPTS|UID' > /container.env

# Setup a cron schedule
echo "SHELL=/bin/bash
BASH_ENV=/container.env
0 * * * * python /app.py
# This extra line makes it a valid cron" > scheduler.txt

crontab scheduler.txt
cron -f