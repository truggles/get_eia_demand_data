#!/usr/bin/env python3

# T. Ruggles
# 3 July 2019
#
# Functions to combine demand csv files. This should happen
# after data cleaning at the most granular scale so
# corrections percolate upwards to larger regions.
#
# Additions 3 Sept 2019:
# for studying the regions in SEM demand values must be positive.
# For MISSING, EMPTY, and negative values, replace with zero
# BEFORE aggregating.

import json
import csv



def return_csv_file(region):
    with open("data/{}.csv".format(region), 'r') as f:
        info = list(csv.reader(f, delimiter=","))
    return info


# Combines csv files if they have the appropriate acronmy matching
# a previously created file by get_regional_demands.py
def combine_regions(regions, out_name, grab_mean_impute=False):
    
    is_first = True
    for region in regions:

        if grab_mean_impute:
            region = region+'_mean_impute'

        # Add subsequent to the first region
        if is_first:
            print("For new region {}, loading first region: {}".format(out_name, region))
            is_first = False
            master = return_csv_file(region)
            zero_missing_and_empty(master)
            continue

        # Load subsequent regions
        print("For new region {}, loading subsequent region: {}".format(out_name, region))
        this_region = return_csv_file(region)

        # Loop over all lines and add values to corresponding row
        # in master file
        for i in range(1, len(this_region)):

            # Check for errors in time alignment
            if master[i][0] != this_region[i][0]:
                print("Error in file alignment in combine_regions for regions {} and {} line {}".format(regions[0], region, i))
                print(master[i], this_region[i])
                break

            master[i][5] = add_values(master[i][5], this_region[i][5])
            master[i][6] = add_values(master[i][6], this_region[i][6])

    if grab_mean_impute:
        out_name=out_name+'_mean_impute'
    save_new_file(master, out_name)
    
def save_new_file(combined_data, out_name):

    with open('data/{}.csv'.format(out_name), 'w', newline='') as csvfile:

        fieldnames = ['time', 'year', 'month', 'day', 'hour', 'demand (MW)', 'forecast demand (MW)']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for line in combined_data:
            if line[0] == 'time': continue
            writer.writerow({'time': line[0], 'year': line[1], 'month': line[2], 'day': line[3], 'hour': line[4],
                    'demand (MW)': line[5], 'forecast demand (MW)': line[6]})


# Set initial MISSING and EMPTY to zero in first file.
# This is to deal with ERCO/TEXAS where there is no subsequent file added.
def zero_missing_and_empty(info):
    for i in range(1, len(info)):
        if info[i][5] in ['MISSING', 'EMPTY']:
            info[i][5] = 0
        if info[i][6] in ['MISSING', 'EMPTY']:
            info[i][6] = 0


# Add demand values and deal with MISSING and EMPTY cases.
# Also, zero out negative values before aggregating
def add_values(val1, val2):
    if val1 in ['MISSING', 'EMPTY'] and val2 not in ['MISSING', 'EMPTY'] and int(float(val2)) >= 0:
        return int(float(val2))
    if val2 in ['MISSING', 'EMPTY'] and val1 not in ['MISSING', 'EMPTY'] and int(float(val1)) >= 0:
        return int(float(val1))
    if val1 in ['MISSING', 'EMPTY'] and val2 in ['MISSING', 'EMPTY']:
        return 0
    if int(float(val1)) < 0 and int(float(val2)) < 0:
        return 0
    if int(float(val1)) < 0:
        return int(float(val2))
    if int(float(val2)) < 0:
        return int(float(val1))
    return int(float(val1)) + int(float(val2))


if '__main__' in __name__:
    # There are 10 US BAs from the EIA database which are excluded from
    # this dictionary. They are the ones who are responsible for generation
    # only and do not report demand data to EIA. See the users guide (linked
    # from the README) for details.
    ICs_from_BAs = {
        'EASTERN_from_BAs' : [
                'AEC', 'AECI', 'CPLE', 'CPLW', 
                'DUK', 'FMPP', 'FPC', 
                'FPL', 'GVL', 'HST', 'ISNE', 
                'JEA', 'LGEE', 'MISO', 'NSB', 
                'NYIS', 'PJM', 'SC', 
                'SCEG', 'SOCO', 
                'SPA', 'SWPP', 'TAL', 'TEC', 
                'TVA', 
                # 'OVEC', 'SEC',
                ],
        'TEXAS_from_BAs' : [
                'ERCO',
                ],
        'WESTERN_from_BAs' : [
                'AVA', 'AZPS', 'BANC', 'BPAT', 
                'CHPD', 'CISO', 'DOPD', 
                'EPE', 'GCPD',
                'IID', 
                'IPCO', 'LDWP', 'NEVP', 'NWMT', 
                'PACE', 'PACW', 'PGE', 'PNM', 
                'PSCO', 'PSEI', 'SCL', 'SRP', 
                'TEPC', 'TIDC', 'TPWR', 'WACM', 
                'WALC', 'WAUW',
                ],
        'CONUS_from_BAs' : [
                'AEC', 'AECI', 'CPLE', 'CPLW', 
                'DUK', 'FMPP', 'FPC', 
                'FPL', 'GVL', 'HST', 'ISNE', 
                'JEA', 'LGEE', 'MISO', 'NSB', 
                'NYIS', 'PJM', 'SC', 
                'SCEG', 'SOCO', 
                'SPA', 'SWPP', 'TAL', 'TEC', 
                'TVA', 
                'ERCO',
                'AVA', 'AZPS', 'BANC', 'BPAT', 
                'CHPD', 'CISO', 'DOPD', 
                'EPE', 'GCPD',
                'IID', 
                'IPCO', 'LDWP', 'NEVP', 'NWMT', 
                'PACE', 'PACW', 'PGE', 'PNM', 
                'PSCO', 'PSEI', 'SCL', 'SRP', 
                'TEPC', 'TIDC', 'TPWR', 'WACM', 
                'WALC', 'WAUW',
                # 'OVEC', 'SEC',
                ]
        }
    # Medium regions already have EIA data cleaning and imputation applied
    # and can provide a comparison against the more graunual SMALL_REGIONS
    ICs_from_REGIONS = {
        'EASTERN_from_REGIONS' : [
            'CENT', 'MIDW', 'TEN', 'SE', 'FLA', 'CAR', 'MIDA', 'NY', 'NE'
                ],
        'TEXAS_from_REGIONS' : [
                'TEX',
                ],
        'WESTERN_from_REGIONS' : [
                'CAL', 'NW', 'SW'
                ],
        'CONUS_from_REGIONS' : [
            'CENT', 'MIDW', 'TEN', 'SE', 'FLA', 'CAR', 'MIDA', 'NY', 'NE',
                'TEX',
                'CAL', 'NW', 'SW'
                ]
        }

    for IC, regs in ICs_from_REGIONS.items():
        combine_regions(regs, IC)

    for IC, BAs in ICs_from_BAs.items():
        combine_regions(BAs, IC)

    # Must have first run simple_mean_impute.py
    grab_mean_impute = True
    for IC, BAs in ICs_from_BAs.items():
        combine_regions(BAs, IC, grab_mean_impute)


