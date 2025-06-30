import os
import pandas as pd
# import re
from functools import reduce

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

# =============================================================================
# terrain
# =============================================================================

# read data and select relevant columns
t_df = pd.read_csv("ignore/Roadway Data/HPMS_2023_Terraain type.csv")
t_df = t_df[['RouteId', 'FromMeasure', 'ToMeasure', 'TerrainType']]
t_df.RouteId.unique()

# remove whitespace and filter route names
t_df = remove_whitespace(t_df)
t_df = t_df[t_df['RouteId'].isin(route_names)]

t_df.RouteId.unique()
t_df.TerrainType.unique()

# inner merge where RouteName_base and RouteId are same
t_mdf = mpdf.merge(t_df, left_on = 'RouteName', right_on = 'RouteId', how = 'inner')

# filter rows where MP is between FromMeasure and ToMeasure
t_mdf = t_mdf[t_mdf['MP'].between(t_mdf['FromMeasure'], t_mdf['ToMeasure'], inclusive = 'both')]

# remove duplicate rows
t_mdf = t_mdf[['IncidentID', 'RouteName', 'MP', 'TerrainType']]
t_mdf.drop_duplicates(inplace = True)

t_mdf.TerrainType.value_counts()
len(t_mdf.IncidentID.unique())

# =============================================================================
# median
# =============================================================================

# read data and select relevant columns
m_df = pd.read_csv("ignore/Roadway Data/HPMS_2023_Median.csv")

# compute average median width
m_df['avg_median_width'] = round((m_df['BeginWidthFt'] + m_df['EndWidthFt'])/2, 1)
m_df = m_df[['RouteId', 'FromMeasure', 'ToMeasure', 'MedianType', 'avg_median_width']]
m_df.RouteId.unique()

# remove whitespace and filter route names
m_df = remove_whitespace(m_df)
m_df = m_df[m_df['RouteId'].isin(route_names)]

m_df.RouteId.unique()
m_df.MedianType.unique()

# inner merge where RouteName_base and RouteId are same
m_mdf = mpdf.merge(m_df, left_on = 'RouteName', right_on = 'RouteId', how = 'inner')

# filter rows where MP is between FromMeasure and ToMeasure
m_mdf = m_mdf[m_mdf['MP'].between(m_mdf['FromMeasure'], m_mdf['ToMeasure'], inclusive = 'both')]

# remove duplicate rows
m_mdf = m_mdf[['IncidentID', 'RouteName', 'MP', 'MedianType', 'avg_median_width']]
m_mdf.drop_duplicates(inplace = True)

m_mdf.MedianType.value_counts()
len(m_mdf.IncidentID.unique())

# =============================================================================
# lanes
# =============================================================================

# read data and select relevant columns
l_df = pd.read_csv("ignore/Roadway Data/HPMS_2023_Lanes.csv")
l_df = l_df[['RouteId', 'FromMeasure', 'ToMeasure', 'NumberOfLanes']]
l_df.RouteId.unique()

# remove whitespace and filter route names
l_df = remove_whitespace(l_df)
l_df = l_df[l_df['RouteId'].isin(route_names)]

l_df.RouteId.unique()

# inner merge where RouteName_base and RouteId are same
l_mdf = mpdf.merge(l_df, left_on = 'RouteName', right_on = 'RouteId', how = 'inner')

# filter rows where MP is between FromMeasure and ToMeasure
l_mdf = l_mdf[l_mdf['MP'].between(l_mdf['FromMeasure'], l_mdf['ToMeasure'], inclusive = 'both')]

# remove duplicate rows
l_mdf = l_mdf[['IncidentID', 'RouteName', 'MP', 'NumberOfLanes']]
l_mdf.drop_duplicates(inplace = True)

l_mdf.NumberOfLanes.value_counts()
len(l_mdf.IncidentID.unique())

# =============================================================================
# left shoulder type
# =============================================================================

# read data and select relevant columns
ls_df = pd.read_csv("ignore/Roadway Data/HPMS_2023_Left shoulder type.csv")
ls_df = ls_df[['RouteId', 'FromMeasure', 'ToMeasure', 'SurfaceType']]
ls_df.RouteId.unique()

# remove whitespace and filter route names
ls_df = remove_whitespace(ls_df)
ls_df = ls_df[ls_df['RouteId'].isin(route_names)]

