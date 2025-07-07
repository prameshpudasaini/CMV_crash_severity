import os
import pandas as pd

os.chdir(r"/Users/prameshpudasaini/Library/CloudStorage/OneDrive-UniversityofArizona/GitHub/CMV_crash_severity")

# read processed incident, unit, and person datasets
file_incident = '2018-24_incident.csv'
file_unit = '2018-24_unit.csv'
file_person = '2018-24_person.csv'

idf = pd.read_csv(os.path.join("ignore/processed_data", file_incident), low_memory = False)
udf = pd.read_csv(os.path.join("ignore/processed_data", file_unit), low_memory = False)
pdf = pd.read_csv(os.path.join("ignore/processed_data", file_person), low_memory = False)

# =============================================================================
# incident data
# =============================================================================

# add on_mainline variable: 1 if mainline, 0 if exit or ramp
idf['on_mainline'] = ~idf['GeocodeOnRoad'].str.contains('exit|ramp', case = False, na = False)
idf['on_mainline'] = idf['on_mainline'].astype(int)

# select crashes only on the mainline
idf = idf[idf['on_mainline'] == 1]

# select single vehicle crashes
idf = idf[idf['TotalUnits'] == 1]
single_veh_incidents = list(idf['IncidentID'].unique())

# drop irrelevant columns from incident
i_cols_drop = ['TotalMotorists', 'TotalNonMotorists', 'TotalInjuries', 'TotalFatalities', 
             'TotalMotoristsInjuries', 'TotalNonMotoristsInjuries', 'TotalMotoristsFatalities', 
             'TotalNonMotoristsFatalities', 'MedicalTransportFlag', 'SchoolBusRelatedFlag',
             'HazardousFlag', 'IntersectionType', 'JunctionRelation', 'SecondaryCrashFlag',
             'on_mainline', 'TotalUnits', 'GeocodeCrossingFeatureName']
idf.drop(i_cols_drop, axis = 1, inplace = True)

# =============================================================================
# unit data
# =============================================================================

# select single vehicle incidents
udf = udf[udf['IncidentID'].isin(single_veh_incidents)]
single_veh_units = list(udf['UnitID'].unique())

# environmental condition
udf['sun_glare'] = (udf['EnvCondition1'] == 10).astype(int)
udf['stopped_vehicle'] = (udf['EnvCondition1'] == 20).astype(int)

# vehicle state code
udf['AZ_registered'] = (udf['VehicleStateCode'] == 'AZ').astype(int)

# defect1
udf['tire_related_defect'] = (udf['Defect1'] == 210).astype(int)

# surface condition
udf['is_wet_surface'] = (udf['SurfaceCondition1'] == 2).astype(int)

# distracted driving
udf['is_distracted'] = (udf['DistractedDriving1'] != 0).astype(int)

# drop irrelevant columns from unit
u_cols_drop = ['UnitID', 'UnitNumber', 'TravelDirection', 'MostHarmfulEvent', 'HitAndRunFlag',
             'RoadCondition1', 'RoadCondition2', 'EnvCondition1', 'EnvCondition2', 
             'VehicleStateCode', 'RegYear', 'BodyStyle', 'Make', 'Color', 'Defect1', 
             'Defect2', 'EventSequence3', 'EventSequence4', 'ControlType', 
             'SurfaceCondition1', 'SurfaceCondition2', 'DistractedDriving1']
udf.drop(u_cols_drop, axis = 1, inplace = True)

# =============================================================================
# person data
# =============================================================================

# select single vehicle units
pdf = pdf[pdf['UnitID'].isin(single_veh_units)]

# female involved in the incident
pdf['has_female'] = pdf.groupby('IncidentID')['Sex'].transform(lambda x: int('F' in x.values))

# child involved in the incident
pdf['has_child'] = pdf.groupby('IncidentID')['Age'].transform(lambda x: int((x < 14).any()))

# safety device not used by at least one person
pdf['safety_device_not_used'] = pdf.groupby('IncidentID')['SafetyDevice'].transform(lambda x: int(1 in x.values))

# airbag not deployed for at least on person
pdf['airbag_not_deployed'] = pdf.groupby('IncidentID')['Airbag'].transform(lambda x: int(1 in x.values))

# filter person data for driver (person type: 1)
pdf = pdf[pdf['PersonType'] == 1]

# fell asleep or fatigue
pdf['fell_asleep_fatigued'] = (pdf['Physical3'] == 3).astype(int)

# 4:alcohol, 5:drugs, or 7:marijuana involved for at-fault unit driver
pdf['DUI_involved'] = ((pdf['Physical4'] == 4) | (pdf['Physical5'] == 5) | (pdf['Physical7'] == 7)).astype(int)

# drop irrelevant columns from person
p_cols_drop = ['UnitID', 'UnitNumber', 'PersonID', 'PersonNumber', 'PersonType',
               'SafetyDevice', 'Airbag', 'InjuryStatus', 'Physical0', 'Physical1', 
               'Physical2', 'Physical3', 'Physical4', 'Physical5', 'Physical6', 
               'Physical7', 'Physical97', 'Physical99']
pdf.drop(p_cols_drop, axis = 1, inplace = True)

# =============================================================================
# merge incident, unit, and person data
# =============================================================================

mdf = idf.merge(udf, on = 'IncidentID', how = 'left')
mdf = mdf.merge(pdf, on = 'IncidentID', how = 'left')

# check injury severity values and filter for severity levels 1-5
mdf['InjurySeverity'].value_counts(dropna = False)
mdf = mdf[mdf['InjurySeverity'].isin(list([1, 2, 3, 4, 5]))]

# save file
mdf.to_csv("ignore/2018-24_merged_crash_data.csv", index = False)