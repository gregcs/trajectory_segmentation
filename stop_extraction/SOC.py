import itertools
from dateutil import parser
import json
from scipy.spatial import ConvexHull
from scipy.spatial import distance
from shapely.geometry import Polygon, LineString
import os

class SOCStopExtractor:
    
    def __init__(self, traj_points, eps, tau, undefined, minMov, straightness_tsh = None, centered_distance_tsh = None):
        self.traj_points = traj_points
        self.eps = eps
        self.tau = tau
        self.undefined = undefined
        self.reachability_distances = []
        self.minMov = minMov
        self.straightness_tsh = straightness_tsh if straightness_tsh else 0.5
        self.centered_distance_tsh = centered_distance_tsh if centered_distance_tsh else 2 * eps


    def point_timestamp(self, point):
        return point[3]

    def point_coordinates(self, point):
        return point[2]

    def distance_point_coordinates(self, p1_coordinates, p2_coordinates):
        return distance.euclidean(p1_coordinates, p2_coordinates)

    def distance(self, point_index_1, point_index_2):
        return self.distance_point_coordinates(self.point_coordinates(self.traj_points[point_index_1]), self.point_coordinates(self.traj_points[point_index_2]))

    def time_diff_str(self, timestamp_str_1, timestamp_str_2):
        tlast = parser.parse(timestamp_str_2)
        tfirst = parser.parse(timestamp_str_1)
        time_diff = tlast - tfirst
        return time_diff.total_seconds()

    def time_diff(self, point_index_1, point_index_2):
        return self.time_diff_str(self.point_timestamp(self.traj_points[point_index_1]), self.point_timestamp(self.traj_points[point_index_2]))

    def equal_sequences(self, seq1, seq2):
        return seq1 == seq2

    def list_concat(self, seq1, seq2):
        return list(itertools.chain(seq1, seq2))

    #It's the maximum sequence in the trajectory T that contains the point pi indexed by point_index and
    #for each point p in the sequence dist(pi,p) <= eps.
    def eps_sequence(self, point_index, eps = None):
        if not eps:
            eps = self.eps
        eps_sequence_forward = []
        i = point_index + 1
        while(i < len(self.traj_points) and self.distance(i, point_index) <= eps):
            eps_sequence_forward.append(i)
            i+=1
        eps_sequence_backward = []
        i = point_index - 1
        while(i >= 0 and self.distance(i, point_index) <= eps):
            eps_sequence_backward.append(i)
            i-=1
        eps_sequence_backward.reverse()
        eps_sequence_backward.append(point_index)
        return self.list_concat(eps_sequence_backward, eps_sequence_forward)

    def exist_point_with_eps_sequence_equal_to_sequence(self, sequence):
        found = False
        i = 0
        while((not found) and i < len(sequence)):
            found = self.equal_sequences(self.eps_sequence(sequence[i]), sequence)
            i+=1
        return found

    #It's a set of continuous points that stay within a defined circular area for at least a given amount of time tau.
    #S is a core sequence if cointains a point p such that S is an eps_sequence of p and
    #the temporal span of S is not shorten than tau.
    def is_core_sequence(self, sequence, tau=None):
        if not tau:
            tau = self.tau
        return sequence and len(sequence) >= 2 \
            and self.time_diff(sequence[0], sequence[-1]) >= tau \
            and self.exist_point_with_eps_sequence_equal_to_sequence(sequence)

    #A point p is a core point if eps_sequence of p is a core sequence.
    def is_core_point(self, point_index):
        return self.is_core_sequence(self.eps_sequence(point_index))

    #It's defined as min{r | r <= Eps and Seq(p, r) is a core sequence} if Seq(p, Eps) is a core sequence;
    #it is UNDEFINED otherwise.
    def core_distance(self, eps_seq, point_index):
        core_distance = 0
        if len(eps_seq) > 1:
            point_sequence_index = eps_seq.index(point_index)
            dist_right = -1
            i = 1
            while(point_sequence_index + i < len(eps_seq)):
                dist = self.distance(eps_seq[point_sequence_index], eps_seq[point_sequence_index + i])
                if(self.is_core_sequence(self.eps_sequence(point_index, dist))):
                    dist_right = dist
                    break
                i+=1
            dist_left = -1
            i=1
            while(point_sequence_index - i >= 0):
                dist = self.distance(eps_seq[point_sequence_index], eps_seq[point_sequence_index - i])
                if(self.is_core_sequence(self.eps_sequence(point_index, dist))):
                    dist_left = dist
                    break
                i+=1
            if not (dist_left == -1 and dist_right ==-1):
                if(dist_left == -1):
                    core_distance = dist_right
                if(dist_right == -1):
                    core_distance = dist_left
                if(not (dist_left == -1 or dist_right ==-1)):
                    core_distance = min(dist_left, dist_right)
        return core_distance

    def compute_reachability_distances(self):
        for _, point_index, _, _ in self.traj_points:
            eps_seq = self.eps_sequence(point_index)
            if(self.is_core_sequence(eps_seq)):
                r = self.core_distance(eps_seq, point_index)
                next_point_sequence_index = eps_seq.index(point_index)
                while(next_point_sequence_index < len(eps_seq)):
                    self.reachability_distances[eps_seq[next_point_sequence_index]] = \
                        max(r, self.distance(point_index, eps_seq[next_point_sequence_index]))
                    next_point_sequence_index+=1

    def extract_eps_reachability_sequence(self, counter):
        eps_reachability_sequence = []
        while(counter < len(self.traj_points)):
            if self.reachability_distances[counter] <= self.eps:
                eps_reachability_sequence.append(counter)
            else:
                break
            counter+=1
        return (eps_reachability_sequence, counter+1)

    def extract_eps_reachability_sequences(self):
        eps_reachability_sequences = []
        counter = 0
        while(counter < len(self.traj_points)):
            (eps_reachability_sequence, counter) = self.extract_eps_reachability_sequence(counter)
            if eps_reachability_sequence:
                eps_reachability_sequences.append(eps_reachability_sequence)
        return eps_reachability_sequences
    
    def get_next_point_index(self, sequence, sequence_index):
        if sequence_index == len(sequence) - 1:
            if sequence[sequence_index] + 1 >= len(self.traj_points):
                return sequence[sequence_index]
            else:
                return sequence[sequence_index] + 1
        else:
            return sequence[sequence_index + 1]

    def spatio_temporal_center(self, sequence):
        cx_num = 0
        cy_num = 0
        den = 0
        for sequence_index, point_index in enumerate(sequence):
            (x,y) = self.point_coordinates(self.traj_points[point_index])
            time_diff = self.time_diff(point_index,self.get_next_point_index(sequence, sequence_index))
            cx_num += x*time_diff
            cy_num += y*time_diff
            den += time_diff
            return (cx_num/den, cy_num/den)

    def merge_eps_reachability_sequences(self, eps_reachability_sequences):

        def criterion1(seq1, seq2):
            return self.distance_point_coordinates(self.spatio_temporal_center(seq1),self.spatio_temporal_center(seq2)) <= 2 * self.eps and \
                        self.time_diff(seq1[-1], seq2[0]) < self.minMov

        def criterion2(seq1, seq2):
            def get_geom_hull(points_seq):
                hull = [(points_seq[ip1], points_seq[ip2]) for ip1, ip2 in ConvexHull(points_seq).simplices]
                return Polygon([point for side in hull for point in side])
            points_seq1 = [self.traj_points[i][2] for i in seq1]
            points_seq2 = [self.traj_points[i][2] for i in seq2]
            geom1 = get_geom_hull(points_seq1) if len(points_seq1) > 2 else  LineString(points_seq1)
            geom2 = get_geom_hull(points_seq2) if len(points_seq2) > 2 else  LineString(points_seq2)
            return geom1.overlaps(geom2) and self.time_diff(seq2[0], seq1[-1]) < self.minMov

        def is_mergeable(seq1, seq2):
            return criterion1(seq1, seq2) and criterion2(seq1,seq2)

        def merge_to_last_element(list_of_sequences, lst_to_merge):
            list_of_sequences.append(self.list_concat(list_of_sequences.pop(), lst_to_merge))

        merged_eps_reachability_sequences = []
        eps_rs_counter = 0
        merged = False
        while(eps_rs_counter < len(eps_reachability_sequences) - 1):
            if not merged:
                if is_mergeable(eps_reachability_sequences[eps_rs_counter], eps_reachability_sequences[eps_rs_counter+1]):
                    merged_eps_reachability_sequences.append(self.list_concat(eps_reachability_sequences[eps_rs_counter],(eps_reachability_sequences[eps_rs_counter+1])))
                    eps_rs_counter+=2
                    merged = True
                else:
                    merged_eps_reachability_sequences.append(eps_reachability_sequences[eps_rs_counter])
                    eps_rs_counter+=1
                    merged = False
            else:
                if is_mergeable(merged_eps_reachability_sequences[-1], eps_reachability_sequences[eps_rs_counter]):
                    merge_to_last_element(merged_eps_reachability_sequences, eps_reachability_sequences[eps_rs_counter])
                    eps_rs_counter+=1
                    merged = True
                else:
                    merged = False
        return merged_eps_reachability_sequences

    def prune_eps_reachability_sequences(self, eps_reachability_sequences):
        pruned_eps_reachability_sequences = []
        for seq in eps_reachability_sequences:
            pruned_eps_reachability_sequence = []
            i = len(seq) - 1
            while i >= 0 and (not self.is_core_point(seq[i])):
                i-=1
            while i>=0:
                pruned_eps_reachability_sequence.append(seq[i])
                i-=1
            pruned_eps_reachability_sequence.reverse()
            pruned_eps_reachability_sequences.append(pruned_eps_reachability_sequence)
        return pruned_eps_reachability_sequences                

    def straightness(self, sequence):
        den = 0
        for sequence_index, point_index in enumerate(sequence[:-1]):
            den += self.distance(point_index, sequence[sequence_index+1])
        return self.distance(sequence[0], sequence[-1]) / den if den else 0
    
    def centered_distance(self, sequence):
        num = 0
        den = 0
        for sequence_index, point_index in enumerate(sequence):
            time_diff = self.time_diff(point_index, self.get_next_point_index(sequence, sequence_index))
            num += self.distance_point_coordinates(self.point_coordinates(self.traj_points[point_index]), self.spatio_temporal_center(sequence)) * time_diff
            den += time_diff
        return num/den if den else 0

    def filter_false_positive_stop_sequences(self, stop_sequences):
        return [s for s in stop_sequences 
                    if self.straightness(s) <= self.straightness_tsh and 
                         self.centered_distance(s) <= self.centered_distance_tsh]

    def save_intermediate_results(self, save_intermediate_results, folder_name = None, file_name = None, file_variable_name = None, data = None):
        if save_intermediate_results:
            if not os.path.isdir(folder_name):
                os.makedirs(folder_name)
            if not file_variable_name:
                file_variable_name = ''
            with open(folder_name + '/' + file_name + '_' + file_variable_name, 'w') as f:
                f.write(json.dumps(data))

    def SOC(self, save_intermediate_results = False, folder_name = None, file_variable_name = None):
        self.reachability_distances = [self.undefined] * len(self.traj_points) 
        print('Computing reachability distances ...')
        self.compute_reachability_distances()
        self.save_intermediate_results(save_intermediate_results, folder_name, 'reachability_distances', file_variable_name, self.reachability_distances)
        print('Finished to compute reachability distances.')
        print('Extracting eps reachability sequences ...')
        eps_reachability_sequences = self.extract_eps_reachability_sequences()
        self.save_intermediate_results(save_intermediate_results, folder_name, 'eps_reachability_sequences', file_variable_name, eps_reachability_sequences)
        print('Finished to extract eps reachability sequences.')
        print('Merging eps reachability sequences ...')
        merged_eps_reachability_sequences = self.merge_eps_reachability_sequences(eps_reachability_sequences)
        self.save_intermediate_results(save_intermediate_results, folder_name, 'merged_eps_reachability_sequences', file_variable_name, merged_eps_reachability_sequences)
        print('Finished to merge eps reachability sequences (merged %d).' % (len(eps_reachability_sequences) - len(merged_eps_reachability_sequences)))
        print('Pruning merged eps reachability sequences ...')
        pruned_eps_reachability_sequences = self.prune_eps_reachability_sequences(merged_eps_reachability_sequences)
        self.save_intermediate_results(save_intermediate_results, folder_name, 'pruned_eps_reachability_sequences', file_variable_name, pruned_eps_reachability_sequences)
        print('Finished to prune merged eps reachability sequences.')
        filtered_eps_reachability_sequences = self.filter_false_positive_stop_sequences(pruned_eps_reachability_sequences)
        return filtered_eps_reachability_sequences




