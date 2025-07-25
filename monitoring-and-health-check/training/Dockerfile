FROM nvidia/cuda:11.8.0-devel-ubuntu22.04

RUN apt-get update -y
RUN apt install -y --allow-change-held-packages  tcptraceroute \
    wget iputils-ping openmpi-bin openmpi-common libopenmpi-dev libgtk2.0-dev

RUN DEBIAN_FRONTEND=noninteractive apt-get install -y --allow-unauthenticated \
    git \
    gcc \
    kmod \
    openssh-client \
    openssh-server \
    build-essential \
    curl \
    autoconf \
    libtool \
    automake \
    python3-distutils \
    cmake \
    apt-utils \
    devscripts \
    debhelper \
    libsubunit-dev \
    check \
    pkg-config

RUN mkdir -p /var/run/sshd

ENV LD_LIBRARY_PATH /usr/local/cuda/extras/CUPTI/lib64:/opt/amazon/openmpi/lib:/opt/nccl/build/lib:/opt/amazon/efa/lib:/opt/aws-ofi-nccl/install/lib:/usr/local/lib:$LD_LIBRARY_PATH
ENV PATH /opt/amazon/openmpi/bin/:/opt/amazon/efa/bin:/usr/bin:/usr/local/bin:$PATH

RUN curl https://bootstrap.pypa.io/get-pip.py -o /tmp/get-pip.py \
    && python3 /tmp/get-pip.py \
    && pip3 install awscli


EXPOSE 10086
RUN apt-get install python3-dev -y

RUN mkdir -p /workspace/

WORKDIR /workspace


RUN pip3 install -U pip setuptools
RUN pip3 install fsspec==2023.1.0
RUN pip3 install huggingface_hub==0.17.0
RUN pip3 install huggingface
RUN pip3 install torch==1.13.0
RUN DS_BUILD_UTILS=1 DS_BUILD_FUSED_ADAM=1 pip3 install deepspeed==0.12.0
RUN pip3 install transformers==4.33.0
RUN pip3 install tqdm==4.66.1
RUN pip3 install peft==0.5.0
RUN pip install sentencepiece==0.1.99
RUN pip3 install tabulate
RUN pip3 install protobuf
RUN pip3 install python-etcd
RUN pip3 install datasets==3.0.1
RUN pip3 install numpy==1.26.4
RUN pip3 install accelerate==0.28.0