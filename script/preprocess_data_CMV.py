import os
import pandas as pd

os.chdir(r"/Users/prameshpudasaini/Library/CloudStorage/OneDrive-UniversityofArizona/GitHub/secondary_crash")

# =============================================================================
# filter CMV crashes from unit data
# =============================================================================

# read unit data
unit = pd.read_csv("ignore/AZ_Crash_Data/AZ_Crash_Data/AZ_Unit_Data_2023.csv")
print(f"Total crashes: {len(unit.IncidentID.unique())}") # 122,625

# filter CMV crashes
trucks = unit['BodyStyle'].isin(range(54,88+1)) # 54-88 as per ACIS User Guide
buses = unit['BusFlag'] == 1
GVWR = unit['GVWRFlag'] == 1
hazmats = unit['HazmatFlag'] == 1

print(f"Truck crashes: {len(unit[trucks].IncidentID.unique())}") # 15,044 
udf = unit.copy()[trucks | buses | GVWR | hazmats]
print(f"CMV crashes (trucks+buses+GVWR+hazmats): {len(udf.IncidentID.unique())}\n") # 17,450

# CMV incidents
cmv_incidents = list(udf['IncidentID'].unique())

# =============================================================================
# filter interstate crashes from incident data
# =============================================================================

# read incident data
incident = pd.read_csv("ignore/AZ_Crash_Data/AZ_Crash_Data/AZ_Incident_Data_2023.csv")
# print(f"Total crashes: {incident.shape[0]}") # 122,625

# filter crashes on interstates
interstates = ['I-8', 'I-10', 'I-15', 'I-17', 'I-19', 'I-40']
interstate_crashes = incident['GeocodeOnRoad'].str.contains('|'.join(interstates), na = False)
idf = incident.copy()[interstate_crashes]
print(f"Interstate crashes: {idf.shape[0]}\n") # 18,053

# =============================================================================
# filter interstate CMV crashes with lane departure
# =============================================================================

# filter interstate cmv crashes
cdf = idf.copy()[idf['IncidentID'].isin(cmv_incidents)]
print(f"Interstate CMV crashes: {cdf.shape[0]}") # 4,288

# list of interstate cmv crashes
interstate_cmv_crashes = list(cdf['IncidentID'].unique())

# save incident and unit data for interstate cmv crashes
cdf.to_csv("ignore/interstate_cmv_crashes_incident.csv", index = False)
temp_unit = unit[unit['IncidentID'].isin(interstate_cmv_crashes)]
temp_unit.to_csv("ignore/interstate_cmv_crashes_unit.csv", index = False)

# check
cdf['TotalUnits'].sum() == len(temp_unit)



cdf['InjurySeverity'].value_counts()
cdf['CollisionManner'].value_counts()

cdf[['InjurySeverity', 'CollisionManner']].value_counts()

# filter interstate cmv crashes with lane departure
lane_depart_crashes = [5, 6, 7]
cdf = cdf[cdf['CollisionManner'].isin(lane_depart_crashes)]
print(f"Interstate CMV crashes with lane departure: {cdf.shape[0]}\n") # 1,782

print(f"Injurity severity for these crashes: \n {cdf.InjurySeverity.value_counts()}")

# =============================================================================
# person data
# =============================================================================

person = pd.read_csv("ignore/AZ_Crash_Data/AZ_Crash_Data/AZ_Person_Data_2023.csv")
print(list(person.columns))

cols_person = [
    'IncidentID', 'UnitID', 'PersonID', 'PersonType',
    'Age', 'Sex', 'Airbag', 'InjuryStatus', 'Violation1', 'Violation2'
]

pdf = person.copy(cols_person)
