spack:
  definitions:
  - compilers: [{{ compiler }}]
  - mpis: [{{ mpi }}]
  - targets: [target={{ arch }}]
  - packages: [seissol-env+mpi+asagi~building_tools, seissol-utils{{ extra }}]

  specs:
  - matrix:
    - [\$compilers]
    - [\$targets]
    - [+piclibs]
  - matrix:
    - [\$mpis, cmake@3.16.2]
    - [\$targets]
    - [\$%compilers]
  - matrix:
    - [\$packages]
    - [\$targets]
    - [\$^mpis]
    - [\$%compilers]
  
  container:
    format: singularity

    base:
      image: {{ os }}
      spack: develop

    strip: false

    os_packages:
      - python3
      - python3-pip
      - pkg-config
      - make
      - git

    extra_instructions:
        final: |
            update-alternatives --install /usr/bin/python python /usr/bin/python3 20 \
            && update-alternatives --install /usr/bin/gcc python /opt/view/bin/gcc 20 \
            && update-alternatives --install /usr/bin/g++ python /opt/view/bin/g++ 20 \
            && ranlib /opt/view/lib/gcc/*/*/libgcc.a \
            && pip3 install scons numpy \
            && mkdir workspace