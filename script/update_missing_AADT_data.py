import os
import pandas as pd

os.chdir(r"/Users/prameshpudasaini/Library/CloudStorage/OneDrive-UniversityofArizona/GitHub/CMV_crash_severity")

# =============================================================================
# merged dataset
# =============================================================================

# load merged crash and roadway data
df = pd.read_csv("ignore/2018-24_merged_crash_roadway_data.csv")

# datetime conversion
df['IncidentDateTime'] = pd.to_datetime(df['IncidentDateTime'], format = '%m/%d/%Y %I:%M:%S %p')

# get AADT for trucks
df['AADT_Trucks_Percent'] = round((df['AADTSingleUnit'] + df['AADTCombination']) / df['AADT'] * 100, 2)
df.drop(['AADTSingleUnit', 'AADTCombination'], axis = 1, inplace = True)

# update milepost
df['MILE_POST'] = df['MPNum'] + df['MPOffset']

# =============================================================================
# AADT and Location data for I-17 from CATS01 server
# =============================================================================

# load AADT and Location datasets
# data downloaded by Moin
adf = pd.read_excel("ignore/missing_AADT_data/AADT_2023.xlsx")
ldf = pd.read_excel("ignore/missing_AADT_data/Location.xlsx")

# select relevant variables
adf.columns
aadt_cols = ['local_id', 'aadt', 'aadt_trucks', 'aadt_single_trucks', 'aadt_combo_trucks']
adf = adf[aadt_cols]

ldf.columns
loc_cols = ['LOCAL_ID', 'ON_ROAD', 'DIR', 'LATITUDE', 'LONGITUDE', 'MILE_POST']
ldf = ldf[loc_cols]

# select bi-directional AADT location IDs on I-17
ldf['DIR'].unique()
ldf = ldf[(ldf['ON_ROAD'] == 'I 17') & (ldf['DIR'] == '2-WAY')]
# local_ids = list(ldf['LOCAL_ID'].unique())

# merge aadt and location data
mdf = pd.merge(adf, ldf, left_on = 'local_id', right_on = 'LOCAL_ID', how = 'inner')
mdf = mdf[['MILE_POST', 'aadt', 'aadt_trucks']]

# sort data by mile post
mdf.sort_values('MILE_POST', inplace = True)
mdf.dropna(subset = 'MILE_POST', inplace = True)

# compute percentage of truck AADT
mdf['aadt_trucks_percent'] = round(mdf['aadt_trucks'] / mdf['aadt'] * 100, 2)
mdf.drop('aadt_trucks', axis = 1, inplace = True)

# update missing percent trucks data
mdf.loc[(mdf['MILE_POST'].between(310, 335)) & (mdf['aadt_trucks_percent'].isna()), 'aadt_trucks_percent'] = 27
mdf.loc[(~mdf['MILE_POST'].between(310, 335)) & (mdf['aadt_trucks_percent'].isna()), 'aadt_trucks_percent'] = 10

# =============================================================================
# update missing AADT data for I-17
# =============================================================================

# filter data for I-17 and sort by mile post
df17 = df.copy()[df['GeocodeOnRoad'].str.contains('I-17')]
df17.sort_values('MILE_POST', inplace = True)

# perform nearest merge
df17_new = pd.merge_asof(df17, mdf, on = 'MILE_POST', direction = 'nearest')

# update AADT and AADT Truck Percent
df17_new['AADT'] = df17_new['aadt']
df17_new['AADT_Trucks_Percent'] = df17_new['aadt_trucks_percent']
df17_new.drop(['aadt', 'aadt_trucks_percent'], axis = 1, inplace = True)

# =============================================================================
# update original dataset
# =============================================================================

# remove data for I-17 with missing AADT values
df_new = df.copy()[~df['GeocodeOnRoad'].str.contains('I-17', na = False)]

# add data for I-17 with filled AADT values
fdf = pd.concat([df_new, df17_new], ignore_index = True)

# remove observations with missing AADT values
fdf.dropna(subset = 'AADT', inplace = True)
fdf.drop(['RouteName', 'MILE_POST'], axis = 1, inplace = True)

# save file
fdf.to_csv("ignore/2018-24_merged_crash_roadway_data_updated.csv", index = False)
