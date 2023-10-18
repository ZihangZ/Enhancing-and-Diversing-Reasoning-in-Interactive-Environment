# Enhancing and Diversing Reasoning in Interactive Environment

The base code and log results for my msc project

## Description

Using LLM to generate reasoning steps based on the current interaction environment's observations and goals to help LLM generate more reasonable actions, and allowing the model to choose multiple different types of thought paths to enhance thought diversity

## Getting Started

### Installation

1. Install [BabyAI-Text](https://github.com/flowersteam/Grounding_LLMs_with_online_RL/tree/main/babyai-text) environment
2. Install [Lamorel](https://github.com/flowersteam/lamorel) 

### How to use

1. Customize the parameters or make a copy of config file (local_gpu_config-Copy5.yaml for default setting)
2. Launch command(s) example:
##### Single machine and single GPU(or no GPU)
- Config: set num_machines to 1 in config file
- Launch command(s):
    - ```shell
      
      python -m lamorel_launcher.launch \
           --config-path /root/autodl-tmp/lamorel/examples/PPO_finetuning/ \
           --config-name local_gpu_config-Copy1.yaml \
           rl_script_args.path=/root/autodl-tmp/lamorel/examples/PPO_finetuning/main-Copy1.py \
           rl_script_args.output_dir=/root/autodl-tmp/outputs \
           lamorel_args.llm_args.model_path=/root/autodl-tmp/flan-t5-large
      ```

##### Single machine and GPU(s)
- Config: set num_machines to number of GPUs in config file
  - Launch command(s):
      - LLM server:
     ```shell
      python -m lamorel_launcher.launch \
           --config-path /root/autodl-tmp/lamorel/examples/PPO_finetuning/ \
           --config-name local_gpu_config-Copy1.yaml \
           rl_script_args.path=/root/autodl-tmp/lamorel/examples/PPO_finetuning/main-Copy1.py \
           rl_script_args.output_dir=/root/autodl-tmp/outputs \
           lamorel_args.accelerate_args.machine_rank=0 \
           lamorel_args.accelerate_args.config_file=/root/autodl-tmp/lamorel/examples/configs/accelerate/default_config-Copy1.yaml \
           lamorel_args.llm_args.model_path=/root/autodl-tmp/flan-t5-large
      ```
      - RL script (change machine_rank to 1):
     ```shell
      python -m lamorel_launcher.launch \
           --config-path /root/autodl-tmp/lamorel/examples/PPO_finetuning/ \
           --config-name local_gpu_config-Copy1.yaml \
           rl_script_args.path=/root/autodl-tmp/lamorel/examples/PPO_finetuning/main-Copy1.py \
           rl_script_args.output_dir=/root/autodl-tmp/outputs \
           lamorel_args.accelerate_args.machine_rank=1 \
           lamorel_args.accelerate_args.config_file=/root/autodl-tmp/lamorel/examples/configs/accelerate/default_config-Copy1.yaml \
           lamorel_args.llm_args.model_path=/root/autodl-tmp/flan-t5-large
      ```
