String adjustToRegex(String str) {
    return str.replaceAll("/","\\\\/");
}


String compose(String str1, String str2) {
    return str1 + '_' + str2
}


String removeVersionAndConstrains(String spec) {
    def components = spec.replace('@', '-').split('[\\^\\+]')
    return components[0]
}


String generateBuilderTag(String os, String compiler, String arch = "") {
    suffix = ""
    if (arch.isAllWhitespace()) {
        suffix = removeVersionAndConstrains(compiler)
    }
    else {
        suffix = compose(arch, removeVersionAndConstrains(compiler))
    }
    return compose(os.replaceAll("[:/]", '-'), suffix)
}


String adjustMPI(String spec) {
    gpuExpr = /(cuda)(@(\d+.\d+.\d+))?/
    def matcher = (spec =~ gpuExpr)

    String gpuSpec = ""
    // check whether there cuda has been specified
    if (matcher.count) {
        gpuSpec = "_cuda"
        // try to find cuda version
        cudaVersionExpr = /\d+.\d+.\d+/
        for (int i = 0; i < matcher.count; ++i) {
            for (int j = 0; j < matcher[i].size(); ++j) {
                if (matcher[i][j] ==~ cudaVersionExpr) {
                    gpuSpec += "-" + matcher[i][j]
                    break;
                }
            }
        }
    }

    // Find MPI impl. and its version
    def components = spec.replace('@', '-').split('[\\^\\+]')
    String mpiSpec = components[0]
    return mpiSpec + gpuSpec
}


void generateImageTag(String os, String compiler, String arch, String mpi) {
    return compose(generateBuilderTag(os, compiler, arch), adjustMPI(mpi))
}


def getNameAndVersionFromSpackSpec(String spec) {
    def nameAndVersion = spec.split("\\+")[0]
    return nameAndVersion.replace('@', '-')
}


def generateImageFileTag(String os, String compiler, String mpi, String gpu, String archFamilty, String arch) {
    String imageTag = compose(os, getNameAndVersionFromSpackSpec(compiler))
    imageTag = compose(imageTag, getNameAndVersionFromSpackSpec(mpi))
    if (!gpu.isAllWhitespace()) {
        imageTag = compose(imageTag, getNameAndVersionFromSpackSpec(gpu))
    }
    if (!arch.isAllWhitespace()) {
        imageTag = compose(imageTag, arch)
    }
    return imageTag
}

return this