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
import pandas as pd



def return_csv_file(region):
    with open("data5_out2/{}.csv".format(region), 'r') as f:
        info = list(csv.reader(f, delimiter=","))
    return info


def add_MICE_imputations_to_files(mice_file_path, region):
    print("Adding MICE imputations to {}".format(region))
    df_mice = pd.read_csv(mice_file_path)
    df = pd.read_csv("data5/{}.csv".format(region))
    df['cleaned demand (MW)'] = df_mice[region]
    df.to_csv("data5_out2/{}.csv".format(region), index=False, na_rep='NA')



# Combines csv files if they have the appropriate acronmy matching
# a previously created file by get_regional_demands.py
def combine_regions(regions, out_name, grab_mean_impute=False, grab_MICE=False):
    
    usable_BAs = return_usable_BAs()
    usable_regions = return_usable_regions()

    is_first = True
    for region in regions:

        if region not in usable_BAs and region not in usable_regions:
            print("BA/region {} is excluded because it is not included in return_usable_BAs() OR return_usable_regions()".format(region))
            continue

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
            if grab_MICE:
                master[i][7] = add_values(master[i][7], this_region[i][7])

    if grab_mean_impute:
        out_name=out_name+'_mean_impute'
    save_new_file(master, out_name, grab_MICE)
    
def save_new_file(combined_data, out_name, grab_MICE=False):

    with open('data5_out2/{}.csv'.format(out_name), 'w', newline='') as csvfile:

        fieldnames = ['time', 'year', 'month', 'day', 'hour', 'demand (MW)', 'forecast demand (MW)']
        if grab_MICE:
            fieldnames.append('cleaned demand (MW)')
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for line in combined_data:
            if line[0] == 'time': continue
            if not grab_MICE:
                writer.writerow({'time': line[0], 'year': line[1], 'month': line[2], 'day': line[3], 'hour': line[4],
                        'demand (MW)': line[5], 'forecast demand (MW)': line[6]})
            else:
                writer.writerow({'time': line[0], 'year': line[1], 'month': line[2], 'day': line[3], 'hour': line[4],
                    'demand (MW)': line[5], 'forecast demand (MW)': line[6], 'cleaned demand (MW)': line[7]})


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



def return_BAs_per_region_map():
    
    regions = {
            'CENT' : 'Central', 
            'MIDW' : 'Midwest', 
            'TEN' : 'Tennessee', 
            'SE' : 'Southeast', 
            'FLA' : 'Florida', 
            'CAR' : 'Carolinas', 
            'MIDA' : 'Mid-Atlantic', 
            'NY' : 'New York', 
            'NE' : 'New England',
            'TEX' : 'Texas', 
            'CAL' : 'California', 
            'NW' : 'Northwest', 
            'SW' : 'Southwest'
    }

    rtn_map = {}
    for k, v in regions.items():
        rtn_map[k] = []

    # Load EIA's Blancing Authority Acronym table
    # https://www.eia.gov/realtime_grid/
    df = pd.read_csv('data/balancing_authority_acronyms.csv', 
            skiprows=1) # skip first row as it is source info

    # Loop over all rows and fill map
    for idx in df.index:

        # Skip Canada and Mexico
        if df.loc[idx, 'Region'] in ['Canada', 'Mexico']:
            continue

        reg_acronym = ''
        # Get region to acronym
        for k, v in regions.items():
            if v == df.loc[idx, 'Region']:
                reg_acronym = k
                break
        assert(reg_acronym != '')

        rtn_map[reg_acronym].append(df.loc[idx, 'Code'])
        
    tot = 0
    print("\nBA to Region mapping:")
    for k, v in rtn_map.items():
        print(k, v)
        tot += len(v)
    print("\n\nTotal US48 BAs mapped {}.  Recall 10 are generation only.".format(tot))

    return rtn_map



def return_usable_BAs():
    return [
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

def return_usable_regions():
    return [
                'CENT', 'MIDW', 'TEN', 'SE', 'FLA', 'CAR', 'MIDA', 'NY', 'NE',
                'TEX', 'CAL', 'NW', 'SW'
                ]


# For analysis copy the 'cleaned' colum over the normal 'demand' column and drop 'cleaned'.
# Drop the first day of data which shows issues for some BAs.
# Start all analysis on July 2, 2015.
def prep_for_MEM(file_path):
    print(f"prep_for_MEM: {file_path}")
    df = pd.read_csv(file_path)
    if 'cleaned demand (MW)' in df.columns:
        df['demand (MW)'] = df['cleaned demand (MW)']
    df = df.drop(['time','cleaned demand (MW)','forecast demand (MW)'], axis=1)
    df = df.drop(df.index[[i for i in range(20)]]) # Start all analysis on July 2, 2015
    df.to_csv(file_path.replace('.csv', '_for_MEM.csv'), index=False, na_rep='NA')


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
                'OVEC', 'SEC',
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
        'CONUS_from_BAs' : return_usable_BAs(),
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


    # Can be used to combine and study initial data queried from EIA
    do_raw_eia = False
    if do_raw_eia:
        for IC, regs in ICs_from_REGIONS.items():
            combine_regions(regs, IC)


        for IC, BAs in ICs_from_BAs.items():
            combine_regions(BAs, IC)


        REGIONS_from_BAs = return_BAs_per_region_map()
        grab_mean_impute = False
        grab_MICE = False # Get data from Dave's MICE runs
        for REGION, BAs in REGIONS_from_BAs.items():
            print(REGION, BAs)
            combine_regions(BAs, REGION, grab_mean_impute, grab_MICE)
        combine_regions(return_usable_BAs(), 'CONUS', grab_mean_impute, grab_MICE)


    # Use to create combinations using the simple anomaly IDing and simple imputations
    # Must have first run simple_mean_impute.py
    do_simple = False
    if do_simple:
        grab_mean_impute = True
        for IC, BAs in ICs_from_BAs.items():
            combine_regions(BAs, IC, grab_mean_impute)



    add_mice_imputations = True
    if add_mice_imputations:
        #----------------------------------------------------
        # Add the imputed demand to the original csv files
        #----------------------------------------------------
        usable_BAs = return_usable_BAs()
        for BA in usable_BAs:
            #add_MICE_imputations_to_files('~/Downloads/mean_impute_csv_MASTER_v12_2day_mice_Sept13.csv', BA)
            add_MICE_imputations_to_files('~/tmp_data4/csv_MASTER_XXX_v12_2day_mean_impute.csv', BA)


        REGIONS_from_BAs = return_BAs_per_region_map()
        grab_mean_impute = False
        grab_MICE = True # Get data from Dave's MICE runs
        combine_regions(return_usable_BAs(), 'CONUS', grab_mean_impute, grab_MICE)

        for REGION, BAs in REGIONS_from_BAs.items():
            print(REGION, BAs)
            combine_regions(BAs, REGION, grab_mean_impute, grab_MICE)

        for IC, BAs in ICs_from_BAs.items():
            combine_regions(BAs, IC, grab_mean_impute, grab_MICE)

    prepare_for_MEM = True
    if prepare_for_MEM:
        for REG in ['EASTERN_from_BAs.csv',
                    'TEXAS_from_BAs.csv',
                    'WESTERN_from_BAs.csv',
                    'CONUS_from_BAs.csv']:
            prep_for_MEM(f'data5_out2/{REG}')

