# Modular python interface for optical detector (e.g., water Cherenkov) data.

## Pre-requisites
It is necessary to have `${WCSIMDIR}` defined and CMake 3.9+ for this interface.
Here are some quick instruction on installing CMake 3.15.3.
```
In the planned directory of installation do

wget https://github.com/Kitware/CMake/releases/download/v3.15.3/cmake-3.15.3.tar.gz
tar xzvf cmake-3.15.3.tar.gz
cd cmake-3.15.3
./bootstrap
make

export PATH="$PWD/bin:$PATH"
```
In the case of multiple CMake definition, try
```
ls -tlr ${cmake_dir}/Modules/CMake.cmake
```
to make sure that the path is correct. Otherwise will have `CMAKE_ROOT not found`.

Before start compiling, go to `./pybind11` to checkout/update the submodule 

```git submodule update --init --recursive```


## To compile on a machine with WCSim installed (e.g. StonyBrook Seawulf)


## To compile on a docker image of WCSim

> Please first refer to https://github.com/WCSim/WCSim#using-wcsim-without-building-using-docker for the instruction of WCSim

On this docker image, `python 2.7` is avaible but the `python-dev`is not installed. Thus there is no required header in `/usr/include/python` for building `pybind11`. One will need to

```
apt-get install python-dev (for Ubuntu)
```
or
```
yum install python-devel (for CentOS)
```

*If running with `python3`, replace `python-dev` with `python3-dev` or `python-devel` with `python3-devel`.*

Then

```
cd ${top_of_pyioopt}
mkdir build
cd build

cmake -DDOWNLOAD_CATCH=1 -DPYBIND11_FINDPYTHON=ON ../

or

cmake -DPYBIND11_FINDPYTHON=OFF -DPYTHON_INCLUDE_DIR=$(python -c "from distutils.sysconfig import get_python_inc; print(get_python_inc())") -DPYTHON_LIBRARY=$(python -c "import distutils.sysconfig as sysconfig; print(sysconfig.get_config_var('LIBDIR'))") ../

make -j${ncores}
make install
```
> The extra condition to CMake helps find the python `include` directory properly. 

Finally add
```
export PYTHONPATH=${pyioopt_dir}/:${PYTHONPATH}
```
to the `env` file.
```