import pandas as pd
import numpy as np

def dataPrepareTarget(file_name, empl_id='All', comp_id=True, network='E+N'):
    file_name = '3030-own'
    df = pd.read_csv(f'Data/{file_name}.csv',
                     encoding='unicode_escape')

    df.rename(columns={'Company name Latin alphabet': 'Comp_Name',
                       'Country ISO code': 'Country',
                       'NACE Rev. 2, core code (4 digits)': 'NACE',
                       'BvD ID number': 'BvD',
                       'Operating revenue (Turnover)\r\nth USD Last avail. yr': 'TURN',
                       'Cash flow\r\nth USD Last avail. yr': 'CF',
                       'Total assets\r\nth USD Last avail. yr': 'TASS',
                       'Shareholders funds\r\nth USD Last avail. yr': 'EC',
                       'Number of employees\r\nLast avail. yr': 'EM',
                       'Shareholder - BvD ID number': 'Sha_BvD',
                       'Shareholder - Direct %': 'Sha_%',
                       'Subsidiary - BvD ID number': 'Sub_BvD',
                       'Subsidiary - Direct %': 'Sub_%'
                       },
              inplace=True)

    # Codebook
    cdbk = pd.read_csv(f'Data\\Codebook.csv', index_col=0)

    # Creating dictionary so that it can be used for index in the main dataframe
    di_cdbk = dict([(bvd, index) for index, bvd in zip(cdbk.index, cdbk.BvD)])

    # Creating separate economic dataframe with attributes
    df_econ = df[['Comp_Name', 'Country', 'NACE', 'BvD', 'TURN', 'CF',
                  'TASS', 'EC', 'EM']].dropna(subset='Comp_Name')

    df_econ['index'] = df_econ['BvD'].map(di_cdbk)
    df_econ.set_index('index', inplace=True)

    # Treats the NA in column with company name and BvD-code in the main dataframe
    df['Comp_Name'].fillna(method='ffill', inplace=True)
    df['BvD'].fillna(method='ffill', inplace=True)

    import copy
    df_sub = copy.copy(df[['Comp_Name', 'BvD', 'Sub_BvD', 'Sub_%']].dropna(subset='Sub_BvD')).drop('Comp_Name', axis=1)
    df_sha = copy.copy(df[['Comp_Name', 'BvD', 'Sha_BvD', 'Sha_%', ]].dropna(subset='Sha_BvD')).drop('Comp_Name',
                                                                                                     axis=1)
    # Converting entire cells
    df_sub['Sub_%'].replace({
        'WO': 100,
        'MO': 51,
        'NG': 0.01,
        'VE': 0.01,
        '-': 0
    },
        inplace=True)

    # Removing special signs from values
    import regex
    df_sub['Sub_%'] = df_sub['Sub_%'].replace('[<>]+', '', regex=True).astype(float)

    # Renames columns
    df_sub.insert(1, 'source', df_sub['BvD'].map(di_cdbk))
    df_sub.insert(2, 'target', df_sub['Sub_BvD'].map(di_cdbk))
    df_sub.rename(columns={'Sub_%': 'weight'}, inplace=True)
    df_sub.drop(['BvD', 'Sub_BvD'], axis=1, inplace=True)

    # Keeps only present links (Drops Nans and weight 0)
    df_sub.dropna(inplace=True)
    df_sub = df_sub[df_sub['weight'] > 0]

    # Shareholders dataset
    df_sha['Sha_%'].replace({
        'WO': 100,
        'MO': 51,
        'NG': 0.01,
        'VE': 0.01,
        'FC': 0.01,
        'GP': 50,
        'BR': 0.01,
        'T': 0.01,
        'FME': 0.01,
        '-': 0
    },
        inplace=True)

    import regex
    df_sha['Sha_%'] = df_sha['Sha_%'].replace('[<>]+', '', regex=True).astype(float)

    # Renames columns
    df_sha.insert(1, 'source', df_sha['Sha_BvD'].map(di_cdbk))
    df_sha.insert(2, 'target', df_sha['BvD'].map(di_cdbk))
    df_sha.rename(columns={'Sha_%': 'weight'}, inplace=True)
    df_sha.drop(['BvD', 'Sha_BvD'], axis=1, inplace=True)

    # Keeps only present links (Drops Nans and weight 0)
    df_sha.dropna(inplace=True)
    df_sha = df_sha[df_sha['weight'] > 0]

    # All E+N links
    df_E_N = pd.concat([df_sha, df_sub]).drop_duplicates(subset=['source', 'target'])






    # Extraction of EASIN
    newDict = {key: value for (key, value) in di_cdbk.items() if str(value).startswith('Targi')}
    df_EASIN = df_E_N[(df_E_N['source'].isin(newDict.values())) & (df_E_N['target'].isin(newDict.values()))]
