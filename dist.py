import numpy as np
from scipy.spatial.distance import cdist
from scipy.spatial import cKDTree

def get_dist_indices(rm, s_coords, diff):

    '''
    We add the coordinates together and discover
    which indices lie within a certain distance of each other
    we return the indices of the target exodus file to add to the source file
    we return the indices of the points on both files, so that other variables may be averaged for the source file
    points.
    We ret
    :param rm:
    :param s_coords:
    :param diff:
    :return:
    '''
    xyz2 = np.concatenate([s_coords, rm])
    tree2 = cKDTree(xyz2)
    rows_to_fuse = tree2.query_pairs(r=diff)
    avg_target_idxs = [x-len(s_coords) for i, x in rows_to_fuse if x > len(s_coords)-1]
    idxs3 = np.arange(len(rm))
    idxs =np.delete(idxs3, np.unique(avg_target_idxs), axis=0)
    avg_source_idxs = [i for i, x in rows_to_fuse if x > len(s_coords) - 1]

    return idxs, avg_source_idxs, avg_target_idxs