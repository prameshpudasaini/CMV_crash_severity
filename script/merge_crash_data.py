import os
import pandas as pd

os.chdir(r"/Users/prameshpudasaini/Library/CloudStorage/OneDrive-UniversityofArizona/GitHub/CMV_crash_severity")

# read processed incident, unit, and person datasets
file_incident = '2021-24_incident.csv'
file_unit = '2021-24_unit.csv'
file_person = '2021-24_person.csv'

idf = pd.read_csv(os.path.join("ignore", file_incident), low_memory = False)
udf = pd.read_csv(os.path.join("ignore", file_unit), low_memory = False)
pdf = pd.read_csv(os.path.join("ignore", file_person), low_memory = False)

# =============================================================================
# incident data
# =============================================================================

# add on_mainline variable: 1 if mainline, 0 if exit or ramp
idf['on_mainline'] = ~idf['GeocodeOnRoad'].str.contains('exit|ramp', case = False, na = False)
idf['on_mainline'] = idf['on_mainline'].astype(int)

# drop irrelevant columns from incident
i_cols_drop = ['TotalMotorists', 'TotalNonMotorists', 'TotalInjuries', 'TotalFatalities', 
             'TotalMotoristsInjuries', 'TotalNonMotoristsInjuries', 'TotalMotoristsFatalities', 
             'TotalNonMotoristsFatalities', 'MedicalTransportFlag', 'SchoolBusRelatedFlag',
             'HazardousFlag', 'IntersectionType', 'JunctionRelation', 'SecondaryCrashFlag']
idf.drop(i_cols_drop, axis = 1, inplace = True)

# =============================================================================
# unit data
# =============================================================================

# CMV at fault
udf['cmv_at_fault'] = (udf['UnitNumber'] == 1 & udf['BodyStyle'].isin(range(54,88+1))).astype(int)

print(f"CMV at fault: {sum(udf['cmv_at_fault'])}")
print(f"Units at fault: {sum(udf['UnitNumber'] == 1)}")

# at fault data
udf = udf[udf['UnitNumber'] == 1]
at_fault_units = list(udf.UnitID.unique())

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

# female involved in the incident
pdf['has_female'] = pdf.groupby('IncidentID')['Sex'].transform(lambda x: int('F' in x.values))

# child involved in the incident
pdf['has_child'] = pdf.groupby('IncidentID')['Age'].transform(lambda x: int((x < 14).any()))

# safety device not used by at least one person
pdf['safety_device_not_used'] = pdf.groupby('IncidentID')['SafetyDevice'].transform(lambda x: int(1 in x.values))

# airbag not deployed for at least on person
pdf['airbag_not_deployed'] = pdf.groupby('IncidentID')['Airbag'].transform(lambda x: int(1 in x.values))

# filter person data for at-fault units and driver (person type: 1)
pdf = pdf[(pdf.UnitID.isin(at_fault_units)) & (pdf['PersonType'] == 1)]

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
mdf.to_csv("ignore/2021-24_merged_data.csv", index = False)