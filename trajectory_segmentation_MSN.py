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


ths_dis_p57 =  0.04026059529684461/3
ths_dur_p57 = 0.08463043183455436/3
ths_speed_p57 = 0.4851796206384786/3
min_angle_p57 = 45
rho_p57 = 0.0001
segment_trajectories('data/trajectories_info/trajectories_info_57.csv', 
                        'data/trajectory_segments_MSN/trajectory_segments_p57.csv',
                           ths_dis_p57, ths_dur_p57, ths_speed_p57, min_angle_p57, rho_p57)
