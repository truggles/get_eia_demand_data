#!/usr/bin/env python3

# T. Ruggles
# 3 July 2019
#
# Functions to combine demand csv files. This should happen
# after data cleaning at the most granular scale so
# corrections percolate upwards to larger regions.

import json
import csv



def return_csv_file(region):
    with open("data/{}.csv".format(region), 'r') as f:
        info = list(csv.reader(f, delimiter=","))
    return info


# Combines csv files if they have the appropriate acronmy matching
# a previously created file by get_regional_demands.py
def combine_regions(regions, out_name):
    
    is_first = True
    for region in regions:

        # Add subsequent to the first region
        if is_first:
            print("For new region {}, loading first region: {}".format(out_name, region))
            is_first = False
            master = return_csv_file(region)
            # Set series_id column to out_name
            for line in master:
                if line[0] == 'series_id': continue
                line[0] = out_name
            continue

        # Load subsequent regions
        print("For new region {}, loading subsequent region: {}".format(out_name, region))
        this_region = return_csv_file(region)

        # Loop over all lines and add values to corresponding row
        # in master file
        for i in range(1, len(this_region)):
            # Check for errors in time alignment
            if master[i][1] != this_region[i][1]:
                print("Error is file alignment in combine_regions for regions {} and {} line {}".format(regions[0], region, i))
                print(master[i], this_region[i])
                break

            master[i][2] = add_values(master[i][2], this_region[i][2])
            master[i][3] = add_values(master[i][3], this_region[i][3])

    save_new_file(master, out_name)
    
def save_new_file(combined_data, out_name):

    with open('data/{}.csv'.format(out_name), 'w', newline='') as csvfile:

        fieldnames = ['series_id', 'time', 'demand (MW)', 'forecast demand (MW)']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for line in combined_data:
            if line[0] == 'series_id': continue
            writer.writerow({'series_id': line[0], 'time': line[1], 'demand (MW)': line[2], 'forecast demand (MW)': line[3]})


# Add demand values and deal with MISSING and EMPTY cases
def add_values(val1, val2):
    if val1 in ['MISSING', 'EMPTY'] and val2 not in ['MISSING', 'EMPTY']:
        return int(val2)
    if val2 in ['MISSING', 'EMPTY'] and val1 not in ['MISSING', 'EMPTY']:
        return int(val1)
    if val1 in ['MISSING', 'EMPTY'] and val2 in ['MISSING', 'EMPTY']:
        return val1
    return int(val1) + int(val2)


if '__main__' in __name__:
    # There are 10 US BAs from the EIA database which are excluded from
    # this dictionary. They are the ones who are responsible for generation
    # only and do not report demand data to EIA. See the users guide (linked
    # from the README) for details.
    REGIONS = {
        'EASTERN' : [
                'AEC', 'AECI', 'CPLE', 'CPLW', 
                'DUK', 'FMPP', 'FPC', 
                'FPL', 'GVL', 'HST', 'ISNE', 
                'JEA', 'LGEE', 'MISO', 'NSB', 
                'NYIS', 'OVEC', 'PJM', 'SC', 
                'SCEG', 'SEC', 'SOCO', 
                'SPA', 'SWPP', 'TAL', 'TEC', 
                'TVA', 
                ],

        'TEXAS' : [
                'ERCO',
                ],
        'WESTERN' : [
                'AVA', 'AZPS', 'BANC', 'BPAT', 
                'CHPD', 'CISO', 'DOPD', 
                'EPE', 'GCPD',
                'IID', 
                'IPCO', 'LDWP', 'NEVP', 'NWMT', 
                'PACE', 'PACW', 'PGE', 'PNM', 
                'PSCO', 'PSEI', 'SCL', 'SRP', 
                'TEPC', 'TIDC', 'TPWR', 'WACM', 
                'WALC', 'WAUW',
                ]
        }

    for IC, BAs in REGIONS.items():
        combine_regions(BAs, IC)




