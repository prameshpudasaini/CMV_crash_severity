import os
import pandas as pd
import re

os.chdir(r"/Users/prameshpudasaini/Library/CloudStorage/OneDrive-UniversityofArizona/GitHub/CMV_crash_severity")

# function to remove whitespace from all columns
def remove_whitespace(xdf):
    xdf = xdf.apply(lambda col: col.str.strip() if col.dtype == 'object' or pd.api.types.is_string_dtype(col) else col)
    return xdf

# # function to extract base route name
# def extract_base_route(route):
#     route = route.strip()
#     # match standard format: starts with 'I', then optional space, 3 digits
#     match = re.match(r'^(I)\s*0*(\d{2,3})', route)
#     if match:
#         return f"{match.group(1)} {int(match.group(2)):03d}"
#     return route # retain route for unmatchables

# =============================================================================
# merged data
# =============================================================================

# read merged (incident, unit, person) data
mdf = pd.read_csv("ignore/2021-24_merged_data.csv", low_memory = False)
route_names = list(mdf.RouteName.unique())

# create milepost dataset and update route
mpdf = mdf.copy()[['IncidentID', 'RouteName', 'MPNum', 'MPOffset']]
mpdf['MP'] = mpdf['MPNum'] + mpdf['MPOffset']

# create list of baseroutename
mpdf['RouteName_base'] = mpdf['RouteName'].apply(lambda x: x[:5] if str(x).strip().startswith('I') else None)
base_route_names = list(mpdf['RouteName_base'].unique())

# # check route name and direction
# temp = mdf.copy()[['IncidentID', 'RouteName', 'GeocodeOnRoad', 'MPNum', 'MPOffset', 'Latitude', 'Longitude']]
# temp.sort_values(by = ['RouteName', 'MPNum', 'MPOffset'], inplace = True)

# =============================================================================
# functional classification
# =============================================================================

# https://adot.maps.arcgis.com/apps/MapJournal/index.html?appid=32bd9c6bf7634a29ae8997c15c88771a

# read data and select relevant columns
fc_df = pd.read_csv("ignore/Roadway Data/ADOT_Functional Classification.csv")
fc_df = fc_df[['RouteId', 'FromMeasure', 'ToMeasure', 'FunctionalClass']]

# remove whitespace and filter route names
fc_df = remove_whitespace(fc_df)
fc_df = fc_df[fc_df['RouteId'].isin(route_names)]

# inner merge where RouteName and RouteId are same
fc_mdf = mpdf.merge(fc_df, left_on = 'RouteName', right_on = 'RouteId', how = 'inner')

# filter rows where MP is between FromMeasure and ToMeasure
fc_mdf = fc_mdf[fc_mdf['MP'].between(fc_mdf['FromMeasure'], fc_mdf['ToMeasure'], inclusive = 'both')]

# remove duplicate rows
fc_mdf = fc_mdf[['IncidentID', 'RouteName', 'MP', 'FunctionalClass']]
fc_mdf.drop_duplicates(inplace = True)
fc_mdf.FunctionalClass.value_counts()
len(fc_mdf.IncidentID.unique())

# remove FunctionalClass with Nan values
fc_mdf.dropna(subset = ['FunctionalClass'], inplace = True)

# =============================================================================
# area type
# =============================================================================

# # read data
# at_df = pd.read_csv("ignore/Roadway Data/HPMS_2023_Area type.csv")

# at_df.UrbanCodeType.value_counts()
# at_df.UrbanCodeType_Value.value_counts()

# =============================================================================
# curve
# =============================================================================

# https://www.fhwa.dot.gov/policyinformation/hpms/fieldmanual/page05.cfm#toc249159732

# read data and select relevant columns
c_df = pd.read_csv("ignore/Roadway Data/HPMS_2023_Curve.csv")
c_df = c_df[['RouteId', 'FromMeasure', 'ToMeasure', 'CurveClass']]
c_df.RouteId.unique()

# remove whitespace and filter route names
c_df = remove_whitespace(c_df)
c_df = c_df[c_df['RouteId'].isin(base_route_names)]

c_df.RouteId.unique()
c_df.CurveClass.unique()

# inner merge where RouteName_base and RouteId are same
c_mdf = mpdf.merge(c_df, left_on = 'RouteName_base', right_on = 'RouteId', how = 'inner')

# filter rows where MP is between FromMeasure and ToMeasure
c_mdf = c_mdf[c_mdf['MP'].between(c_mdf['FromMeasure'], c_mdf['ToMeasure'], inclusive = 'both')]

# remove duplicate rows
c_mdf = c_mdf[['IncidentID', 'RouteName', 'MP', 'CurveClass']]
c_mdf.drop_duplicates(inplace = True)
c_mdf.CurveClass.value_counts()
len(c_mdf.IncidentID.unique())

# =============================================================================
# grade
# =============================================================================

# https://www.fhwa.dot.gov/policyinformation/hpms/fieldmanual/page05.cfm#toc249159732

# read data and select relevant columns
g_df = pd.read_csv("ignore/Roadway Data/HPMS_2023_Grade.csv")
g_df = g_df[['RouteId', 'FromMeasure', 'ToMeasure', 'GradeClass']]
g_df.RouteId.unique()

# remove whitespace and filter route names
g_df = remove_whitespace(g_df)
g_df = g_df[g_df['RouteId'].isin(base_route_names)]

g_df.RouteId.unique()
g_df.GradeClass.unique()

# inner merge where RouteName_base and RouteId are same
g_mdf = mpdf.merge(g_df, left_on = 'RouteName_base', right_on = 'RouteId', how = 'inner')

# filter rows where MP is between FromMeasure and ToMeasure
g_mdf = g_mdf[g_mdf['MP'].between(g_mdf['FromMeasure'], g_mdf['ToMeasure'], inclusive = 'both')]

# remove duplicate rows
g_mdf = g_mdf[['IncidentID', 'RouteName', 'MP', 'GradeClass']]
g_mdf.drop_duplicates(inplace = True)
g_mdf.GradeClass.value_counts()
len(g_mdf.IncidentID.unique())
