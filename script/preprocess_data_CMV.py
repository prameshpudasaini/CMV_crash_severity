import os
import pandas as pd

os.chdir(r"/Users/prameshpudasaini/Library/CloudStorage/OneDrive-UniversityofArizona/GitHub/secondary_crash")

def remove_whitespace(xdf):
    xdf = xdf.apply(lambda col: col.str.strip() if col.dtype == 'object' or pd.api.types.is_string_dtype(col) else col)
    return xdf

year = 2024
file_unit = 'AZ_Unit_Data_' + str(year) + '.csv'
file_incident = 'AZ_Incident_Data_' + str(year) + '.csv'
file_person = 'AZ_Person_Data_' + str(year) + '.csv'
path_unit = os.path.join("ignore/AZ_Crash_Data/AZ_Crash_Data", file_unit)
path_incident = os.path.join("ignore/AZ_Crash_Data/AZ_Crash_Data", file_incident)
path_person = os.path.join("ignore/AZ_Crash_Data/AZ_Crash_Data", file_person)

print(f"Year: {year}")

# =============================================================================
# filter CMV crashes from unit data
# =============================================================================

# read unit data and remove whitespace
unit = pd.read_csv(path_unit, low_memory = False)
unit = remove_whitespace(unit)
print(f"\nTotal crashes in unit: {len(unit.IncidentID.unique())}") # 122,625

# filter CMV crashes
trucks = unit['BodyStyle'].isin(range(54,88+1)) # 54-88 as per ACIS User Guide
buses = unit['BusFlag'] == 1
GVWR = unit['GVWRFlag'] == 1
hazmats = unit['HazmatFlag'] == 1

print(f"Truck crashes: {len(unit[trucks].IncidentID.unique())}") # 15,044
print(f"Bus crashes: {len(unit[buses].IncidentID.unique())}") # 790
print(f"GVWR crashes: {len(unit[GVWR].IncidentID.unique())}") # 6,420
print(f"Hazmat crashes: {len(unit[hazmats].IncidentID.unique())}") # 0

# exclude buses for CMVs
# udf = unit.copy()[trucks | buses | GVWR | hazmats]
# print(f"CMV crashes: {len(udf.IncidentID.unique())}") # 15,044
udf = unit.copy()[trucks | GVWR | hazmats]
print(f"CMV crashes: {len(udf.IncidentID.unique())}") # 17,296

# CMV incidents
cmv_incidents = list(udf['IncidentID'].unique())

# CMV at fault
udf['CMV_at_fault'] = (udf['UnitNumber'] == 1 & udf['BodyStyle'].isin(range(54,88+1))).astype(int)
cmv_at_fault_incidents = list(udf[udf['CMV_at_fault'] == 1].IncidentID.unique()) # 8,411

# =============================================================================
# filter interstate crashes from incident data
# =============================================================================

# read incident data and remove whitespace
incident = pd.read_csv(path_incident, low_memory = False)
# print(f"{len(incident.GeocodeOnRoad.unique())}")
incident = remove_whitespace(incident)
# print(f"{len(incident.GeocodeOnRoad.unique())}")
print(f"\nTotal crashes in incident: {incident.shape[0]}") # 122,625

# filter crashes on interstates
interstates = ['I-8', 'I-10', 'I-15', 'I-17', 'I-19', 'I-40']
interstate_crashes = incident['GeocodeOnRoad'].str.contains('|'.join(interstates), na = False)
idf = incident.copy()[interstate_crashes]
print(f"Interstate crashes: {idf.shape[0]}") # 18,053

# exclude crashes on frontage roads
idf = idf[~idf['GeocodeOnRoad'].str.contains('frontage', case = False, na = False)]
print(f"Interstate crashes (excluding frontage): {idf.shape[0]}") # 17,203

# check unique GeocodeOnRoad values
temp = idf.GeocodeOnRoad.value_counts().reset_index()
# print(f"{idf.GeocodeOnRoad.value_counts()}")

