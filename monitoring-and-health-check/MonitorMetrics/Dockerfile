FROM 048912060910.dkr.ecr.cn-northwest-1.amazonaws.com.cn/dockerhub/nvidia/cuda:12.4.0-devel-ubuntu22.04

RUN apt-get update && \
apt-get install -y ca-certificates curl && \
rm -rf /var/lib/apt/lists/*

RUN curl -O https://amazoncloudwatch-agent.s3.amazonaws.com/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb && \
dpkg -i -E amazon-cloudwatch-agent.deb && \
rm -rf /tmp/* && \
rm -rf /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-config-wizard && \
rm -rf /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl && \
rm -rf /opt/aws/amazon-cloudwatch-agent/bin/config-downloader

ENV RUN_IN_CONTAINER="True"
ENTRYPOINT ["/opt/aws/amazon-cloudwatch-agent/bin/start-amazon-cloudwatch-agent"]