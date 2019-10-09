#!/usr/bin/env python3

# 3 Sept 2019 T. Ruggles
#
#
# Very simple anomaly IDing and imputation method for basic comparisons.
# Expanding to take the "best" anomaly IDing developed my Ruggles and Farnham
# and apply simple imputation methods to that.
#


import pandas as pd
import numpy as np



def get_file(file_path):
    df = pd.read_csv(file_path,
        dtype={'demand (MW)':np.float64},
        parse_dates=True, na_values=['MISSING', 'EMPTY'])

    return df


def set_negative_to_NA(df):
    df['demand (MW)'] = df['demand (MW)'].mask(df['demand (MW)'] < 0.)
    return df


def impute_with_mean(df, region, col_to_impute='demand (MW)'):
    num_nans = df[col_to_impute].isna().sum()
    mean = np.nanmean(df[col_to_impute])
    df[col_to_impute] = df[col_to_impute].fillna(mean)
    print("{}: number NANs initially {} for {}pct flagged".format(region, num_nans, round(num_nans/len(df.index)*100., 4)))
    return df


if '__main__' in __name__:
    base = 'data2/'
    all_BAs = [
                # BAs
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
                # 'OVEC', 'SEC', # These two do not perform well and we are removing
                # them from the imputation and comparisons.
            ]
    all_BAs_and_regions = [
                # BAs
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
                # 'OVEC', 'SEC', # These two do not perform well and we are removing
                # them from the imputation and comparisons.

                # Regions
                'CENT', 'MIDW', 'TEN', 'SE', 'FLA', 'CAR', 'MIDA', 'NY', 'NE',
                'TEX',
                'CAL', 'NW', 'SW'
            ]

    print(f"{len(all_BAs_and_regions)} BAs and regions")

    do_simple = False
    print(f"do simple anomaly ID and simple impute: {do_simple}")
    if do_simple:
        for reg in all_BAs_and_regions:
            df = get_file(base+reg+'.csv')
            df = set_negative_to_NA(df)
            df = impute_with_mean(df, reg)
            #print(df.head())
            df.to_csv(base+reg+'_mean_impute.csv', index=False, na_rep=0)

    # This portion takes the output file that I normally sent to Dave for MICE imputations.
    do_complex = True
    print(f"do complex anomaly ID and simple impute: {do_complex}")
    if do_complex:
        print(f"Running complex anomaly ID and simple impute over {len(all_BAs)} BAs.")
        master = pd.read_csv('/Users/truggles/tmp_data4/csv_MASTER_XXX_v12_2day.csv')
        for reg in all_BAs:
            master = impute_with_mean(master, reg, reg)
        master.to_csv('/Users/truggles/tmp_data4/csv_MASTER_XXX_v12_2day_mean_impute.csv',
                index=False, na_rep=0)


