## Installing Tensorflow from source (GPU enabled) 

Original instructions can be found [here](http://www.nvidia.com/object/gpu-accelerated-applications-tensorflow-installation.html). 

The instructions at NVIDIA did not work for me, several modifications were made in order for me to install Tensorflow: I removed the hard reset when installing Tensorflow:

```
$ git reset --hard 70de76e
```

And I removed 6.1 compatibility when configuring:
```
Please note that each additional compute capability significantly increases your build time and binary size. 
[Default is: "3.5,5.2"]: 5.2,6.1 [see https://developer.nvidia.com/cuda-gpus] 
```

Step 1. Intall NVIDIA CUDA

Step 2. Install NVIDIA cuDNN

Once cuDNN downloaded, uncompress the files and copy them into the CUDA Toolkit directory (assumed here to be in /usr/local/cuda/): 

```
$ sudo tar -xvf cudnn-7.5-linux-x64-v5.1.tgz -C /usr/local 
```

Step 3. Install and Upgrade PIP (if necessary)

```
$ sudo apt-get install python-pip python-dev
$ pip install --upgrade pip 
```


Step 4. Install Bazel

```
$ sudo apt-get install software-properties-common swig 
$ sudo add-apt-repository ppa:webupd8team/java 
$ sudo apt-get update 
$ sudo apt-get install oracle-java8-installer 
$ echo "deb http://storage.googleapis.com/bazel-apt stable jdk1.8" | sudo tee /etc/apt/sources.list.d/bazel.list 
$ curl https://storage.googleapis.com/bazel-apt/doc/apt-key.pub.gpg | sudo apt-key add - 
$ sudo apt-get update 
$ sudo apt-get install bazel 
```

Step 5. Install Tensorflow

```
$ git clone https://github.com/tensorflow/tensorflow
$ cd tensorflow 
```

Then run the configure script:

```
$ ./configure 
Please specify the location of python. [Default is /usr/bin/python]: [enter]
Do you wish to build TensorFlow with Google Cloud Platform support? [y/N] n 
No Google Cloud Platform support will be enabled for TensorFlow 
Do you wish to build TensorFlow with GPU support? [y/N] y 
GPU support will be enabled for TensorFlow 
Please specify which gcc nvcc should use as the host compiler. [Default is /usr/bin/gcc]: [enter] 
Please specify the Cuda SDK version you want to use, e.g. 7.0. [Leave empty to use system default]: 7.5 
Please specify the location where CUDA 8.0 toolkit is installed. Refer to README.md for more details. [Default is /usr/local/cuda]: [enter] 
Please specify the Cudnn version you want to use. [Leave empty to use system default]: 5 
Please specify the location where cuDNN 5 library is installed. Refer to README.md for more details. [Default is /usr/local/cuda]: [enter] 
Please specify a list of comma-separated Cuda compute capabilities you want to build with. 
You can find the compute capability of your device at: https://developer.nvidia.com/cuda-gpus. 
Please note that each additional compute capability significantly increases your build time and binary size. 
[Default is: "3.5,5.2"]: 5.2 [see https://developer.nvidia.com/cuda-gpus] 
Setting up Cuda include 
Setting up Cuda lib64 
Setting up Cuda bin 
Setting up Cuda nvvm 
Setting up CUPTI include 
Setting up CUPTI lib64 
Configuration finished 
```

Then call bazel to build the TensorFlow pip package: 

```
bazel build -c opt --config=cuda //tensorflow/tools/pip_package:build_pip_package 
bazel-bin/tensorflow/tools/pip_package/build_pip_package /tmp/tensorflow_pkg 
```

And finally install the TensorFlow pip package

Python 2.7:

```
sudo pip install --upgrade /tmp/tensorflow_pkg/tensorflow-0.11.0rc2-cp27-cp27mu-linux_x86_64.whl
```

Step 6. You may have to upgrade your protobuf:

```
sudo pip install --upgrade https://storage.googleapis.com/tensorflow/linux/cpu/protobuf-3.0.0-cp27-none-linux_x86_64.whl
```

Step 7. Test your installation:

```python
$ cd 
$ python 
…
>>> import tensorflow as tf 
I tensorflow/stream_executor/dso_loader.cc:105] successfully opened CUDA library libcublas.so locally 
I tensorflow/stream_executor/dso_loader.cc:105] successfully opened CUDA library libcudnn.so locally 
I tensorflow/stream_executor/dso_loader.cc:105] successfully opened CUDA library libcufft.so locally 
I tensorflow/stream_executor/dso_loader.cc:105] successfully opened CUDA library libcuda.so.1 locally 
I tensorflow/stream_executor/dso_loader.cc:105] successfully opened CUDA library libcurand.so locally 
```

