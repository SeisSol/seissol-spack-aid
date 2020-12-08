spack:
  definitions:
  - compilers: [{{ compiler }}]
  - mpis: [{{ mpi }}]
  - targets: [target={%+ if arch is defined %}{{ arch }}{% else %}{{ arch_family }}{% endif %}]
  - packages: 
      - seissol-env+mpi+asagi~building_tools{%+ if arch_family != 'x86_64' %}~x86{% endif %}
      - seissol-utils
 
  specs:
  - matrix:
    - [\$compilers]
    - [arch={{ arch_family }}]
#    - [+piclibs]
  - matrix:
    - [\$mpis, cmake@3.16.2{%+ if gpu is defined %}{{ ", " }}{{ gpu }}{% endif %}]
    - [\$targets]
    - [\$%compilers]
  - matrix:
    - [\$packages]
    - [\$targets]
    - [\$^mpis]
    - [\$%compilers]
  
  container:
    format: singularity

    images:
      build: {{ builder_image }}
      final: {{ target_image }}

    strip: false

    os_packages:
      command: {{ install_command }}
      final:
      - python3
      - python3-pip
      - pkg-config
      - make
      - git

    extra_instructions:
        final: |
            update-alternatives --install /usr/bin/python python /usr/bin/python3 20 \
            && compiler_path=$(cat /opt/software/compiler_path | tr -d '\n') \
            && update-alternatives --install /usr/bin/gcc gcc $compiler_path/bin/gcc 20 \
            && update-alternatives --install /usr/bin/g++ g++ $compiler_path/bin/g++ 20 \
            && update-alternatives --install /usr/bin/gfortran gfortran $compiler_path/bin/gfortran 20 \
            && $compiler_path/lib/gcc/*/*/libgcc.a \
            && pip3 install scons numpy