# General Info
This guide provides information how to configure a new jenkins-slave on lrz-cloud

# Let's get started

## Create a new instance on LRZ cloud
Follow the [offical LRZ tutorial](https://doku.lrz.de/display/PUBLIC/Create+a+VM) about how to create and configure an instance. Pick up `Ubuntu-18.04-LTS-bionic` image and make sure your instance has at least 80GB attached. Please, don't forget to `Associate Floating IP` once your instance has been instantiated.


## Create and configure a new user for Jenkins server
Login to a remote node on LRZ cloud that you've just created using `ssh` and add a new user which jenkins master is going to communicated. Let's configure it
```
sudo adduser jenkins-slave
sudo mkdir -p /home/jenkins-slave/.ssh
sudo cp ~/.ssh/authorized_keys /home/jenkins-slave/.ssh
sudo chown jenkins-slave:jenkins-slave /home/jenkins-slave/.ssh/authorized_keys
sudo usermod -aG sudo jenkins-slave
```
Log out and login as `jenkins-slave` to continue.

Install Java 11
```
sudo apt-get update
sudo apt-get install openjdk-11-jdk
```

and create a temporary directory for jenkins
```
mkdir -p /home/jenkins-slave/jenkins
```

edit `/etc/ssh/sshd_config` file
```
PasswordAuthentication yes
```
and reload ssh deamon
```
sudo systemctl restart ssh
```

## Create and connect to a remote node from Jenkins
Open `Manage Credentials` and create a new credentials by clicking on `Add Credentials`. Select `Username with password`. 
- **Username** - `jenkins-slave`
- **Password** - the one that you specified while creating `jenkins-slave` user
- **UD** - `lrz_runner_id`

and click on `Save`.

At the next step, go to `Manage Jenkins` and and click on `Manage Nodes and Cloud`. After that, click on `New Node`. Specify `lrz_runner` as a name, select `Permanent Agent` and press `Ok`. Fill in the following fields:

- **Remote root directory** - `/home/jenkins-slave/jenkins`
- **Labels** - `runner`
- **Usage** - `Only build jobs label expressions matching this node`
- **Launch Method** - `Launch agents via SSH`
- **Host** - Floating IP address provided by LRZ cloud (openstack)
- **Credentials** - pick up the one starting as `jenkins-slave/***`
- **Hoset Key Verification Strategy** - `Known hosts file Verification Strategy`
- **Availiability** - `Keep this agent online as much as possible`

Click on `save` button and proceed to the next field. You will see a list of nodes configured on your Jenkins server. Find `lrz_runner` and click on it.
If there is no error message then you configure a node correctly.

## Install Docker
Follow the official [installation  documentation](https://docs.docker.com/engine/install/ubuntu/) and install Docker engine

#### Enable Experimental Features of Docker
Edit a global config file i.e., `/etc/docker/daemon.json`:
```
{
  "experimental": true
}
```
and a local one i.e., `~/.docker/config.json`
```
{
  "experimental": "enabled"
}
```
#### Restart docker deamon
```
sudo systemctl start docker
```

#### Enable Docker without sudo
```
sudo groupadd docker
sudo usermod -aG docker $USER
```
Log out and log back in so that your group membership is re-evaluated 
or execute the following:
```
newgrp docker
```

## Enable Docker Buildx (qemu-v5.0.1)
```
sudo apt-get install qemu binfmt-support qemu-user-static
docker run --rm --privileged multiarch/qemu-user-static --reset -p yes 
docker run --privileged --rm tonistiigi/binfmt --install all
```
##### Create your own custom builder
```
docker buildx create --name custom_builder --platform linux/arm64/v8,linux/ppc64le,linux/amd64

docker buildx use custom_builder
docker buildx inspect --bootstrap
```


## Install Singularity
Install GNU Compiler Collection
```
sudo apt-get install gcc g++ make
```
Follow the official [installation guide](https://sylabs.io/guides/3.7/user-guide/quick_start.html) to install Singularity 3.7

#### Configure Singulairty Public key for signing images and access token
```
singularity key newpair
singularity remote login
```

## Final steps
You will probably need to disconnect and connect to `lrz_runner` from your Jenkins server to enforce all made chages to be is re-evaluated. It can be done from `Manage Nodex and Clouds`.

#### Install python environment
```
sudo apt-get install python3 python3-dev python3-pip
sudo pip3 install Jinja2
```

#### Required Credentials
Please, make sure that the following credentials are set up in your Jenkins server
- singularity-user
- docker-hub
- github-repo

Because of singularity, one needs to set up credentials of a privilege user for each agent/node/slave according to the following convention: `<agent_name>_id`
