# Copyright 2013-2020 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)


from spack.package import *
import os

class SeissolEnv(BundlePackage):
    """Seissol - A scientific software for the numerical simulation of seismic wave phenomena and earthquake dynamics.
    This package only provides all necessary libs for seissol installation.
    """

    homepage = "http://www.seissol.org"
    version('develop',
            git='https://github.com/SeisSol/SeisSol.git',
            branch='master')

    maintainers = ['ravil-mobile']
    
    variant('mpi', default=True, description="installs an MPI implementation")
    variant('asagi', default=True, description="installs asagi for material input")
    variant('libxsmm', default=True, description="installs libxsmm-generator")
    variant('extra_blas', default='none', description='installs an extra blas implementation',
            values=('mkl', 'openblas', 'blis', 'none'), 
            multi=True)
    variant('memkind', default=True, description="installs memkind")
    variant('python', default=False, description="installs python, pip, numpy and scipy")
    variant('building_tools', default=False, description="installs scons and cmake")    
    variant("cuda", default=False, description="install libraries for compiling the GPU version based on cuda and sycl")

    depends_on('mpi', when="+mpi")
    # with cuda 12 and llvm 14:15, we have the issue: "error: no template named 'texture" 
    # https://github.com/llvm/llvm-project/issues/61340
    conflicts("cuda@12", when="+cuda ^llvm@14:15")
    # this issue is fixed with llvm 16. SeisSol compiles but does not run on heisenbug:
    # [hipSYCL Warning] from (...)/cuda_hardware_manager.cpp:55 @ cuda_hardware_manager(): cuda_hardware_manager: Could not obtain number of devices (error code = CUDA:35)
    # [hipSYCL Error] from (...)/cuda_hardware_manager.cpp:74 @ get_device(): cuda_hardware_manager: Attempt to access invalid device detected.
    # Therefore the cuda version is set to 11 now, but this constrain could be released in the future
    depends_on("cuda@11", when="+cuda")
    depends_on("hipsycl@develop +cuda", when="+cuda")

    depends_on('parmetis +int64 +shared', when="+mpi")
    depends_on('metis +int64 +shared', when="+mpi")
    depends_on('libxsmm@1.17 +generator', when="+libxsmm target=x86_64:")

    depends_on('hdf5@1.10:1.12.2 +shared +threadsafe ~mpi', when="~mpi")
    depends_on('hdf5@1.10:1.12.2 +shared +threadsafe +mpi', when="+mpi")

    depends_on('netcdf-c@4.6:4.7.4 +shared ~mpi', when="~mpi")
    depends_on('netcdf-c@4.6:4.7.4 +shared +mpi', when="+mpi")

    depends_on('asagi ~mpi ~mpi3 ~fortran', when="+asagi ~mpi")
    depends_on('asagi +mpi +mpi3', when="+asagi +mpi")

    depends_on('easi@1.2 ~asagi jit=impalajit,lua', when="~asagi")
    depends_on('easi@1.2 +asagi jit=impalajit,lua', when="+asagi")


    depends_on('intel-mkl threads=none', when="extra_blas=mkl")
    depends_on('openblas threads=none', when="extra_blas=openblas")
    depends_on('blis threads=none', when="extra_blas=blis")

    depends_on('memkind', when="+memkind target=x86_64:")
    depends_on('py-pspamm')
    depends_on('yaml-cpp@0.6.2')
    depends_on('cxxtest')
    depends_on('eigen@3.4.0')
    
    depends_on('py-numpy', when='+python')
    depends_on('py-scipy', when='+python')
    depends_on('py-matplotlib', when='+python')
    depends_on('py-pip', when='+python')
    depends_on('py-pyopenssl', when='+python')
    depends_on('python@3.6.0:', when='+python')
    
    depends_on('cmake@3.12.0:3.16.2', when='+building_tools')
    depends_on('scons@3.0.1:3.1.2', when='+building_tools')
