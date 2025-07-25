##Runnable multiple IB cards
current_hostname=$(hostname)

hosts_file="/hybridgpu/my_hosts"

rank=`awk -v hostname="\$current_hostname" '\$1 == hostname {print NR; exit}' "\$hosts_file"`
rank=$((rank-1))
echo "rank is $rank"

nodes=$(grep -v '^#' "$hosts_file" | grep -v '^\$' | wc -l)
echo "node number is $nodes"

NCCL_SOCKET_IFNAME=bond0 NCCL_IB_DISABLE=0 NCCL_DEBUG=INFO  NCCL_IB_HCA=mlx5_10,mlx5_11,mlx5_12,mlx5_13  torchrun --nproc_per_node 8 --nnodes  $nodes --node_rank=$rank  --master_addr='10.13.10.32' --master_port='10086' /hybridgpu/training/train.py --per_device_eval_batch_size 1 --per_device_train_batch_size 1 --model_max_length 2048 --distributed-backend nccl --learning_rate 0.00001 --training_dir /hybridgpu/training/data/ --test_dir /hybridgpu/training/data/ --output_dir /hybridgpu/training/Output --deepspeed --deepspeed_config /hybridgpu/training/ds_z1_fp16.json --num_train_epochs 4



##Runnable single IB card
#NCCL_IB_DISABLE=0 NCCL_DEBUG=INFO NCCL_IB_HCA=mlx5_5 torchrun --nproc_per_node 8 --nnodes 2 --node_rank=0  --master_addr='10.13.10.35' --master_port='10086' /hybridgpu/training/train.py --per_device_eval_batch_size 1 --per_device_train_batch_size 1 --model_max_length 2048 --distributed-backend nccl --learning_rate 0.00001 --training_dir /hybridgpu/training/data/ --test_dir /hybridgpu/training/data/ --output_dir /hybridgpu/training/output --deepspeed --deepspeed_config /hybridgpu/training/ds_z3_fp16.json --num_train_epochs 1


##Runnable Socket
#NCCL_SOCKET_IFNAME=^lo,docker NCCL_DEBUG=INFO torchrun --nproc_per_node 8 --nnodes 2 --node_rank=0  --master_addr='10.13.10.32' --master_port='10086' /hybridgpu/training/train.py --per_device_eval_batch_size 1 --per_device_train_batch_size 1 --model_max_length 2048 --distributed-backend nccl --learning_rate 0.00001 --training_dir /hybridgpu/training/data/ --test_dir /hybridgpu/training/data/ --output_dir /hybridgpu/training/output --deepspeed --deepspeed_config /hybridgpu/training/ds_z3_fp16.json --num_train_epochs 1