# =============================================================================
# filter interstate CMV crashes with lane departure
# =============================================================================

# filter interstate cmv crashes
cdf = idf.copy()[idf['IncidentID'].isin(cmv_incidents)]
print(f"\nInterstate CMV crashes: {cdf.shape[0]}") # 4,102

print("\nSeverity of interstate CMV crashes:")
print(cdf['InjurySeverity'].value_counts())

# filter interstate cmv crashes with lane departure
lane_depart_events = [1,11,12,13,14,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49]
cdf = cdf[cdf['FirstHarmfulEvent'].isin(lane_depart_events)]
print(f"\nInterstate CMV crashes with lane departure: {cdf.shape[0]}") # 399

print("\nSeverity of interstate CMV crashes with lane departure:")
print(cdf['InjurySeverity'].value_counts())

i_cmv_crashes_lane_depart = list(cdf['IncidentID'].unique())

# =============================================================================
# select relevant columns
# =============================================================================

# read person data and remove whitespace
person = pd.read_csv(path_person, low_memory = False)
person = remove_whitespace(person)
print(f"\nTotal crashes in person: {person.IncidentID.unique().shape[0]}") # 122,625

cols_incident = ['IncidentID',
       'IncidentDateTime',
       'CollisionManner', 'LightCondition', 'FirstHarmfulEvent',
       'TotalUnits', 'TotalMotorists',
       'TotalNonMotorists', 'TotalInjuries', 'TotalFatalities',
       'TotalMotoristsInjuries', 'TotalNonMotoristsInjuries',
       'TotalMotoristsFatalities', 'TotalNonMotoristsFatalities',
       'InjurySeverity', 'MedicalTransportFlag', 'FatalAccidentFlag',
       'TowAwayFlag', 'SchoolBusRelatedFlag',
       'WorkZoneRelatedFlag', 'AlcoholInvolvementFlag',
       'DrugInvolvementFlag', 'HazardousFlag', 'HitAndRunFlag', 'RouteName',
       'MPNum', 'MPOffset',
       'Latitude', 'Longitude',
       'TrafficWayType',
       'IntersectionType', 'JunctionRelation', 'Weather',
       'SecondaryCrashFlag', 'GeocodeOnRoad', 'GeocodeCrossingFeatureName']

cols_unit = ['IncidentID', 'UnitID', 'UnitNumber',
       'TravelDirection', 'RoadAlignment',
       'RoadGrade', 'Lane',
       'UnitAction', 'MostHarmfulEvent',
       'HitAndRunFlag', 'RoadCondition1',
       'RoadCondition2',
       'EnvCondition1', 'EnvCondition2',
       'VehicleStateCode',
       'RegYear', 'BodyStyle', 'Make',
       'Color',
       'PostedSpeed', 'EstimatedSpeed',
       'Defect1', 'Defect2',
       'EventSequence1',
       'EventSequence2', 'EventSequence3',
       'EventSequence4',
       'ControlType', 'SurfaceCondition1',
       'SurfaceCondition2',
       'DistractedDriving1', 'CMV_at_fault']

cols_person = ['IncidentID', 'UnitID', 'UnitNumber', 'PersonID', 'PersonNumber',
       'PersonType', 'Age', 'Sex', 'SafetyDevice',
       'Airbag', 'InjuryStatus',
       'Violation1', 'Violation2',
       'Physical0', 'Physical1', 'Physical2', 'Physical3', 'Physical4',
       'Physical5', 'Physical6', 'Physical7', 'Physical97', 'Physical99']

# filter person data for interstate cmv crashes with lane departure
pdf = person.copy()[person['IncidentID'].isin(i_cmv_crashes_lane_depart)]

# incident, unit, person data
cdf = cdf[cols_incident]
udf = udf[cols_unit]
pdf = pdf[cols_person]

cdf.to_csv("ignore/2023_incident.csv", index = False)
udf.to_csv("ignore/2023_unit.csv", index = False)
pdf.to_csv("ignore/2023_person.csv", index = False)
