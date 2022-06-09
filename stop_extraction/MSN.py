from numpy import log as ln
from numpy import random
import pandas as pd

class MSNTrajcetorySegmentator:

    def __init__(self, series, ths_dis, ths_dur, ths_speed, min_angle, rho):
        self.series = series
        self.ths_dis = ths_dis
        self.ths_dur = ths_dur
        self.ths_speed = ths_speed
        self.min_angle = min_angle
        self.rho = rho

    def __modified_zscore(self, data_series):
        median = data_series.median()
        MAD = (abs(data_series - median)).median() * 1.4826
        return ((data_series - median) * 0.6745)/MAD

    def move_stop_noise_segmentation(self):
        distance_outliers = []
        mzs_distance = self.__modified_zscore(self.series['distance'])
        print(f"std mzs distance: {mzs_distance.std()}")
        for i in range(len(mzs_distance)):
            if mzs_distance[i] > self.ths_dis:
                distance_outliers.append(i)

        direction_outliers = []
        for i in range(len(self.series['turning_angle']) - 1):
            if self.series['turning_angle'][i] < self.min_angle and self.series['turning_angle'][i+1] < self.min_angle:
                direction_outliers.append(i)
                direction_outliers.append(i+1)

        noise_indexes = list(set(distance_outliers).union(direction_outliers))
        clean_indexes = list(set(range(len(self.series))).difference(noise_indexes))
        clean_series = self.series.iloc[clean_indexes, :]

        duration = clean_series['duration'] + random.uniform(-self.rho, self.rho)
        duration_outliers = []
        mzs_duration = self.__modified_zscore(duration)
        print(f"std mzs duration: {mzs_duration.std()}")
        for i in mzs_duration.index:
            if mzs_duration[i] > self.ths_dur:
                duration_outliers.append(i)

        speed = ln(clean_series['speed'])
        speed_outliers = []
        mzs_speed = self.__modified_zscore(speed)
        print(f"std mzs speed: {mzs_speed.std()}")
        for i in mzs_speed.index:
            if mzs_speed[i] < -self.ths_speed:
                speed_outliers.append(i)

        stop_indexes = list(set(duration_outliers).intersection(speed_outliers))
        move_indexes = list(set(clean_indexes).difference(stop_indexes))
        return (move_indexes, stop_indexes, noise_indexes)
