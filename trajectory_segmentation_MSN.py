from stop_extraction import MSNTrajcetorySegmentator
import pandas as pd

def segment_trajectories(data_path, to_save_path, ths_dis, ths_dur, ths_speed, min_angle, rho):
   traj_infos = pd.read_csv(data_path)
   segmentator = MSNTrajcetorySegmentator(traj_infos, ths_dis, ths_dur, ths_speed, min_angle, rho)
   (move_indexes, stop_indexes, noise_indexes) = segmentator.move_stop_noise_segmentation()
   traj_infos['segment'] = None
   for i in move_indexes:
      traj_infos.at[i, 'segment'] = 'move'
   for i in stop_indexes:
      traj_infos.at[i, 'segment'] = 'stop'
   for i in noise_indexes:
      traj_infos.at[i, 'segment'] = 'noise'
   traj_infos.to_csv(to_save_path)   


ths_dis_p57 = 1.13 * 3
ths_dur_p57 = 8.55
ths_speed_p57 = 0.73
min_angle_p57 = 45
rho_p57 = 0.0001
segment_trajectories('data/trajectories_info/trajectories_info_57.csv', 
                        'data/trajectory_segments_MSN/trajectory_segments_p57.csv',
                           ths_dis_p57, ths_dur_p57, ths_speed_p57, min_angle_p57, rho_p57)

ths_dis_p67 =  1.1 * 3
ths_dur_p67 = 13.33
ths_speed_p67 = 0.69
min_angle_p67 = 45
rho_p67 = 0.0001
segment_trajectories('data/trajectories_info/trajectories_info_67.csv', 
                        'data/trajectory_segments_MSN/trajectory_segments_p67.csv',
                           ths_dis_p67, ths_dur_p67, ths_speed_p67, min_angle_p67, rho_p67)

ths_dis_p68 =  1.094 * 3
ths_dur_p68 = 31.6
ths_speed_p68 = 0.58
min_angle_p68 = 45
rho_p68 = 0.0001
segment_trajectories('data/trajectories_info/trajectories_info_68.csv', 
                        'data/trajectory_segments_MSN/trajectory_segments_p68.csv',
                           ths_dis_p68, ths_dur_p68, ths_speed_p68, min_angle_p68, rho_p68)
