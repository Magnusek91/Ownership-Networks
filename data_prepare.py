import pandas as pd
import numpy as np

def dataPrepareTarget(file_name, empl_id='All', comp_id=True):
    df = pd.read_csv(f'Data\\Input\\{file_name}.csv',
                     encoding='unicode_escape',
                     usecols=['Company name Latin alphabet',
                              'BvD ID number',
                              'DM\nUCI (Unique Contact Identifier)',
                              'DM\nType of role']