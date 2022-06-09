from stop_extraction import PMLHStopDetection
from stop_extraction import read_traj_points_csv
from stop_extraction import write_output_csv
from dateutil import parser

def classify_point_trajectories(data_path, to_save_path, roaming_distance_delta , stay_duration_delta):
    (df, traj_points) = read_traj_points_csv(data_path)
    print("Extracting sequences...")
    stays = PMLHStopDetection(traj_points, roaming_distance_delta , stay_duration_delta).extract_stays()
    print(f"Classifying points (stays = {len(stays)}) ...")
    df['segment'] = 'move'
    df['medoid'] = False
    for medoid, timestamp1, timestamp2 in stays:
        print(f"medoid: {medoid}")
        for _, point_index, _, timestamp in traj_points:
            if parser.parse(timestamp) >= parser.parse(timestamp1) and parser.parse(timestamp) <= parser.parse(timestamp2):
                df.at[point_index, 'segment'] = 'stop_with_center_' + str(medoid)
            if point_index == medoid:
                df.at[point_index, 'medoid'] = True
    write_output_csv(df, to_save_path)

roaming_distance_delta = 1
stay_duration_delta = 30
#traj_points = classify_point_trajectories('data/trajectory_points/trajectory_points_57.csv', f'data/trajectory_segments_PMLH/stop_points_p57_PMLH_r{roaming_distance_delta}_s{stay_duration_delta}.csv', roaming_distance_delta, stay_duration_delta)
traj_points = classify_point_trajectories('data/trajectory_points/trajectory_points_67.csv', f'data/trajectory_segments_PMLH/stop_points_p67_PMLH_r{roaming_distance_delta}_s{stay_duration_delta}.csv', roaming_distance_delta, stay_duration_delta)
traj_points = classify_point_trajectories('data/trajectory_points/trajectory_points_68.csv', f'data/trajectory_segments_PMLH/stop_points_p68_PMLH_r{roaming_distance_delta}_s{stay_duration_delta}.csv', roaming_distance_delta, stay_duration_delta)