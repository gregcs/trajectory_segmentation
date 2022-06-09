from scipy.spatial import distance
from dateutil import parser
from  itertools import combinations

class PMLHStopDetection:

    def __init__(self, traj_points, roaming_distance_delta, stay_duration_delta):
        self.traj_points = traj_points
        self.roaming_distance_delta = roaming_distance_delta
        self.stay_duration_delta = stay_duration_delta
        self.min_date = min([parser.parse(p[3]) for p in traj_points])

    def point_index(self, point):
        return point[1]

    def point_indexes(self, i, j):
        return [self.point_index(p) for p in self.traj_points[i:j+1]]

    def point_coordinates(self, point):
        return point[2]

    def point_timestamp(self, point):
        return point[3]

    def distance_point_coordinates(self, p1_coordinates, p2_coordinates):
        return distance.euclidean(p1_coordinates, p2_coordinates)

    def distance(self, point_index_1, point_index_2):
        return self.distance_point_coordinates(self.point_coordinates(self.traj_points[point_index_1]), self.point_coordinates(self.traj_points[point_index_2]))
    
    def all_distances(self, i, j):  
        return [self.distance(point_index_1, point_index_2) for point_index_1, point_index_2 
                        in combinations(self.point_indexes(i, j), 2)]

    def distances_from_point(self, point_index, point_indexes_lst):  
        return [self.distance(point_index, point_index_2) for point_index_2 
                        in point_indexes_lst]

    def time_in_sec(self, point_index):
        tlast = parser.parse(self.point_timestamp(self.traj_points[point_index]))
        tfirst = self.min_date
        time_diff = tlast - tfirst
        return time_diff.total_seconds()
    
    def j_star_candidate(self, i):
        j=i+1
        while(j < len(self.traj_points)):
            if self.time_in_sec(j) >= self.time_in_sec(i) + self.stay_duration_delta:
                break
            j+=1
        return j

    def deameter(self, i, j):
        return max(self.all_distances(i, j))
    
    def max_j_deameter(self, i, j_star):
        print(f'max_j_deameter ({i},{j_star})')
        counter = j_star - 1
        while(counter > i):
            if self.deameter(i, counter)  <= self.roaming_distance_delta:
                break
            else:
                counter-=1
        return counter
    
    def medoid(self, i, j):
        print(f'find medoid ({i}, {j})')
        max_distances = [max([self.distances_from_point(point_index,self.point_indexes(i,j))]) for point_index in self.point_indexes(i, j)]
        return i + max_distances.index(min(max_distances)) 

    def extract_stays(self):
        stays = []
        i=0
        while(i< len(self.traj_points)-1):
            print(f"point: {i}")
            j_star = self.j_star_candidate(i)
            if self.deameter(i, j_star) > self.roaming_distance_delta:
                i+=1
            else:
                j_star = self.max_j_deameter(i, j_star)
                stay = (self.medoid(i, j_star), self.point_timestamp(self.traj_points[i]), self.point_timestamp(self.traj_points[j_star]))
                stays.append(stay)
                i = j_star +1
        return stays