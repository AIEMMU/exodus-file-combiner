import xarray
import exo_combine
import netCDF4
import glob as glob
import argparse
import os
#remove source file if it exists
try:
    os.remove('source.e')
    print("source file removed")
except:
    print("no file found")
# get argumnets
parser = argparse.ArgumentParser()
parser.add_argument("--path", default="", help ="path to dice_solutions")
parser.add_argument("--dist", type=float, default = 5, help ="The difference between thesitances of points that should be removed between points that should be removed")
parser.add_argument("--overlap", type=float, default = 0.3, help ="The amount of the point cloud you would like to try and align against. It can only be between 0.01 and 1.0")
#parse
flags = parser.parse_args()
if flags.overlap <0.001 or flags.overlap >1:
    print(" please enter a valid value for the overlap value. It can only be between 0.001 and 1.0")
    quit()
files = glob.glob(f'{flags.path}/*.e')

if len(files)==0:
    print("There were no exodus files to combine. Please add the correct directory.")
    quit()

#IO configuration
#create the reference source file

s = xarray.load_dataset(files[0])
s.to_netcdf('source.e', unlimited_dims=s.dims)
s = netCDF4.Dataset('source.e', 'r+')
files.pop(0)
#for the number of exodus files in the folder
for fn in files:
    #create a clone of the target file,
    #load it and combine it with the source file
    t = xarray.load_dataset(fn)
    t.to_netcdf('target.e')
    t  = netCDF4.Dataset('target.e', 'r+')
    s = exo_combine.combine(s,t, diff=flags.dist, overlap = flags.overlap)
    t.close()

#close the source file and remove the target clone
s.close()
os.remove('target.e')
print("The Exodus Combination has completed")


