FROM 048912060910.dkr.ecr.cn-northwest-1.amazonaws.com.cn/dockerhub/nvidia/cuda:12.4.0-devel-ubuntu22.04

RUN apt-get update -y

RUN apt install -y --allow-change-held-packages  tcptraceroute \
    wget iputils-ping openmpi-bin openmpi-common libopenmpi-dev libgtk2.0-dev bc net-tools


RUN wget  http://www.vdberg.org/~richard/tcpping -O /usr/bin/tcpping
RUN chmod +x /usr/bin/tcpping
RUN apt-get install -y datacenter-gpu-manager

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
RUN sed -i 's/[ #]\(.*StrictHostKeyChecking \).*/ \1no/g' /etc/ssh/ssh_config && \
    echo "    UserKnownHostsFile /dev/null" >> /etc/ssh/ssh_config && \
    sed -i 's/#\(StrictModes \).*/\1no/g' /etc/ssh/sshd_config


RUN mkdir -p /root/.ssh/ \
 && ssh-keygen -q -t rsa -N '' -f /root/.ssh/id_rsa \
 && cp /root/.ssh/id_rsa.pub /root/.ssh/authorized_keys
RUN sed -i 's/#Port 22/Port 2022/' /etc/ssh/sshd_config
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin without-password/' /etc/ssh/sshd_config
RUN sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
EXPOSE 2022

ENV LD_LIBRARY_PATH /usr/local/cuda/extras/CUPTI/lib64:/opt/amazon/openmpi/lib:/opt/nccl/build/lib:/usr/local/lib:$LD_LIBRARY_PATH
ENV PATH /opt/amazon/openmpi/bin/:/usr/bin:/usr/local/bin:$PATH

RUN curl https://bootstrap.pypa.io/get-pip.py -o /tmp/get-pip.py \
    && python3 /tmp/get-pip.py \
    && pip3 install awscli

RUN mkdir -p /workspace/
WORKDIR /workspace
RUN git clone https://github.com/NVIDIA/nccl-tests.git \
    && cd nccl-tests \
    && make -j $(nproc) MPI=1 MPI_HOME=/usr/lib/x86_64-linux-gnu/openmpi CUDA_HOME=/usr/local/cuda/
CMD ["/usr/sbin/sshd", "-D"]