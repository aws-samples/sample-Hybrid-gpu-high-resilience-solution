from transformers import AutoModelForCausalLM, Trainer, TrainingArguments, AutoTokenizer
from transformers.models.llama.tokenization_llama import LlamaTokenizer
#from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from datasets import load_from_disk,load_dataset
import random
import logging
import sys
import argparse
import os
import torch
import subprocess
import deepspeed
import torch.distributed as dist
import torch
import subprocess
import deepspeed
import os
import torch.distributed as dist
import argparse
import logging
import sys
if __name__ == "__main__":


    # Environment variables set by torch.distributed.launch
    LOCAL_RANK = int(os.environ['LOCAL_RANK'])
    WORLD_SIZE = int(os.environ['WORLD_SIZE'])
    WORLD_RANK = int(os.environ['RANK'])

    dist.init_process_group(backend='nccl', rank=WORLD_RANK, world_size=WORLD_SIZE)

    parser = argparse.ArgumentParser()

    # hyperparameters sent by the client are passed as command-line arguments to the script.
    parser.add_argument("--num_train_epochs", type=int, default=3)
    parser.add_argument("--per_device_train_batch_size", type=int, default=2)
    parser.add_argument("--per_device_eval_batch_size", type=int, default=4)
    parser.add_argument("--warmup_steps", type=int, default=100)
    #parser.add_argument("--eval_steps",type=int,default=5000)
    parser.add_argument("--learning_rate", type=str, default=2e-5)
    parser.add_argument("--evaluation_strategy",type=str,default="epoch")
    parser.add_argument("--gradient_accumulation_steps",type=int,default=4)
    parser.add_argument("--c",type=bool,default=False)
    #parser.add_argument("--logging_steps",type=int,default=5000)
    parser.add_argument("--save_steps",type=int,default=500)
    parser.add_argument("--save_strategy",type=str,default="steps")
    parser.add_argument("--save_total_limit",type=int,default=4)
    parser.add_argument("--model_max_length",type=int,default=512)
    parser.add_argument("--bf16",type=bool,default=True)
    #parser.add_argument("--deepspeed_config",type=str,default="/data/")
    # Data, model, and output directories
    parser.add_argument("--output_data_dir", type=str, default="/data/llmma/output_data")
    parser.add_argument("--output_dir", type=str, default="/data/data/llama2/output")
    parser.add_argument("--model_dir", type=str, default="/data/llmma/model")
    parser.add_argument("--n_gpus", type=str, default=8)
    parser.add_argument("--training_dir", type=str, default="/data/llmma/training")
    parser.add_argument("--test_dir", type=str, default="/data/llmma/test")

    parser = deepspeed.add_config_arguments(parser)

    args, _ = parser.parse_known_args()

    # Set up logging
    logger = logging.getLogger(__name__)

    logging.basicConfig(
        level=logging.getLevelName("INFO"),
        handlers=[logging.StreamHandler(sys.stdout)],
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    rank = dist.get_rank()

    world_size = dist.get_world_size()
    print(f"Rank: {rank}, World_size:{world_size}")
    # load datasets
    train_dataset = load_from_disk(args.training_dir)
    #test_dataset = load_dataset(args.test_dir)

    logger.info(f" loaded train_dataset length is: {len(train_dataset)}")
    #logger.info(f" loaded test_dataset length is: {len(test_dataset)}")

    #model_name_or_path = "meta-llama/Llama-2-7b-hf"
    fsx_model_path = "/hybridgpu/training/llama2/snapshots/01c7f73d771dfac7d292323805ebc428287df4f9"

    model_name_or_path = "/home/node-user/test-liang/train_llm/llm_model"
    #Download source model from fsx to local disk for local rank 0
    if LOCAL_RANK == 0:
        print("-----------local rank 0 downloading model from fsx ----")
        os.system("cp -r {0} {1}".format(fsx_model_path, model_name_or_path))

    #Note: the barrier is used to ensure just only local rank 0 to download model assets from s3.
    torch.distributed.barrier()

    model_name_or_path = model_name_or_path + '/01c7f73d771dfac7d292323805ebc428287df4f9/'

    model = AutoModelForCausalLM.from_pretrained(model_name_or_path, use_cache=False)

    tokenizer = LlamaTokenizer.from_pretrained(model_name_or_path, model_max_length=args.model_max_length)
    # Print additional special tokens
    print("BOS Token:", tokenizer.bos_token)
    print("EOS Token:", tokenizer.eos_token)
    print("Mask Token:", tokenizer.mask_token)
    print("Pad Token:", tokenizer.pad_token)
    print("Unknown Token:", tokenizer.unk_token)


    # define training args
    training_args = TrainingArguments(
        output_dir = f"{args.output_dir}/checkpoint",
        num_train_epochs=args.num_train_epochs,
        per_device_train_batch_size=args.per_device_train_batch_size,
        per_device_eval_batch_size=args.per_device_eval_batch_size,
        warmup_steps=args.warmup_steps,
        evaluation_strategy="no",         #just for test
        logging_dir=f"{args.output_dir}/logs",
        logging_steps = 10,
        gradient_checkpointing=False,
        learning_rate=float(args.learning_rate),
        deepspeed=args.deepspeed_config,
        #save_steps = args.save_steps,
        save_strategy = "epoch",          #just for test
        #save_strategy = "no",          #just for test
        save_total_limit = args.save_total_limit,
        remove_unused_columns=False,
        save_on_each_node = True,
        gradient_accumulation_steps = args.gradient_accumulation_steps,
        fp16=True,
        bf16=False,  # Use BF16 if available
    )

    # create Trainer instance
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
    #    eval_dataset=test_dataset,
#        tokenizer=tokenizer
    )

    # train model
    trainer.train()


    print("------saving model!-----")
    save_model_dir = f"{args.output_dir}/model"
    tokenizer.save_pretrained(save_model_dir)
    trainer.save_model(save_model_dir)
    print("------model is saved!-----")

