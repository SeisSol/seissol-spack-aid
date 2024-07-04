# Copyright 2013-2024 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)


from spack.package import *


class PyGemmforge(PythonPackage):
    """GPU-GEMM generator for the Discontinuous Galerkin method"""

    homepage = "https://github.com/SeisSol/gemmforge/blob/master/README.md"
    git = "https://github.com/SeisSol/gemmforge.git"

    maintainers("davschneller", "Thomas-Ulrich")
    license("BSD-3-Clause")

    version("master", branch="master")
    depends_on("py-numpy")

    def install(self, spec, prefix):
        install_tree(".", prefix)

    def setup_run_environment(self, env):
        env.prepend_path("PATH", self.spec.prefix)
        env.prepend_path("PYTHONPATH", self.spec.prefix)
