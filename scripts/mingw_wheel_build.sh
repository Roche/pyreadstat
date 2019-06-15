#!/usr/bin/env bash

# This script is to be run using mingw and generates python wheels.
# It assumes that there are already existing virtual envs for every python version

# define python command for every version
py37=/c/Users/fajardoo/AppData/Local/conda/conda/envs/py37/python.exe
py36=/c/Users/fajardoo/AppData/Local/conda/conda/envs/py36/python.exe
py35=/c/Users/fajardoo/AppData/Local/conda/conda/envs/py35/python.exe
py27=/c/Users/fajardoo/AppData/Local/conda/conda/envs/py27/python.exe
build="setup.py bdist_wheel"
#####

cd ..

# clean deployment folder
rm dist/*

# build!
echo "Building wheel for python 3.7"
$py37 $build
echo "***************************************"
echo "Building wheel for python 3.6"
$py36 $build
echo "***************************************"
echo "Building wheel for python 3.5"
$py35 $build
echo "***************************************"
echo "Building wheel for python 2.7"
$py27 $build
echo "***************************************"
