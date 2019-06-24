#!/usr/bin/env python3

# T. Ruggles
# 14 June 2019
#
# Functions to query the EIA demand database and output a simple csv file.
# If run as is this will generate individual csv files for each region
# based on EIA region.



import urllib.request
import urllib.parse
import json
import csv
import os
import datetime
from collections import OrderedDict

# Query EIA to get list of regions for which hourly electricity deman data is available
def get_regions_data():

    regions_query = urllib.request.urlopen('http://api.eia.gov/category/?api_key={}&category_id=2122628&format=json'.format(os.environ['EIA_API_KEY']))
    regions_response = regions_query.read().decode('utf-8')
    regions_data = json.loads(regions_response)

    return regions_data


# Query EIA for hour electric demand data for a given region
def get_regional_data(series_id):

    region_query = urllib.request.urlopen('http://api.eia.gov/series/?api_key={}&series_id={}&format=json'.format(os.environ['EIA_API_KEY'], series_id))
    region_response = region_query.read().decode('utf-8')
    region_data = json.loads(region_response)
    return region_data



# Generate full hourly date and time series from start date ending the hour before end date
def generate_full_time_series(start_date, end_date):
    full_date_range = []
    for n in range(int ((end_date - start_date).days)):
        for h in range(24):
            full_date_range.append(datetime.datetime.combine(start_date + datetime.timedelta(n), datetime.time(h, 0)))

    return full_date_range


# Save region hourly electric demand data to a format usable by SEM
def save_to_SEM_format(region_data, full_date_range):

    series_id = region_data['request']['series_id']

    with open('data/{}.csv'.format(series_id), 'w', newline='') as csvfile:

        fieldnames = ['series_id', 'time', 'demand (MW)']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        full_date_range_dict = OrderedDict()
        for hour in full_date_range:
            full_date_range_dict[hour.strftime("%Y%m%dT%HZ")] = 'MISSING'

        for demand in region_data['series'][0]['data']:
            try:
                if demand[1] == None:
                    full_date_range_dict[demand[0]] = 'EMPTY'
                else:
                    full_date_range_dict[demand[0]] = demand[1]
            except KeyError:
                print("Check date and time formatting for series {} for time {}".format(series_id, hour[0]))


        for time, demand in full_date_range_dict.items():
            writer.writerow({'series_id': series_id, 'time': time, 'demand (MW)': demand})




if '__main__' in __name__:

    regions_data = get_regions_data()

    # Date range of interest
    start_date = datetime.date(2015, 7, 1) # EIA demand data starts in July of 2015
    end_date = datetime.date(2019, 6, 1) # Can update this as time progresses
    full_date_range = generate_full_time_series(start_date, end_date)

    
    for region in regions_data['category']['childseries']:

        print("Getting data for region: {} with series_id {}".format(region['name'], region['series_id']))
        region_data = get_regional_data(region['series_id'])
        save_to_SEM_format(region_data, full_date_range)




# Helpful command for dumping a dictionary to the screen if you need help
# figuring out the dictionary structure.
#
#print(json.dumps(DICTIONAY_X, sort_keys=True, indent=4))



