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

This will generate a host of csv files in the `data` folder, one for each region. 

One can edit the start date and end date of the queried data by adjusting the `start_date`
and `end_date` values in `get_regional_demands.py`.

The resulting csv files will have a header row and a single row for each hour within
the desired time range.

In the cases where the result of the EIA API query skipped
an hour, the associated row will have a demand value of `MISSING`.
In the cases where the result of the EIA API query returned NONE for
an hour, the associated row will have a demand value of `EMPTY`.
These values are kept distinct to help informe further study of the EIA data set.

# Details

The first 5 hours of July 1st 2015 are skipped in the output because that
is when EIA data begins. The data must begin at a local time, because
the West Coast regions still have three missing hours while East Coast
regions have no missing at the beginning using this method.
