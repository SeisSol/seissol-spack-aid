# Copyright 2013-2024 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)


from spack.package import *


class SeissolEnv(BundlePackage, CudaPackage, ROCmPackage):
    """Seissol - A scientific software for the numerical simulation
    of seismic wave phenomena and earthquake dynamics.
    This package only provides all necessary libs for seissol installation.
    """

    homepage = "http://www.seissol.org"
    git = "https://github.com/SeisSol/SeisSol.git"
    version("master", branch="master", submodules=True)
    maintainers("Thomas-Ulrich", "davschneller", "vikaskurapati")
  
    variant('mpi', default=True, description="installs an MPI implementation")
    variant('asagi', default=True, description="installs asagi for material input")

    variant(
        "gemm_tools_list",
        default="LIBXSMM,PSpaMM",
        description="gemm toolkit(s) for the (CPU) code generator",
        values=("LIBXSMM", "MKL", "OpenBLAS", "BLIS", "PSpaMM", "Eigen", "LIBXSMM_JIT"),
        multi=True,
    )

    variant('memkind', default=True, description="installs memkind")
    variant('python', default=False, description="installs python, pip, numpy and scipy")
    variant('building_tools', default=False, description="installs cmake") 

   # GPU options
    variant("intel_gpu", default=False, description="Compile for Intel GPUs")

    forwarded_variants = ["cuda", "intel_gpu", "rocm"]
    for v in forwarded_variants:
        variant(
            "sycl_backend",
            default="acpp",
            description="SYCL backend to use for DR and point sources",
            values=("acpp", "oneapi"),
            when=f"+{v}",
        )
        variant(
            "sycl_gemm",
            default=False,
            description="Use SYCL also for the wave propagation part (default for Intel GPUs)",
            when=f"+{v}",
        )


    with when("+cuda"):
        for var in ["openmpi", "mpich", "mvapich", "mvapich2", "mvapich2-gdr"]:
            depends_on(f"{var} +cuda", when=f"^[virtuals=mpi] {var}")

    with when("+rocm"):
        for var in ["mpich", "mvapich2-gdr"]:
            depends_on(f"{var} +rocm", when=f"^[virtuals=mpi] {var}")

    # with cuda 12 and llvm 14:15, we have the issue: "error: no template named 'texture"
    # https://github.com/llvm/llvm-project/issues/61340
    conflicts("cuda@12", when="+cuda ^llvm@14:15")
    # this issue is fixed with llvm 16. SeisSol compiles but does not run on heisenbug:
    # [hipSYCL Warning] from (...)/cuda_hardware_manager.cpp:55 @ cuda_hardware_manager():
    # cuda_hardware_manager: Could not obtain number of devices (error code = CUDA:35)
    # [hipSYCL Error] from (...)/cuda_hardware_manager.cpp:74 @ get_device():
    # cuda_hardware_manager: Attempt to access invalid device detected.
    conflicts("cuda@12", when="+cuda cuda_arch=86")
    depends_on("cuda@11:", when="+cuda")
    depends_on("hip", when="+rocm")

    requires("%oneapi", when="sycl_backend=oneapi")

    depends_on("hipsycl@0.9.3: +cuda", when="+cuda sycl_backend=acpp")

    # TODO: this one needs to be +rocm as well--but that's not implemented yet
    depends_on("hipsycl@develop", when="+rocm sycl_backend=acpp")

    # TODO: extend as soon as level zero is available
    depends_on("hipsycl@develop", when="+intel_gpu sycl_backend=acpp")

    # TODO: once adaptivecpp supports NVHPC, forward that (SYCL_USE_NVHPC)

    # GPU architecture requirements
    conflicts(
        "cuda_arch=none",
        when="+cuda",
        msg="A value for cuda_arch must be specified. Add cuda_arch=XX",
    )

    conflicts(
        "amdgpu_target=none",
        when="+rocm",
        msg="A value for amdgpu_arch must be specified. Add amdgpu_arch=XX",
    )


    depends_on('parmetis +int64 +shared', when="+mpi")
    depends_on('metis +int64 +shared', when="+mpi")

    depends_on('hdf5@1.10: +shared +threadsafe ~mpi', when="~mpi")
    depends_on('hdf5@1.10: +shared +threadsafe +mpi', when="+mpi")

    depends_on('netcdf-c@4.6: +shared ~mpi', when="~mpi")
    depends_on('netcdf-c@4.6: +shared +mpi', when="+mpi")

    depends_on('asagi ~mpi ~mpi3 ~fortran', when="+asagi ~mpi")
    depends_on('asagi +mpi +mpi3', when="+asagi +mpi")

    depends_on('easi@1.2: ~asagi jit=impalajit,lua', when="~asagi")
    depends_on('easi@1.2: +asagi jit=impalajit,lua', when="+asagi")

    depends_on("intel-mkl threads=none", when="gemm_tools_list=MKL")
    depends_on("blis threads=none", when="gemm_tools_list=BLIS")
    depends_on("openblas threads=none", when="gemm_tools_list=OpenBLAS")
    depends_on("libxsmm@main", when="gemm_tools_list=LIBXSMM_JIT")

    conflicts("gemm_tools_list=LIBXSMM", when="gemm_tools_list=LIBXSMM_JIT")

    depends_on('memkind', when="+memkind target=x86_64:")

    depends_on("py-pspamm", when="gemm_tools_list=PSpaMM")
    depends_on(
        "libxsmm@1.17 +generator", when="gemm_tools_list=LIBXSMM target=x86_64:")
    )


    depends_on('yaml-cpp@0.6.2')
    depends_on('cxxtest')
    depends_on('eigen@3.4.0')
    
    depends_on('py-numpy', when='+python')
    depends_on('py-scipy', when='+python')
    depends_on('py-matplotlib', when='+python')
    depends_on('py-pip', when='+python')
    depends_on('py-pyopenssl', when='+python')
    depends_on('python@3.6.0:', when='+python')
    
    depends_on('cmake@3.12.0:', when='+building_tools')
