from stop_extraction import SOCStopExtractor
import pandas as pd
import time 

def read_csv(path):
    df = pd.read_csv(path)
    id = df['id'].tolist()
    x = df['x'].tolist()
    y = df['y'].tolist()
    timestamp = df['timestamp'].tolist()
    return [(id[i], i, (x[i],y[i]),timestamp[i]) for i in range(len(df))]

def write_output(path, traj_points, stops):
    traj_points_separated_coordinates = [(id, index, x, y,timestamp, 'move') for id, index, (x, y), timestamp in traj_points]
    temp_df = pd.DataFrame(traj_points_separated_coordinates, columns=['id', 'index', 'x', 'y', 'timestamp', 'segment'])
    for i, stop in enumerate(stops):
        for point in stop:
            temp_df.at[point, 'segment'] = 'stop' + str(i)
    temp_df.to_csv(path)

def eps_tau(ratio, minimum_sampling_interval, taumult):
    return (ratio * (minimum_sampling_interval * taumult))/2, minimum_sampling_interval * taumult

traj_points = read_csv('data/trajectory_points/trajectory_points_57.csv')

minimum_sampling_interval_p57 = 0.071
(eps,tau) = eps_tau(0.8, minimum_sampling_interval_p57, 5)
undefined = 1.2 * eps
min_mov = 0.085

stop_extractor = SOCStopExtractor(traj_points, eps , tau, undefined, min_mov)
stops = stop_extractor.SOC(True, 'soc_data/' + time.strftime("%Y%m%d_%H%M%S"), 'person_57')
write_output('data/trajectory_points_with_stops/trajectory_points_with_stops_57.csv', traj_points, stops)
