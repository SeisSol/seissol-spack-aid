# Copyright 2013-2020 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)


from spack.package import *
import sys
import os
import glob
import shutil 

class SeissolUtils(Package):
    """Seissol - A scientific software for the numerical simulation of seismic wave phenomena 
    and earthquake dynamics. This package provides all necessary apps, libs, scripts 
    as well as simulation cases to work with SeisSol.
    """

    homepage = "http://www.seissol.org"
    version('develop',
            git='https://github.com/SeisSol/SeisSol.git',
            branch='master', submodules=True)

    maintainers = ['ravil-mobile']

    variant('cookbook', 
            default=False, 
            description="fetches SeisSol cookbook i.e., exemplary setups")

    variant('benchmarks', 
            default=False, 
            description="fetches benchmarks. Be sure that you "
                        "have access to the SeisSol LRZ-gitlab repo.")

    variant('gmsh_gui', default=False, description="enables gui support for gmsh")
    variant('paraview', default=False, description="installs Paraview for visualization")
    variant('cross_arch_build', default=False, description="installs via cross architectural build")

    resource(name='examples', 
             git='https://github.com/SeisSol/Examples',
             when='+examples',
             placement='examples')

    resource(name='benchmarks', 
             git='https://gitlab.lrz.de/seissol.org/benchmarks',
             when='+benchmarks', 
             placement='benchmarks')

    depends_on('hdf5@1.10: +shared +threadsafe +mpi')
    depends_on('netcdf-c@4.6.1 +shared +mpi')
    depends_on('pumgen')
    depends_on('glm@0.9.7.1')
    depends_on('proj@4.9.2 +pic')
    depends_on('eigen@3.4.0')

    depends_on("gmsh+hdf5+metis+netgen~med", when='~gmsh_gui')
    depends_on("gmsh+hdf5+metis+fltk+netgen~med", when='+gmsh_gui')

    # openblas cannot detect a correct architecture during a cross-arch build
    # and thus we have to switch to netlib blas
    depends_on("netlib-lapack", when="+cross_arch_build")
    depends_on("openblas@:0.3.12", when="%gcc@:10.1.99 ~cross_arch_build")

    depends_on("netgen+metis")

    depends_on("paraview+hdf5+qt", when="+paraview") 
    depends_on("mesa~llvm", when="+paraview") 

    depends_on('scons@3.0.1:3.1.2', type='build')
    depends_on('cmake', type='build')
    
    scons_utils = {'gmsh2gambit': 'preprocessing/meshing/gmsh2gambit'}

    cmake_utils = {'rconv': 'preprocessing/science/rconv',
                   'cube_c': 'preprocessing/meshing/cube_c'}

    phases = ['build', 'install']

    def build(self, spec, prefix):
        CC = os.getenv('CC')
        CXX = os.getenv('CXX')

        if spec['mpi'].compiler.name == 'intel':
            c_compiler_name = 'mpiicc'
            cxx_compiler_name = 'mpiicpc'
        else:
            c_compiler_name = 'mpicc'
            cxx_compiler_name = 'mpic++'

        os.environ['CC'] = os.path.join(spec['mpi'].prefix.bin, c_compiler_name)
        os.environ['CXX'] = os.path.join(spec['mpi'].prefix.bin, cxx_compiler_name)

        for util in SeissolUtils.scons_utils:
            path = join_path(self.stage.source_path, SeissolUtils.scons_utils[util])
            with working_dir(path, create=False):
                if util == 'rconv':
                    args = []
                    args.append('compiler={}'.format(spec.compiler.name))
                    args.append('netcdfDir={}'.format(spec['netcdf-c'].prefix))
                    args.append('proj4Dir={}'.format(spec['proj'].prefix))
                    scons(*args)
                else:
                    scons()
        
        # restore env. variable to the state how it was before
        os.environ['CC'] = "" if CC == None else CC
        os.environ['CXX'] = "" if CXX == None else CXX


        for util in SeissolUtils.cmake_utils:
            path = join_path(self.stage.source_path, SeissolUtils.cmake_utils[util])
            with working_dir(path, create=False):
                cmake(".")
                make()

    def install(self, spec, prefix):

        if "+examples" in spec:
            install_tree("examples", prefix.examples)

        if "+benchmarks" in spec:
            install_tree("benchmarks", prefix.benchmarks)

        copy_list = {}
        for util in SeissolUtils.scons_utils:
            copy_list[util] = [os.path.join(self.stage.source_path, SeissolUtils.scons_utils[util], "build", "bin"), None]
        
        for util in SeissolUtils.cmake_utils:
            copy_list[util] = [os.path.join(self.stage.source_path, SeissolUtils.cmake_utils[util]), None]

        copy_list['gmsh2gambit'][1] = prefix.gmsh2gambit
        copy_list['cube_c'][1] = prefix.cube_c
        copy_list['rconv'][1] = prefix.rconv

        for key in copy_list:
            install_tree(copy_list[key][0], copy_list[key][1])
            
        # isntall vizualization tools
        install_tree(join_path(self.stage.source_path, 'postprocessing/visualization/receiver'), prefix.viz.receiver)
    
    def setup_run_environment(self, env):
        pumgen = self.spec['pumgen']
        gmsh = self.spec['gmsh']
        bins = [self.prefix.gmsh2gambit,
                self.prefix.cube_c,
                self.prefix.rconv,
                pumgen.prefix.bin,
                gmsh.prefix.bin]

        if "+paraview" in self.spec:
            paraview = self.spec['paraview']
            bins.append(paraview.prefix.bin)

        env.prepend_path('PATH', ":".join(bins))

        if "+examples" in self.spec:
            env.set('SEISSOL_EXAMPLES', self.prefix.examples)


        if "+benchmarks" in self.spec:
            env.set('BENCHMARKS', self.prefix.benchmarks)

        env.prepend_path('PATH', self.prefix.viz.receiver.bin)
        env.prepend_path('PYTNONPATH', self.prefix.viz.receiver.src)

