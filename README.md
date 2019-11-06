# Combine steropaired camera files from the DIC engine

## 1. Introduction

This is a python implementation that combines ExodusII files that are out put from the DIC engine(https://github.com/dicengine/dice). It contains a full pipline for aligning the point clouds, and removing overlapping points. 

## 2. Requirements

Python version: 3

Packages:

- Numpy 
- Scipy
- Sklearn
- xarray
- netCDF4

These can be installed using the following command  `pip install -r requirements.txt`

## 3. Run the demo
There are some demo files provided in the data/ folder. a Demo can be run using the following code:

```shell
python main.py --path data/ --dist 1
```
This will open the exodus files in the data folder and create a new file that combines the two exodus files in the folder. This file can be viewed in Paraview(https://www.paraview.org/).

## 4. Code usage

```shell
$ python main.py --path --overlap --dist
```
The path is argument is a path to the exodus files and where they are located. --Overlap is a percentage amount of the meshes you wish to compare to find the best alignment for the mesh. --dist is the argument to check for distance between points that you wish to fuse together. 

## Tips and tricks
(1) Play with the overlap amount. The default amount will not guarentee the best fit. 
(2) Experiment with the distance argument, as too large an amount may remove all the points from the target file, though a small amount may not remove them at all. 
