# Build stage with Spack pre-installed and ready to be used
FROM ravilmobile/spack_custom_builder_arm64:ubuntu-1804_gcc-8.3.0 as builder


# What we want to install and how we want to install it
# is specified in a manifest file (spack.yaml)
RUN mkdir /opt/spack-environment \
&&  (echo "spack:" \
&&   echo "  definitions:" \
&&   echo "  - compilers:" \
&&   echo "    - gcc@8.3.0" \
&&   echo "  - mpis:" \
&&   echo "    - openmpi@3.1.5+cuda" \
&&   echo "  - targets:" \
&&   echo "    - target=aarch64" \
&&   echo "  - packages:" \
&&   echo "    - seissol-env+mpi+asagi~building_tools" \
&&   echo "    - seissol-utils+cross_arch_build" \
&&   echo "  specs:" \
&&   echo "  - matrix:" \
&&   echo "    - - \$compilers" \
&&   echo "    - - arch=aarch64" \
&&   echo "  - matrix:" \
&&   echo "    - - \$mpis" \
&&   echo "      - cmake@3.16.2" \
&&   echo "      - cuda@11.0.2" \
&&   echo "    - - \$targets" \
&&   echo "    - - \$%compilers" \
&&   echo "  - matrix:" \
&&   echo "    - - \$packages" \
&&   echo "    - - \$targets" \
&&   echo "    - - \$^mpis" \
&&   echo "    - - \$%compilers" \
&&   echo "  concretization: together" \
&&   echo "  config:" \
&&   echo "    install_tree: /opt/software" \
&&   echo "  view: /opt/view") > /opt/spack-environment/spack.yaml

# Install the software, remove unnecessary deps
RUN . /opt/spack/share/spack/setup-env.sh \
&& cd /opt/spack-environment \
&& spack env activate . \
&& spack install --fail-fast \
&& spack gc -y

# Modifications to the environment that are necessary to run
RUN cd /opt/spack-environment && \
    . /opt/spack/share/spack/setup-env.sh && \
    spack env activate --sh -d . >> /etc/profile.d/z10_spack_environment.sh

RUN cd /opt/spack-environment && . /opt/spack/share/spack/setup-env.sh \
&& spack env activate --sh -d . >> /opt/spack-environment/seissol_env.sh \
&& spack find -v > /opt/spack-environment/installed_packages.txt
RUN cuda_real_path=$(dirname $(dirname $(readlink /opt/view/bin/nvcc))) \
&& (echo "export CUDA_PATH=${cuda_real_path}" \
&&  echo "export CUDA_HOME=${cuda_real_path}" \
&&  echo "export CMAKE_PREFIX_PATH=\$CMAKE_PREFIX_PATH:${cuda_real_path}" \
&&  echo "export LD_LIBRARY_PATH=\$LD_LIBRARY_PATH:${cuda_real_path}/lib64/stubs" \
&&  echo "export LIBRARY_PATH=\$LIBRARY_PATH:${cuda_real_path}/lib64/stubs") >> /opt/spack-environment/cuda_env.sh


# Bare OS image to run the installed executables
FROM ubuntu:18.04

COPY --from=builder /opt/spack-environment /opt/spack-environment
COPY --from=builder /opt/software /opt/software
COPY --from=builder /opt/view /opt/view
COPY --from=builder /etc/profile.d/z10_spack_environment.sh /etc/profile.d/z10_spack_environment.sh

RUN apt-get -yqq update && apt-get -yqq upgrade \
 && apt-get -yqq install python3 python3-pip pkg-config make git gdb vim \
 && rm -rf /var/lib/apt/lists/*

RUN update-alternatives --install /usr/bin/python python /usr/bin/python3 20 \
&& compiler_path=$(cat /opt/software/compiler_path | tr -d '\n') \
&& update-alternatives --install /usr/bin/gcc gcc $compiler_path/bin/gcc 20 \
&& update-alternatives --install /usr/bin/g++ g++ $compiler_path/bin/g++ 20 \
&& update-alternatives --install /usr/bin/gfortran gfortran $compiler_path/bin/gfortran 20 \
&& ranlib $compiler_path/lib/gcc/*/*/libgcc.a \
&& pip3 install scons numpy \
&& mkdir /workspace


ENTRYPOINT ["/bin/bash", "--rcfile", "/etc/profile", "-l"]
