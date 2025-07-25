import os
from typing import Dict, Any

class Config:
    """
    Centralized configuration for the ECS GPU Recovery CDK Stack.
    Configuration can be overridden using environment variables.
    """

    # DynamoDB Tables
    TASK_TABLE_NAME = "nwcd-l4-v1-tasks-2"
    JOB_TABLE_NAME = "nwcd-l4-v1-jobs-2"
    NODE_TABLE_NAME = "nwcd-l4-v1-nodes-2"

    # ECS Configuration
    ECS_CLUSTER_NAME = "nwcd-l4-v1"
    DCGM_HEALTH_CHECK_TASK = "arn:aws:ecs:us-east-1:633205212955:task-definition/hybridGpu-GPU-DGGM-check:3"

    # SNS Configuration
    SNS_TOPIC_NAME = "gpu-training-notifications"
    SNS_TOPIC_DISPLAY_NAME = "GPU Training Job Notifications"

    # Lambda Configuration
    LAMBDA_TIMEOUT_SECONDS = 300
    LAMBDA_MEMORY_SIZE = 256

    # EC2 Configuration
    CREATE_EC2_INSTANCE = False
    EC2_VPC_ID = "vpc-080281cabd959304f"
    EC2_SUBNET_ID = "subnet-004a411c7043b829a"
    EC2_SSH_KEY_NAME = ""
    EC2_INSTANCE_TYPE = ""
    EC2_AMI_ID = ""  # If empty, will use latest Amazon Linux 2 AMI

    # FSx Lustre Configuration
    CREATE_FSX_LUSTRE = False
    FSX_VPC_ID = ""  # If empty, will use EC2_VPC_ID
    FSX_SUBNET_ID = ""  # If empty, will use EC2_SUBNET_ID
    FSX_STORAGE_CAPACITY_GB = 1200
    FSX_DEPLOYMENT_TYPE = "SCRATCH_2"
    FSX_PER_UNIT_STORAGE_THROUGHPUT = 125

    @classmethod
    def get_config(cls) -> Dict[str, Any]:
        """
        Returns the configuration with environment variable overrides.

        Environment variables take precedence over default values.
        """
        config = {}

        # Get all class variables (excluding methods and private variables)
        for key in dir(cls):
            if not key.startswith('_') and not callable(getattr(cls, key)):
                # Check if environment variable override exists
                env_value = os.environ.get(key)
                if env_value is not None:
                    config[key] = env_value
                else:
                    config[key] = getattr(cls, key)

        return config