ls_df.RouteId.unique()
ls_df.SurfaceType.unique()

# inner merge where RouteName_base and RouteId are same
ls_mdf = mpdf.merge(ls_df, left_on = 'RouteName', right_on = 'RouteId', how = 'inner')

# filter rows where MP is between FromMeasure and ToMeasure
ls_mdf = ls_mdf[ls_mdf['MP'].between(ls_mdf['FromMeasure'], ls_mdf['ToMeasure'], inclusive = 'both')]

# remove duplicate rows
ls_mdf = ls_mdf[['IncidentID', 'RouteName', 'MP', 'SurfaceType']]
ls_mdf.drop_duplicates(inplace = True)
ls_mdf.rename(columns = {'SurfaceType': 'LeftShoulderType'}, inplace = True)

ls_mdf.LeftShoulderType.value_counts()
len(ls_mdf.IncidentID.unique())

# =============================================================================
# right shoulder type
# =============================================================================

# read data and select relevant columns
rs_df = pd.read_csv("ignore/Roadway Data/HPMS_2023_Right shoulder type.csv")
rs_df = rs_df[['RouteId', 'FromMeasure', 'ToMeasure', 'SurfaceType']]
rs_df.RouteId.unique()

# remove whitespace and filter route names
rs_df = remove_whitespace(rs_df)
rs_df = rs_df[rs_df['RouteId'].isin(route_names)]

rs_df.RouteId.unique()
rs_df.SurfaceType.unique()

# inner merge where RouteName_base and RouteId are same
rs_mdf = mpdf.merge(rs_df, left_on = 'RouteName', right_on = 'RouteId', how = 'inner')

# filter rows where MP is between FromMeasure and ToMeasure
rs_mdf = rs_mdf[rs_mdf['MP'].between(rs_mdf['FromMeasure'], rs_mdf['ToMeasure'], inclusive = 'both')]

# remove duplicate rows
rs_mdf = rs_mdf[['IncidentID', 'RouteName', 'MP', 'SurfaceType']]
rs_mdf.drop_duplicates(inplace = True)
rs_mdf.rename(columns = {'SurfaceType': 'RightShoulderType'}, inplace = True)

rs_mdf.RightShoulderType.value_counts()
len(rs_mdf.IncidentID.unique())

# =============================================================================
# left shoulder width
# =============================================================================

# read data and select relevant columns
swl_df = pd.read_csv("ignore/Roadway Data/HPMS_2023_shoulder_width_left.csv")

# compute avg shoulder width
swl_df['avg_shoulder_width_left'] = round((swl_df['BegShoulderWidthFt'] + swl_df['EndShoulderWidthFt'])/2, 1)
swl_df = swl_df[['RouteId', 'FromMeasure', 'ToMeasure', 'avg_shoulder_width_left']]
swl_df.RouteId.unique()

# remove whitespace and filter route names
swl_df = remove_whitespace(swl_df)
swl_df = swl_df[swl_df['RouteId'].isin(route_names)]

swl_df.RouteId.unique()

# inner merge where RouteName_base and RouteId are same
swl_mdf = mpdf.merge(swl_df, left_on = 'RouteName', right_on = 'RouteId', how = 'inner')

# filter rows where MP is between FromMeasure and ToMeasure
swl_mdf = swl_mdf[swl_mdf['MP'].between(swl_mdf['FromMeasure'], swl_mdf['ToMeasure'], inclusive = 'both')]

# remove duplicate rows
swl_mdf = swl_mdf[['IncidentID', 'RouteName', 'MP', 'avg_shoulder_width_left']]
swl_mdf.drop_duplicates(inplace = True)

len(swl_mdf.IncidentID.unique())

# =============================================================================
# right shoulder width
# =============================================================================

# read data and select relevant columns
swr_df = pd.read_csv("ignore/Roadway Data/HPMS_2023_shoulder_width_right.csv")

# compute avg shoulder width
swr_df['avg_shoulder_width_right'] = round((swr_df['BegShoulderWidthFt'] + swr_df['EndShoulderWidthFt'])/2, 1)
swr_df = swr_df[['RouteId', 'FromMeasure', 'ToMeasure', 'avg_shoulder_width_right']]
swr_df.RouteId.unique()

# remove whitespace and filter route names
swr_df = remove_whitespace(swr_df)
swr_df = swr_df[swr_df['RouteId'].isin(route_names)]

