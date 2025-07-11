import os
import pandas as pd
import numpy as np

os.chdir(r"/Users/prameshpudasaini/Library/CloudStorage/OneDrive-UniversityofArizona/GitHub/CMV_crash_severity")

# load draft model data
df = pd.read_csv("ignore/model_data_draft.csv")
df['IncidentDateTime'] = pd.to_datetime(df['IncidentDateTime'])

# =============================================================================
# weather condition
# =============================================================================

df['Weather'].value_counts(dropna = False)
sorted(list(df['Weather'].unique()))

df['is_weather_clear_cloudy'] = (df['Weather'].isin([1,2])).astype(int)
df['is_weather_rainy_snowy'] = (df['Weather'].isin([3,4,5])).astype(int)
# df['is_weather_others'] = (df['Weather'].isin([7,8,97,99])).astype(int)

sum(df['is_weather_clear_cloudy']) + sum(df['is_weather_rainy_snowy']) - len(df)
df.drop('Weather', axis = 1, inplace = True)

# =============================================================================
# lighting condition
# =============================================================================

df['LightCondition'].value_counts(dropna = False)
sorted(list(df['LightCondition'].unique()))

# update unknown lighting condition based on incident date time
df['Hour'] = df['IncidentDateTime'].dt.hour

# function to classify light condition
def classify_light_condition(hour):
    if 5 <= hour < 7:
        return 2
    elif 7 <= hour < 18:
        return 1
    elif 18 <= hour < 20:
        return 3
    else:
        return 4
    
df.loc[df['LightCondition'] == 51, 'LightCondition'] = (
    df.loc[df['LightCondition'] == 51, 'Hour'].apply(classify_light_condition)
)
    
df['is_daylight'] = (df['LightCondition'].isin([1])).astype(int)
df['is_dawn_dusk'] = (df['LightCondition'].isin([2,3])).astype(int)
df['is_dark'] = (df['LightCondition'].isin([4,5,6])).astype(int)

sum(df['is_daylight']) + sum(df['is_dawn_dusk']) + sum(df['is_dark']) - len(df)
df.drop(['Hour', 'LightCondition'], axis = 1, inplace = True)

# =============================================================================
# miscellaneous
# =============================================================================

df['is_wet_surface'].value_counts(dropna = False)

df['sun_glare'].value_counts(dropna = False)
df.drop('sun_glare', axis = 1, inplace = True)

df['stopped_vehicle'].value_counts(dropna = False)

df['is_weekday'] = (df['day_of_week'] == 'weekday').astype(int)
df.drop('day_of_week', axis = 1, inplace = True)

# =============================================================================
# first harmful event
# =============================================================================

df['FirstHarmfulEvent'].value_counts(dropna = False)
sorted(list(df['FirstHarmfulEvent'].unique()))

df['first_harmful_overturn_rollover'] = (df['FirstHarmfulEvent'].isin([1])).astype(int)
df['first_harmful_fixed_object'] = (df['FirstHarmfulEvent'].isin([30,31,33,34,35,39,40,41,42,43,44,45,49])).astype(int)
df['first_hamrful_guardrail'] = (df['FirstHarmfulEvent'].isin([29,36,37,38,46])).astype(int)

sum(df['first_harmful_fixed_object']) + sum(df['first_hamrful_guardrail']) + sum(df['first_harmful_overturn_rollover'])
df.drop(['FirstHarmfulEvent', 'EventSequence1', 'EventSequence2'], axis = 1, inplace = True)

# =============================================================================
# age
# =============================================================================

df['Age'].describe()
df['Age'].value_counts(dropna = False)

df['is_age_young'] = np.where(df['Age'] <= 30, 1, 0)
df['is_age_middle'] = np.where(df['Age'].between(31,59), 1, 0)
df['is_age_old'] = np.where(df['Age'].between(60,130), 1, 0)

sum(df['is_age_young']) + sum(df['is_age_middle']) + sum(df['is_age_old']) - len(df)
df.drop('Age', axis = 1, inplace = True)

# =============================================================================
# sex
# =============================================================================

df['Sex'].value_counts(dropna = False)

df['is_male'] = np.where(df['Sex'] == 'M', 1, 0)
df['is_female'] = np.where(df['Sex'] == 'F', 1, 0)

sum(df['is_male']) + sum(df['is_female']) - len(df)
df.drop('Sex', axis = 1, inplace = True)

# =============================================================================
# posted speed
# =============================================================================

df['PostedSpeed'].describe()

df['is_PSL_below_65'] = np.where(df['PostedSpeed'] <= 65, 1, 0)
df.drop('PostedSpeed', axis = 1, inplace = True)

# =============================================================================
# AADT
# =============================================================================

df['log_AADT'] = np.log(df['AADT'])
df['is_AADT_trucks_below_25_percent'] = np.where(df['AADT_Trucks_Percent'] <= 25, 1, 0)
df.drop(['AADT', 'AADT_Trucks_Percent'], axis = 1, inplace = True)

# =============================================================================
# alignment and grade
# =============================================================================

df['RoadAlignment'].value_counts(dropna = False)
df['is_curve'] = (df['RoadAlignment'].isin([2,3])).astype(int)

df['RoadGrade'].value_counts(dropna = False)
df['is_grade_level'] = (df['RoadGrade'] == 1).astype(int)

df.drop(['RoadAlignment', 'RoadGrade'], axis = 1, inplace = True)

# =============================================================================
# number of lanes
# =============================================================================

df['NumberOfLanes'].value_counts(dropna = False)

df['is_lanes_2_below'] = np.where(df['NumberOfLanes'].notna(),
                                  np.where(df['NumberOfLanes'] <= 2, 1, 0),
                                  np.nan)
df['is_lanes_2_above'] = np.where(df['NumberOfLanes'] > 2, 1, 0)

sum(df['is_lanes_2_below']) + sum(df['is_lanes_2_above']) - len(df)
df.drop('NumberOfLanes', axis = 1, inplace = True)

# =============================================================================
# shoulder width
# =============================================================================

df['is_left_shoulder_short'] = np.where(df['avg_shoulder_width_left'] <= 4, 1, 0)
df['is_left_shoulder_mid'] = np.where(df['avg_shoulder_width_left'].between(4,10, inclusive = 'neither'), 1, 0)
df['is_left_shoulder_long'] = np.where(df['avg_shoulder_width_left'] >= 10, 1, 0)

df['is_right_shoulder_short'] = np.where(df['avg_shoulder_width_right'] <= 4, 1, 0)
df['is_right_shoulder_mid'] = np.where(df['avg_shoulder_width_right'].between(4,10, inclusive = 'neither'), 1, 0)
df['is_right_shoulder_long'] = np.where(df['avg_shoulder_width_right'] >= 10, 1, 0)

sum(df['is_left_shoulder_short']) + sum(df['is_left_shoulder_mid']) + sum(df['is_left_shoulder_long']) - len(df)
sum(df['is_right_shoulder_short']) + sum(df['is_right_shoulder_mid']) + sum(df['is_right_shoulder_long']) - len(df)

df.drop(['avg_shoulder_width_left', 'avg_shoulder_width_right'], axis = 1, inplace = True)
