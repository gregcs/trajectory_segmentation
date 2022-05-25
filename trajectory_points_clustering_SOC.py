from stop_extraction import SOCStopExtractor
from stop_extraction import read_traj_points_csv
from stop_extraction import write_output_csv
import pandas as pd
import time 

def eps_tau(ratio, minimum_sampling_interval, taumult):
    return (ratio * (minimum_sampling_interval * taumult))/2, minimum_sampling_interval * taumult

def classify_point_trajectories(data_path, to_save_path, eps , tau, undefined, min_mov, save_intermediate_results = False, variable_part_filename = None):
    _, traj_points = read_traj_points_csv(data_path)
    stops = SOCStopExtractor(traj_points, eps , tau, undefined, min_mov) \
                .SOC(save_intermediate_results, 'soc_data/' + time.strftime("%Y%m%d_%H%M%S"), variable_part_filename)
    traj_points_separated_coordinates = [(id, index, x, y,timestamp, 'move') for id, index, (x, y), timestamp in traj_points]
    temp_df = pd.DataFrame(traj_points_separated_coordinates, columns=['id', 'index', 'x', 'y', 'timestamp', 'segment'])
    for i, stop in enumerate(stops):
        for point in stop:
            temp_df.at[point, 'segment'] = 'stop' + str(i)
    write_output_csv(temp_df, to_save_path)

minimum_sampling_interval = 0.071
(eps,tau) = eps_tau(0.85, minimum_sampling_interval, 5)
undefined = 1.2 * eps
min_mov = 0.5

classify_point_trajectories('data/trajectory_points/trajectory_points_57.csv', 
                                'data/trajectory_segments_SOC/trajectory_points_with_stops_57.csv', eps , tau, undefined, min_mov, True, 'person_57')

classify_point_trajectories('data/trajectory_points/trajectory_points_67.csv', 
                                'data/trajectory_segments_SOC/trajectory_points_with_stops_67.csv', eps , tau, undefined, min_mov, True, 'person_67')

classify_point_trajectories('data/trajectory_points/trajectory_points_68.csv', 
                                'data/trajectory_segments_SOC/trajectory_points_with_stops_68.csv', eps , tau, undefined, min_mov, True, 'person_68')