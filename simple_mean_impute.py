#!/usr/bin/env python3

# 3 Sept 2019 T. Ruggles
#
#
# Very simple anomaly IDing and imputation method for basic comparisons.
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


def impute_with_mean(df, region):
    num_nans = df['demand (MW)'].isna().sum()
    mean = np.nanmean(df['demand (MW)'])
    df['demand (MW)'] = df['demand (MW)'].fillna(mean)
    print("{}: number NANs initially {}".format(region, num_nans))
    return df


if '__main__' in __name__:
    base = 'data2/'
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

    print(len(all_BAs_and_regions))

    for reg in all_BAs_and_regions:
        df = get_file(base+reg+'.csv')
        df = set_negative_to_NA(df)
        df = impute_with_mean(df, reg)
        #print(df.head())
        df.to_csv(base+reg+'_mean_impute.csv', index=False, na_rep=0)

