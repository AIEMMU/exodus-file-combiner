import numpy as np
import icp
import dist
import netCDF4

#get the x,y,z coordinates for the point cloud
#and return these
def get_pointcloud(file):
    X = file['coordx']
    Y = file['coordy']
    Z = file['coordz']
    xyz= np.array([X[:], Y[:], Z[:]]).T
    return xyz

def combine_variables(s, t, idxs,avg_source_idxs, avg_target_idxs):
    #get the num of elements, and num of idxs
    num_elems = len(s['coordx'])
    num_idx = len(idxs)
    #create a variable to store the properties of each variable
    variables = []

    for v in s.variables.values():
        #if the shape of the variable is 1
        #its either the elem_num map or node_num_map
        #or the x,y,z coordinates of the model
        #so the new variables is the length of the  length of the source file and number of
        #indexes
        if len(v.shape) == 1:
            if v.name == 'elem_num_map':
                variables.append((v.name, np.ma.arange(1, num_elems +num_idx + 1)))
            elif v.name == 'node_num_map':
                variables.append((v.name, np.ma.arange(num_elems + num_idx)))
            elif v.shape[0] == num_elems:
                a = s[v.name][:]
                b = t[v.name][:]
                #this line can be un commneted if the user wishes to average
                # the coordinate points between the source and target file
                #a[avg_source_idxs] = (a[avg_source_idxs] + b[avg_target_idxs]) / 2
                variables.append((v.name, np.ma.array(np.ma.concatenate([a, b[idxs]]))))
        else:
            if v.name == 'connect1':

                b = np.vstack(np.arange(1, num_elems + num_idx + 1))
                variables.append((v.name, np.ma.array(b)))
            elif v.shape[1] == num_elems:
                #this is the same as above,
                #but for each array within the variable
                c = np.zeros((s[v.name].shape[0], s[v.name].shape[1] + num_idx))
                for i in range(len(c)):
                    a = s[v.name][i][:]
                    b = t[v.name][i][:]
                    #a[avg_source_idxs] = (a[avg_source_idxs] +b[avg_target_idxs]) //2
                    c[i] = np.concatenate([a, b[idxs]])
                variables.append((v.name, np.ma.array(c)))
    #the variables are stored within the variables array
    for v in variables:
        s[v[0]][:] = v[1]

    return s
def change_variables(t, rot, trans):
    #get the xyz coordinates
    X = t['vals_nod_var1'][:]
    Y = t['vals_nod_var2'][:]
    Z = t['vals_nod_var3'][:]
    #create variables that that are the shape
    # of the target files variables

    var1 = np.zeros(t['vals_nod_var1'].shape)
    var2 = np.zeros(t['vals_nod_var2'].shape)
    var3 = np.zeros(t['vals_nod_var3'].shape)
    i = 0
    for x, y, z in zip(X, Y, Z):
        #rotate  and translate the array and
        # then add it back to the target file
        rm = np.array([x, y, z]).T
        rm = np.matmul(rm, rot.T)
        rm += trans
        var1[i] = rm[:, 0]
        var2[i] = rm[:, 1]
        var3[i] = rm[:, 2]
        i += 1
    t['vals_nod_var1'][:] = var1
    t['vals_nod_var2'][:] = var2
    t['vals_nod_var3'][:] = var3
    return t

def combine(ref, t, diff, overlap, orient):

    #get file cloud points
    s_coords = get_pointcloud(ref)
    t_coords = get_pointcloud(t)

    #set number of points to be compared in ICP
    num_points = len(s_coords) if len(s_coords) < len(t_coords) else len(t_coords)
    num_points = int(num_points * overlap)
    #get the right most points of the source file, and left most points of the target file
    #so they can be compared for the best fit.
    if orient =='hor':
        left = np.argpartition(s_coords[:, 0], num_points)[-num_points:]
        right = np.argpartition(t_coords[:, 0], num_points - 1)[:num_points]
    else:
        left = np.argpartition(s_coords[:, 1], num_points)[-num_points:]
        right = np.argpartition(t_coords[:, 1], num_points - 1)[:num_points]
    #calcuate iteratable Closest point (ICP) with the coordinates
    #to get a translation and rotation matrix for the target points
    T, R1, t1 = icp.icp(t_coords[:num_points], s_coords[-num_points:], max_iterations=1000, tolerance=0.001)

    #rotation and translation matrix
    rot = T[:3, :3]
    trans =T[:3, -1]

    #rotate the points and add them to the target points
    rotated_points = t_coords
    rotated_points = np.matmul(rotated_points, rot.T)
    rotated_points += trans
    #set the points
    t['coordx'][:] = rotated_points[:, 0]
    t['coordy'][:] = rotated_points[:, 1]
    t['coordz'][:] = rotated_points[:, 2]

    #change other variables that are effected by the rotation and translation matrix
    t = change_variables(t, rot, trans)
    #get indices for points that can be added to the source file
    #as well as indicees to average the data between two points
    idxs, avg_source_idxs, avg_target_idxs = dist.get_dist_indices(rotated_points, s_coords, diff)
    #combine the variables to create one file
    ref = combine_variables(ref, t, idxs, avg_source_idxs, avg_target_idxs)
    return ref