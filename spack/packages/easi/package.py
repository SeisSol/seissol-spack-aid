# Copyright 2013-2021 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)


import os
import shutil

from spack.package import *


class Easi(CMakePackage):
    """easi is a library for the Easy Initialization of models
    in three (or less or more) dimensional domains.
    """

    homepage = "https://easyinit.readthedocs.io"
    git = "https://github.com/SeisSol/easi.git"

    maintainers = ['ThrudPrimrose', 'ravil-mobile', 'krenzland']

    version('develop', branch='master')
    version('1.2.0', tag='v1.2.0')

    variant('asagi', default=True, description='build with ASAGI support')
    variant('jit', default='impalajit', description='build with JIT support',
            values=('impalajit', 'lua'), multi=True)

    depends_on('asagi +mpi +mpi3', when='+asagi')
    depends_on('yaml-cpp@0.6.2')

    depends_on('impalajit', when='jit=impalajit' or 'jit=impalajit,lua')
    depends_on('lua@5.3.2', when='jit=lua' or 'jit=impalajit,lua')

    conflicts('jit=impalajit', when='target=aarch64:')
    conflicts('jit=impalajit', when='target=ppc64:')
    conflicts('jit=impalajit', when='target=ppc64le:')
    conflicts('jit=impalajit', when='target=riscv64:')

    def cmake_args(self):

        args = []
        args.append(self.define_from_variant('ASAGI', 'asagi'))
        if 'impalajit' in self.spec.variants['jit'].value:
            args.append(self.define('IMPALAJIT', True))
            args.append(self.define('IMPALAJIT_BACKEND', 'original'))
        else:
            args.append(self.define('IMPALAJIT', False))
        
        if 'lua' in self.spec.variants['jit'].value:
            args.append(self.define('LUA', True))

        return args
