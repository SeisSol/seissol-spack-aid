# Build stage with Spack pre-installed and ready to be used
FROM {{ spack_os }}:latest

RUN spack install {{ compiler }} \
    && spack compiler add $(spack location -i {{ compiler }})

RUN mkdir spack_support spack_support/packages
COPY ./repo.yaml spack_support
COPY ./packages ./spack_support/packages
RUN spack repo add spack_support

#NOTE: the current version of spack doesn't allow to install a compiler
# from a speck and immediately use it. Therefore, we create a pre-build
# spack image where we explicitely install and add a compiler first.
# Additionally, we copy and add SeisSol Spack installation scripts
# which we're going to use in the next building step