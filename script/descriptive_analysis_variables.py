import os
import pandas as pd

os.chdir(r"/Users/prameshpudasaini/Library/CloudStorage/OneDrive-UniversityofArizona/GitHub/CMV_crash_severity")

# =============================================================================
# load data and process temporal variables
# =============================================================================

# load merged crash and roadway data
df = pd.read_csv("ignore/2018-24_merged_crash_roadway_data_updated.csv")
print(f"Unique incidents: {len(df.IncidentID.unique())}")

# datetime conversion
df['IncidentDateTime'] = pd.to_datetime(df['IncidentDateTime'])

# add weekend/weekday variable
df['day_of_week'] = df['IncidentDateTime'].dt.dayofweek.apply(lambda x: 'weekend' if x >= 5 else 'weekday')

# add time of day variable
def classify_time(hour):
    if 7 <= hour < 19:
        return 'daytime'
    elif 19 <= hour <= 23:
        return 'evening'
    else:
        return 'night'
    
df['time_of_day'] = df['IncidentDateTime'].dt.hour.apply(classify_time)

# =============================================================================
# update missing shoulder data
# =============================================================================

# load data with missing values manually collected
sdf = pd.read_csv("ignore/missing_shoulder_lanes_data/2018-24_merged_crash_roadway_data_updated_shoulder.csv")
sdf = sdf[['IncidentID', 'NumberOfLanes', 'avg_shoulder_width_left', 'avg_shoulder_width_right']]

# update values in df
df.set_index('IncidentID', inplace = True)
sdf.set_index('IncidentID', inplace = True)
df.update(sdf[['NumberOfLanes', 'avg_shoulder_width_left', 'avg_shoulder_width_right']])
df.reset_index(inplace = True)

# =============================================================================
# mising/unknown age and sex
# =============================================================================

df['Sex'].value_counts(dropna = False)
df['Age'].describe()

df = df[df['Sex'].isin(['M', 'F'])]
df['Sex'].value_counts(dropna = False)

df = df[df['Age'] <= 150]

# =============================================================================
# descriptive summary
# =============================================================================

# define categorical and continuous variables
df.columns

cat_vars = ['CollisionManner', 'LightCondition',
       'FirstHarmfulEvent', 'InjurySeverity',
       'FatalAccidentFlag', 'TowAwayFlag', 'WorkZoneRelatedFlag',
       'AlcoholInvolvementFlag', 'DrugInvolvementFlag', 'HitAndRunFlag',
       'TrafficWayType', 'Weather',
       'RoadAlignment', 'Lane',
       'RoadGrade', 'UnitAction', 'PostedSpeed',
       'EventSequence1', 'EventSequence2', 'sun_glare',
       'stopped_vehicle', 'AZ_registered', 'tire_related_defect',
       'is_wet_surface', 'is_distracted', 'Sex', 'Violation1',
       'Violation2', 'has_female', 'has_child', 'safety_device_not_used',
       'airbag_not_deployed', 'fell_asleep_fatigued', 'DUI_involved',
       'CurveClass', 'GradeClass', 'TerrainType', 'MedianType',
       'NumberOfLanes', 'LeftShoulderType',
       'RightShoulderType',
       'day_of_week', 'time_of_day']

num_vars = ['Lane', 'EstimatedSpeed', 'Age',
       'avg_median_width', 'NumberOfLanes', 'avg_shoulder_width_left',
       'avg_shoulder_width_right', 'AADT', 'AADT_Trucks_Percent']

# temp = df.drop(['avg_median_width', 'TerrainType'], axis = 1)
# temp.dropna(inplace = True)

# summarize info for categorical variables
for var in cat_vars:
    counts = df[var].value_counts(dropna = False)
    percents = df[var].value_counts(normalize = True, dropna = False) * 100
    summary = pd.DataFrame({'count': counts, 'percent': percents.round(2)})
    print(summary)
    print("")

# summarize info for continuous variables    
cont_summary = df[num_vars].describe().T[['min', 'mean', 'std', '25%', '50%', '75%', 'max']]
cont_summary['missing'] = df[num_vars].isna().sum()

# =============================================================================
# select columns for modeling
# =============================================================================

model_cols = ['IncidentID', 'IncidentDateTime', 'InjurySeverity', 'Weather', 'LightCondition',
             'is_wet_surface', 'sun_glare', 'stopped_vehicle',
             'day_of_week',
             'FirstHarmfulEvent', 'EventSequence1', 'EventSequence2',
             'AZ_registered', 'tire_related_defect', 'airbag_not_deployed', 
             'has_female', 'has_child',
             'Age', 'Sex', 'DUI_involved', 'safety_device_not_used', 'is_distracted',
             'fell_asleep_fatigued',
             'PostedSpeed', 'AADT', 'AADT_Trucks_Percent', 'RoadAlignment', 'RoadGrade',
             'NumberOfLanes', 'avg_shoulder_width_left', 'avg_shoulder_width_right']

# select variables
mdf = df.copy()[model_cols]
mdf.to_csv("ignore/model_data_draft.csv", index = False)
