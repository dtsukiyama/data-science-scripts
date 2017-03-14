## Deep Learning Cloud Computing

This is a tutorial on how to install Tensorflow on a GPU enabled EC2 instance AWS (Amazon Web Services). I have approached this from two avenues: first, installing Tensorflow from source; second, installing Anaconda and then creating a conda environment in order to launch Jupyter notebooks from your instance. 

This tutorial assumes you have an Amazon Web Services account and have command line experience. And also a Nvidia Developers Account in order to download cudnn.

## EC2 Instance Creation

1. First launch an instance
2. Select an Ubuntu Server Amazon Machine Image 
3. Select a p2xlarge GPU Instance
4. Leave Configure Instance Details as defaults
5. Under Add Storage, increase Size (GiB) to at least 16
6. Under Add Tags, give any name you wish
7. Under Configure Security Group you have two choices: leave defaults except for source, which should be My IP; or if you wish to be able to launch a Jupyter notebook from your instance you will have to create additional rules. There should be 3 in total:

SSH
HTTPS
Custom TCP Rule

The custom TCP Rule should be set to a port like 8080, which will be familiar to you if you often launch Jupyter notebooks locally. Additionally you need to have the source for all three set to 'Anywhere.'

When you launch your instance you will be asked to a key pair, you may either have one or you may create a new one. Assume we create a new key pair, it will be downloaded. Place in a directory. CD into the directpry and run:

```
chmod 400 /path_to_key/my_key.pem
```

Now you can ssh into your instance:

```
ssh -i /path_to_key/my_key.pem ubuntu@public_dns_name
```

## Install Tensorflow 1.0.1 from Source

Install dependencies:

```
sudo apt-get -y update
sudo apt-get -y upgrade
sudo apt-get -y install git python-pip python-dev
sudo apt-get -y install -y libpng12-dev libfreetype6 python-numpy python-scipy ipython python-matplotlib build-essential cmake pkg-config libtiff4-dev libjpeg-dev libjasper-dev libgtk2.0-dev libavcodec-dev libavformat-dev libswscale-dev libv4l-dev swig zip python-sklearn python-wheel
```

Java:

```
sudo add-apt-repository ppa:webupd8team/java
sudo apt-get update
sudo apt-get install oracle-java8-installer
```

Create a directory to install Bazel and Tensorflow:

```
cd ~
mkdir installation
cd installation
wget https://github.com/bazelbuild/bazel/releases/download/0.4.4/bazel-0.4.4-installer-linux-x86_64.sh 
chmod +x bazel-0.4.4-installer-linux-x86_64.sh
./bazel-0.4.4-installer-linux-x86_64.sh --user
```

After installing Bazel, you should exit your instance then log in again to make sure Bazel has been properly installed

```
bazel version
```

Install CUDA:

```
sudo apt-get install -y linux-image-extra-`uname -r` linux-headers-`uname -r` linux-image-`uname -r`
wget http://developer.download.nvidia.com/compute/cuda/repos/ubuntu1404/x86_64/cuda-repo-ubuntu1404_8.0.44-1_amd64.deb
sudo dpkg -i  cuda-repo-ubuntu1404_8.0.44-1_amd64.deb
sudo apt-get -y update
sudo apt-get -y upgrade
sudo apt-get install -y cuda
sudo sh -c "sudo echo '/usr/local/cuda/lib64' > /etc/ld.so.conf.d/cuda.conf"
sudo ldconfig
```

You can check your CUDA installation:
```
nvidia-smi
```

Install Cudnn:

Download cudnn-8.0-linux-x64-v5.1.tgz from your Nvidia Developer account.

Now upload the tgz to your instance, ubuntu@ec2-xxx-xx-xxxx-xxx.compute-1.amazonaws.com references you instances public DNS; e.g ubuntu@ec2-123-45-678-900.compute-1.amazonaws.com 

```
scp -i /path_to_key/my_key.pem /path_to/cudnn-8.0-linux-x64-v5.1.tgz ubuntu@ec2-xxx-xx-xxxx-xxx.compute-1.amazonaws.com:~/installation/
```

Unpack the tgz:

```
tar -zxf cudnn-8.0-linux-x64-v5.1.tgz
sudo cp -P cuda/lib64/* /usr/local/cuda/lib64/
sudo cp cuda/include/* /usr/local/cuda/include/
```

Install Tensorflow:

```
git clone https://github.com/tensorflow/tensorflow
cd tensorflow
./configure
```

During configuration Tensorflow will ask several questions, for the most part the defaults suffice excpet for when it asks 
"Do you wish to build Tensorflow with CUDA support?" Answer y.

"Please note that each additional compute capability significantly your build time and binary size." Answer 3.7, which is the size of the p2xlarge instance.

Build Tensorflow:

```
bazel build -c opt --config=cuda //tensorflow/tools/pip_package:build_pip_package

bazel-bin/tensorflow/tools/pip_package/build_pip_package /tmp/tensorflow_pkg

sudo pip install /tmp/tensorflow_pkg/tensorflow-1.0.1-cp27-none-linux_x86_64.whl
```

Edit you bashrc (nano ~/.bashrc) file by adding the following two lines:

export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/usr/local/cuda/lib64:/usr/local/cuda/extras/CUPTI/lib64"
export CUDA_HOME=/usr/local/cuda

Test Installation:

```python
import tensorflow as tf
tf.__version__
```

Test GPU settings:

```python
a=tf.Variable(1.0)
b=a+3
with tf.Session() as sess:
    sess.run(tf.global_variables_initializer())
    print(sess.run(b))
```

## Install Jupyer Environment

Go to the Continuum [archive](https://repo.continuum.io/archive/) to select a package for download.

Download package:

```
wget https://repo.continuum.io/archive/Anaconda2-4.3.1-Linux-x86_64.sh
```

Then run:

```
bash Anaconda2-4.3.1-Linux_x86_64.sh
```

Now you can run the following commands to create your password hash:

```python
ipython
from IPython.lib import passwd
passwd()
```

Verfiy and save your password

```python
exit()
```

Now configure Jupyter:

```
jupyter notebook --generate-config 
mkdir certs
cd certs
sudo openssl req -x509 -nodes -days 365 -newkey rsa:1024 -keyout mycert.pem -out mycert.pem
cd ~/.jupyter/
nano jupyter_notebook_config.py
```

In the Jupyer configuration file add:

```
c = get_config()
c.IPKernelApp.pylab = 'inline' 
c.NotebookApp.certfile = u'/home/ubuntu/certs/mycert.pem' 
c.NotebookApp.ip = '*' 
c.NotebookApp.open_browser = False 

#Relace the password with your password 
c.NotebookApp.password = u'sha1:941c93244463:0a28b4a9a472da0dc28e79351660964ab81605ae' 
c.NotebookApp.port = 8080
```

## Create Jupyter Environment

Create a new conda environment and name it:

```
conda create --name NAME python=2
```

Activate the environment:

```
source activate NAME
```

Install packages:

```
conda install -c conda-forge tensorflow=1.0.0
conda install numpy matplotlib pandas jupyter notebook
```

Now you can launch the notebook:

```
jupyter notebook
```

In the browswer set the address:

https://ec2-xx-xxx-xxx-xx.compute-1.amazonaws.com:8080/


