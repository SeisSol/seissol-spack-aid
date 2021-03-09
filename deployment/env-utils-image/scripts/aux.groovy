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