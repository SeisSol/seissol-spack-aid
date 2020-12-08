## Docker Setup For Cross-Building
- linux kernel >= 4.8
- binfmt-support >= 2.1.7
- docker version >= 19.03
- with **buildx** feature. You will need to set `experimental` flag in the following files: 
   - `/etc/docker/daemon.json`
```
{
   ...
  "experimental": true
  ...
}
```
   - `~/.docker/config.json`

```
{
   ...
  "experimental": "enabled"
  ...
}
```
- QEMU emulator
```
# taken from: www.stereolabs.com/docs/docker/...

# Install the qemu packages
$ sudo apt-get install qemu binfmt-support qemu-user-static

# This step will execute the registering scripts
$ docker run --rm --privileged multiarch/qemu-user-static --reset -p yes 
```

- Additional steps
```
$ docker run --privileged --rm tonistiigi/binfmt --install all
```

## Setup Docker Builders
Create your own custom builder
```
$ docker buildx create --name custom_builder [--driver docker] --platform linux/arm64/v8,linux/ppc64le,linux/amd64
```
Set it as a current builder
```
$ docker buildx use custom_builder
```

If it you haven't use this builder before i.e., it is freshly created one, then make it active:
```
$ docker buildx inspect --bootstrap
[+] Building 5.0s (1/1) FINISHED                                                                                                                                             
 => [internal] booting buildkit                                                                                                                                         5.0s
 => => pulling image moby/buildkit:buildx-stable-1                                                                                                                      4.3s
 => => creating container buildx_buildkit_custom_builder0                                                                                                               0.7s
Name:   custom_builder
Driver: docker-container

Nodes:
Name:      custom_builder0
Endpoint:  unix:///var/run/docker.sock
Status:    running
Platforms: linux/arm64/v7, linux/arm64, linux/ppc64le, linux/amd64, linux/riscv64, linux/386
```

### Example
You may need to reboot your PC to enable all changes
```
docker buildx build -o type=docker --platform linux/arm -t <image>:<tag> .
```

```
docker buildx build -t spack:amd64 --platform linux/amd64 -o type=docker -f ./share/spack/docker/ubuntu-1804.dockerfile .
```