swr_df.RouteId.unique()

# inner merge where RouteName_base and RouteId are same
swr_mdf = mpdf.merge(swr_df, left_on = 'RouteName', right_on = 'RouteId', how = 'inner')

# filter rows where MP is between FromMeasure and ToMeasure
swr_mdf = swr_mdf[swr_mdf['MP'].between(swr_mdf['FromMeasure'], swr_mdf['ToMeasure'], inclusive = 'both')]

# remove duplicate rows
swr_mdf = swr_mdf[['IncidentID', 'RouteName', 'MP', 'avg_shoulder_width_right']]
swl_mdf.drop_duplicates(inplace = True)

len(swr_mdf.IncidentID.unique())

# =============================================================================
# AADT
# =============================================================================

# read data and select relevant columns
aadt_df = pd.read_csv("ignore/Roadway Data/HPMS_2023_AADT.csv")
aadt_df = aadt_df[['RouteId', 'FromMeasure', 'ToMeasure', 'AADT']]
aadt_df.RouteId.unique()

# remove whitespace and filter route names
aadt_df = remove_whitespace(aadt_df)
aadt_df = aadt_df[aadt_df['RouteId'].isin(base_route_names)]

aadt_df.RouteId.unique()

# inner merge where RouteName_base and RouteId are same
aadt_mdf = mpdf.merge(aadt_df, left_on = 'RouteName_base', right_on = 'RouteId', how = 'inner')

# filter rows where MP is between FromMeasure and ToMeasure
aadt_mdf = aadt_mdf[aadt_mdf['MP'].between(aadt_mdf['FromMeasure'], aadt_mdf['ToMeasure'], inclusive = 'both')]

# remove duplicate rows
aadt_mdf = aadt_mdf[['IncidentID', 'RouteName', 'MP', 'AADT']]
aadt_mdf.drop_duplicates(inplace = True)

len(aadt_mdf.IncidentID.unique())

# =============================================================================
# AADT single unit truck
# =============================================================================

# read data and select relevant columns
aadt_sut_df = pd.read_csv("ignore/Roadway Data/HPMS_2023_AADT_singleunittruck.csv")
aadt_sut_df = aadt_sut_df[['RouteId', 'FromMeasure', 'ToMeasure', 'AADTSingleUnit']]
aadt_sut_df.RouteId.unique()

# remove whitespace and filter route names
aadt_sut_df = remove_whitespace(aadt_sut_df)
aadt_sut_df = aadt_sut_df[aadt_sut_df['RouteId'].isin(base_route_names)]

aadt_sut_df.RouteId.unique()

# inner merge where RouteName_base and RouteId are same
aadt_sut_mdf = mpdf.merge(aadt_sut_df, left_on = 'RouteName_base', right_on = 'RouteId', how = 'inner')

# filter rows where MP is between FromMeasure and ToMeasure
aadt_sut_mdf = aadt_sut_mdf[aadt_sut_mdf['MP'].between(aadt_sut_mdf['FromMeasure'], aadt_sut_mdf['ToMeasure'], inclusive = 'both')]

# remove duplicate rows
aadt_sut_mdf = aadt_sut_mdf[['IncidentID', 'RouteName', 'MP', 'AADTSingleUnit']]
aadt_sut_mdf.drop_duplicates(inplace = True)

len(aadt_sut_mdf.IncidentID.unique())

# =============================================================================
# merge all roadway info
# =============================================================================

# list of datasets with roadway info for unique incidents
road_df_list = [c_mdf, g_mdf, t_mdf, m_mdf, l_mdf, ls_mdf, rs_mdf, swl_mdf, swr_mdf, aadt_mdf, aadt_sut_mdf]

# remove RouteName and MP columns
road_df_list = [df.drop(columns = ['RouteName', 'MP'], errors = 'ignore') for df in road_df_list]

# merge all on IncidentID
road_df = reduce(lambda left, right: pd.merge(left, right, on = 'IncidentID', how = 'outer'), road_df_list)

# =============================================================================
# merge roadway and crash info
# =============================================================================

fdf = pd.merge(mdf, road_df, on = 'IncidentID', how = 'outer')
fdf.columns

df_num = fdf.describe(include = [float, int]).T
df_cat = fdf.describe(include = 'object').T

fdf.to_csv("ignore/merged_crash_roadway_data.csv", index = False)
