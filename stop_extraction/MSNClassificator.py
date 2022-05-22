from numpy import log as ln
from numpy import random
import pandas as pd

def modified_zscore(data_series):
    median = data_series.median()
    MAD = (abs(data_series - median)).median() * 1.4826
    return ((data_series - median) * 0.6745)/MAD

def move_stop_noise_classification(series, ths_dis, ths_dur, ths_speed, min_angle, rho):
    distance_outliers = []
    mzs_distance = modified_zscore(series['distance'])
    for i in range(len(mzs_distance)):
        if mzs_distance[i] > ths_dis:
            distance_outliers.append(i)

    direction_outliers = []
    for i in range(len(series['turning_angle']) - 1):
        if series['turning_angle'][i] < min_angle and series['turning_angle'][i+1] < min_angle:
            direction_outliers.append(i)
            direction_outliers.append(i+1)

    noise_indexes = list(set(distance_outliers).union(direction_outliers))
    clean_indexes = list(set(range(len(series))).difference(noise_indexes))
    clean_series = series.iloc[clean_indexes, :]

    duration = clean_series['duration'] + random.uniform(-rho, rho)
    duration_outliers = []
    mzs_duration = modified_zscore(duration)
    for i in mzs_duration.index:
        if mzs_duration[i] > ths_dur:
            duration_outliers.append(i)

    speed = ln(clean_series['speed'])
    speed_outliers = []
    mzs_speed = modified_zscore(speed)
    for i in mzs_speed.index:
        if mzs_speed[i] < -ths_speed:
            speed_outliers.append(i)

    stop_indexes = list(set(duration_outliers).intersection(speed_outliers))
    move_indexes = list(set(clean_indexes).difference(stop_indexes))
    return (move_indexes, stop_indexes, noise_indexes)

def move_stop_noise_classification_csv(path):
    df = pd.read_csv(path)
    return move_stop_noise_classification(df, 3.5, 5, 3.5, 45, 0.5)


p57 = move_stop_noise_classification_csv('data/trajinfo/trajinfo57.csv')
p67 = move_stop_noise_classification_csv('data/trajinfo/trajinfo67.csv')
p68 = move_stop_noise_classification_csv('data/trajinfo/trajinfo68.csv')

print(p57[1])
print(p67[1])
print(p68[1])

