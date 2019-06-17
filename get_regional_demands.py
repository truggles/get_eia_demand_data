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


def get_regions_data():

    regions_query = urllib.request.urlopen('http://api.eia.gov/category/?api_key={}&category_id=2122628&format=json'.format(os.environ['EIA_API_KEY']))
    regions_response = regions_query.read().decode('utf-8')
    regions_data = json.loads(regions_response)

    return regions_data

def get_regional_data(series_id):

    region_query = urllib.request.urlopen('http://api.eia.gov/series/?api_key={}&series_id={}&format=json'.format(os.environ['EIA_API_KEY'], series_id))
    region_response = region_query.read().decode('utf-8')
    region_data = json.loads(region_response)
    return region_data


def save_to_SEM_format(region_data):

    series_id = region_data['request']['series_id']

    with open('data/{}.csv'.format(series_id), 'w', newline='') as csvfile:

        fieldnames = ['series_id', 'time', 'demand (MW)']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for hour in region_data['series'][0]['data'] :
            writer.writerow({'series_id': series_id, 'time': hour[0], 'demand (MW)': hour[1]})


if '__main__' in __name__:

    regions_data = get_regions_data()
    
    for region in regions_data['category']['childseries']:
    
        print("Getting data for region: {} with series_id {}".format(region['name'], region['series_id']))
        region_data = get_regional_data(region['series_id'])
        save_to_SEM_format(region_data)




# Helpful command for dumping a dictionary to the screen if you need help
# figuring out the dictionary structure.
#
#print(json.dumps(DICTIONAY_X, sort_keys=True, indent=4))



