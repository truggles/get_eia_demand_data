# get_eia_demand_data
Tools for using EIA's (U.S. Energy Information Administration) API to query demand data and formatting it for SEM use.

This code was written using `python3.6`.

# Getting and EIA API key

EIA provides open data and an API for accessing them. To use their API you must first get a key here: https://www.eia.gov/opendata/register.php

Then create a file: `~/keys/eia_api_key.sh` with a single line `export EIA_API_KEY=YOUR_KEY_HERE`


# EIA API Resources

EIA provides some commands here: https://www.eia.gov/opendata/commands.php


# EIA Electricity Demand

Web interface for EIA electricity demand data: https://www.eia.gov/opendata/qb.php?category=2122628


# Running The Code

At the start of each session `source env.sh` to load your EIA API key.

To generate a single csv file per EIA region with all EIA hourly demand run

```
python get_regional_demands.py
```
