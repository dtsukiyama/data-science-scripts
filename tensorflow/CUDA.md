## Install CUDA via the NVIDIA package:

To use CUDA on your system, you will need the following installed:
* CUDA-capable GPU
* A supported version of Linux with a gcc compiler and toolchain
* NVIDIA CUDA Toolkit (available at http://developer.nvidia.com/cuda-downloads)

Verify that your GPU is CUDA-capable:

```
$ lspci | grep -i nvidia
```

Verify you have a supported version of Linux:

```
$ uname -m && cat /etc/*release
```

Veridy the system has gcc installed:

```
$ gcc --version
```

Download the NVIDIA CUDA Toolkit, which is available at http://developer.nvidia.com/cuda-downloads.

The installer type for this example was deb(network).

Install CUDA:

```
sudo dpkg -i cuda-repo-ubuntu1504_7.5-18_amd64.deb
sudo apt-get update
sudo apt-get install cuda
```

Post-installation requirements:

There are some differing approaches to this. Nvidia's documentation [here](http://docs.nvidia.com/cuda/cuda-installation-guide-linux/index.html#post-installation-actions) or another approach by modifying the .bashrc file in your home directory. 

```
nano ~/.bashrc
```

Add the following lines:

````
export CUDA_HOME=/usr/local/cuda-7.5 
export LD_LIBRARY_PATH=${CUDA_HOME}/lib64 
 
PATH=${CUDA_HOME}/bin:${PATH} 
export PATH
```

We test CUDA installation success by compiling CUDA samples, install in a directory:

```
cuda-install-samples-7.5.sh /home/david/nvidia_cuda_samples
cd nvidia_cuda_samples
cd NVIDIA_CUDA-7.5_Samples
make
cd bin/x86_64/linux/release
./deviceQuery
./bandwidthTest
```

