# Overall brief
The monitor metrics script deployes an DAMON cloudwatch agent container to host node that push metrics to Cloudwatch. 
The metrics includes two part.
One part is generally metrics such as CPU, MEM,Disk, Network and so on .
The other part is NVIDIA CUDA metrics which be supported by Cloudwatch agent native.
All metrics will defined in SSM parameter store

The ECS instance monitor metrics collector setting environment is be ECS optimized Amazon Linux 2023 AMI. AMI-ID:ami-01a935dc864a9b004.
The ECS Anywhere general use Ubuntu 2204 custom OS environment and should be registered to ECS anywhere as extenal instances.

# Preparation
ECS monitor container image build By dockerfile

```
FROM nvidia/cuda:12.6.3-base-ubuntu22.04

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
ENV NVIDIA_VISIBLE_DEVICES="all"
ENTRYPOINT ["/opt/aws/amazon-cloudwatch-agent/bin/start-amazon-cloudwatch-agent"]
```

Define monitor metircs configure in SSM parameter store. Reference URL: [Cloudwatch metrics](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/metrics-collected-by-CloudWatch-agent.html#linux-metrics-enabled-by-CloudWatch-agent)

Refer: ECS-MonitorMetrics-SSM-Parameter-store.json
```
{
    "agent": {
        "region": "cn-northwest-1",
        "omit_hostname": false
    },
    "metrics": {
        "namespace": "NWCD-ECS-Cluster-Monitor",
        "metrics_collected": {
            "nvidia_gpu": {
                "measurement": [
                    "utilization_gpu",
                    "memory_used"
                ],
                "metrics_collection_interval": 60,
                "resources": [
                    "*"
                ]
            },
            "cpu": {
                "measurement": [
                    "cpu_usage_idle",
                    "cpu_usage_active",
                    "cpu_usage_iowait",
                    "cpu_usage_user",
                    "cpu_usage_system"
                ],
                "metrics_collection_interval": 60,
                "totalcpu": true
            },
            "disk": {
                "measurement": [
                    "disk_total",
                    "disk_used_percent"
                ],
                "metrics_collection_interval": 60,
                "ignore_file_system_types": [
                    "sysfs",
                    "devtmpfs",
                    "tmpfs",
                    "proc",
                    "overlay",
                    "autofs",
                    "nfs",
                    "squashfs"
                ],
                "drop_device": true
            },
            "diskio": {
                "measurement": [
                    "diskio_reads",
                    "diskio_writes"
                ],
                "metrics_collection_interval": 60
            },
            "mem": {
                "measurement": [
                    "mem_used_percent",
                    "mem_free"
                ],
                "metrics_collection_interval": 60
            }
        }
    }
}
```

# One. Create role
Create role and trust relationships
CWAgentECSTaskRole

```
aws iam create-role —role-name CWAgentECSTaskRole \
    —assume-role-policy-document "{\"Version\": \"2012-10-17\",\"Statement\": [{\"Sid\": \"\",\"Effect\": \"Allow\",\"Principal\": {\"Service\": \"ecs-tasks.amazonaws.com\"},\"Action\": \"sts:AssumeRole\"}]}"
```

attach policy
```
aws iam attach-role-policy —policy-arn arn:aws-cn:iam::aws:policy/CloudWatchAgentServerPolicy \
    —role-name CWAgentECSTaskRole
```

Create role and trust relationships
CWAgentECSExecutionRole

```
aws iam create-role —role-name CWAgentECSExecutionRole \
    —assume-role-policy-document "{\"Version\": \"2012-10-17\",\"Statement\": [{\"Sid\": \"\",\"Effect\": \"Allow\",\"Principal\": {\"Service\": \"ecs-tasks.amazonaws.com\"},\"Action\": \"sts:AssumeRole\"}]}"

aws iam attach-role-policy —policy-arn arn:aws-cn:iam::aws:policy/CloudWatchAgentServerPolicy \
    —role-name CWAgentECSExecutionRole

aws iam attach-role-policy —policy-arn arn:aws-cn:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy \
    —role-name CWAgentECSExecutionRole

aws iam attach-role-policy —policy-arn arn:aws-cn:iam::aws:policy/AmazonSSMReadOnlyAccess \
        —role-name CWAgentECSExecutionRole

```

# TWO.Create ECS Cluster
Console Create ECS Cluster by ECS Console

Cluster："<YOUR CLUSTER NAME>"
region："<YOUR region>"
launch an instance in Cluster ASG

# Three.Create the task definition 
Download the task definition templates

```
TaskRoleArn=CWAgentECSTaskRole
ExecutionRoleArn=CWAgentECSExecutionRole
AWSLogsRegion="<YOUR Region>"
Region="<YOUR Region>"

curl -O https://raw.githubusercontent.com/aws-samples/amazon-cloudwatch-container-insights/latest/ecs-task-definition-templates/deployment-mode/daemon-service/cwagent-ecs-instance-metric/cwagent-ecs-instance-metric.json
sed -i "s|task-role-arn|${TaskRoleArn}|;s|execution-role-arn|${ExecutionRoleArn}|;s|awslogs-region|${AWSLogsRegion}|" ./cwagent-ecs-instance-metric.json
```

Update ECS task definition that add below parameters by editor tools.

```
# Image
# Full content file refer ./cwagent-ecs-instance-metric.json
"image": "<your custom image>",

# Enable gpu access
            "environment": [
                {
                    "name": "NVIDIA_VISIBLE_DEVICES",
                    "value": "all"
                }
            ],
            
# External config
            "secrets": [
                {
                    "name": "CW_CONFIG_CONTENT",
                    "valueFrom": "ecs-cwagent-daemon-service"
                }
            ],
# definition container networkMode 
             "networkMode": "host"
```

Register task definition 

```
aws ecs register-task-definition --cli-input-json file://cwagent-ecs-instance-metric.json
```

# FOUR. Launch the daemon service

```
ClusterName="<your Cluster Name>"
Region="<YOUR Region>"

aws ecs create-service \
    —cluster ${ClusterName} \
    —service-name cwagent-daemon-service \
    —task-definition ecs-cwagent-daemon-service \
    —scheduling-strategy DAEMON \
    —region ${Region} \
    —launch-type EC2
```

# FIVE.Check the results
In Amazon ECS service. the "cwagent-daemon-service" service will launch a task in every nodes and the status is "running".
In Cloudwatch console. can push custom metircs and namespace in "All metrics"
