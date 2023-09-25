'''
PPO implementation taken from https://github.com/openai/spinningup
'''
import random
import json
import hydra
from utils.ppo_buffer import PPOBuffer
from utils.generate_prompt import generate_prompt, generate_thought_prompt, generate_prompt_memory, generate_thought_prompt_memory, generate_reflect_prompt, generate_prompt_cot
import torch
import numpy as np

from tqdm import tqdm
import time
import pickle
import os

import gym
import babyai_text

from lamorel import Caller, lamorel_init
from lamorel import BaseUpdater, BaseModuleFunction

lamorel_init()

def get_thought_text(thought_output):
    return thought_output[0][0]['text'].replace('\n', ' ').replace('   ', '').replace('next step', 'next action').replace('go_right', 'turn_right').replace('go_left', 'turn_left').replace('.', '')

def get_actions(thought_list,thought_type):
    action_sequences = []
    for thought in thought_list:
        thought = thought.lower()
        if 'next actions are' in thought:
            action_text = thought[thought.index('next actions are') + len('next actions are'):]
        elif 'next action is' in thought:
            action_text = thought[thought.index('next action is') + len('next action is'):]
        else:
            action_text = thought
        if 'thought' in action_text:
            action_text = action_text[:action_text.index('thought')]
        if 'observation' in action_text:
            action_text = action_text[:action_text.index('observation')]
        if 'please' in action_text:
            action_text = action_text[:action_text.index('please')]
        if 'next goal' in action_text:
            action_text = action_text[:action_text.index('next goal')]
        if 'you' in action_text:
            action_text = action_text[:action_text.index('you')]
        if 'expected' in action_text:
            action_text = action_text[:action_text.index('expected')]
        if 'note' in action_text:
            action_text = action_text[:action_text.index('note')]
        if 'explanation' in action_text:
            action_text = action_text[:action_text.index('explanation')]
        action_text = action_text.replace('\n', ' ').replace(',', ' ').replace(':', ' ')
        action_sequence = action_text.split()
        action_sequences.append(action_sequence)
    return action_sequences
            

def rollout_thought(obs,action_list,rollout_num, thought_type, model_type):
    thought_list = []
    thought_prompt = generate_thought_prompt(obs,action_list,thought_type)
    for _ in range(rollout_num):
        if model_type == 'seq2seq':
            generate_answer = lm_server.generate(contexts=[thought_prompt], max_length=256)
        else:
            generate_answer = lm_server.generate(contexts=[thought_prompt], 
                                             max_new_tokens=64, 
                                             do_sample = False,
                                             temperature = 1.,
                                             repetition_penalty=1., 
                                             eos_token_id=2, 
                                             bos_token_id=1, 
                                             pad_token_id=0)
        thought_list.append(thought_i)
    return thought_list

@hydra.main(config_path='config', config_name='config')
def main(config_args):
    
    # Random seed
    seed = 42
    torch.manual_seed(seed)
    np.random.seed(seed)
    os.makedirs(config_args.rl_script_args.output_dir, exist_ok=True)
    
    # Create LLM agent
    lm_server = Caller(config_args.lamorel_args)
    
    # type_list = [('subgoal','BabyAI-GoToLocalS6N2-v0'),('subgoal','BabyAI-GoToLocalS6N6-v0'),('subgoal','BabyAI-GoToLocalS6N8-v0'),('highlevel_subgoal','BabyAI-GoToLocalS6N2-v0'),('highlevel_subgoal','BabyAI-GoToLocalS6N4-v0'),('highlevel_subgoal','BabyAI-GoToLocalS6N6-v0'),('highlevel_subgoal','BabyAI-GoToLocalS6N8-v0')]
        
    # type_list = [('subgoal','BabyAI-GoToLocalS6N4-v0',2),('subgoal','BabyAI-PickupDistDebug-v0',2),('subgoal','BabyAI-GoToLocalS6N4-v0',3),('subgoal','BabyAI-PickupDistDebug-v0',3),('subgoal','BabyAI-GoToLocalS6N4-v0',5),('subgoal','BabyAI-PickupDistDebug-v0',5)]
    
    # type_list = [('highlevel_subgoal','BabyAI-GoToLocalS6N4-v0',0.2),('highlevel_subgoal','BabyAI-GoToLocalS7N4-v0',0.2),('highlevel_subgoal','BabyAI-GoToLocalS8N4-v0',0.2),('highlevel_subgoal','BabyAI-GoToLocalS8N5-v0',0.2),('highlevel_subgoal','BabyAI-GoToLocalS8N6-v0',0.2),('highlevel_subgoal','BabyAI-GoToLocalS8N7-v0',0.2)]
    
    # type_list = [('subgoal','BabyAI-GoToLocalS6N4-v0',0.2),('subgoal','BabyAI-GoToLocalS7N4-v0',0.2),('subgoal','BabyAI-GoToLocalS8N4-v0',0.2),('subgoal','BabyAI-GoToLocalS8N5-v0',0.2),('subgoal','BabyAI-GoToLocalS8N6-v0',0.2),('subgoal','BabyAI-GoToLocalS8N7-v0',0.2)]
    
    # type_list = [('subgoal','BabyAI-GoToLocalS6N4-v0',0.2),('subgoal','BabyAI-GoToLocalS6N4-v0',0.5),('subgoal','BabyAI-GoToLocalS6N4-v0',1.0),('subgoal','BabyAI-PickupDistDebug-v0',0.2),('subgoal','BabyAI-PickupDistDebug-v0',0.5),('subgoal','BabyAI-PickupDistDebug-v0',1.0)]
    
    # type_list = [('highlevel_subgoal','BabyAI-GoToLocalS6N4-v0',0.2),('highlevel_subgoal','BabyAI-GoToLocalS6N4-v0',0.5),('highlevel_subgoal','BabyAI-GoToLocalS6N4-v0',1.0),('highlevel_subgoal','BabyAI-PickupDistDebug-v0',0.2),('highlevel_subgoal','BabyAI-PickupDistDebug-v0',0.5),('highlevel_subgoal','BabyAI-PickupDistDebug-v0',1.0)]
    
    # type_list = [('highlevel_subgoal','BabyAI-GoToLocalS6N4-v0',0.2),('highlevel_subgoal','BabyAI-GoToLocalS7N4-v0',0.2),('highlevel_subgoal','BabyAI-GoToLocalS8N4-v0',0.2),('highlevel_subgoal','BabyAI-GoToLocalS8N5-v0',0.2),('highlevel_subgoal','BabyAI-GoToLocalS8N6-v0',0.2),('highlevel_subgoal','BabyAI-GoToLocalS8N7-v0',0.2),('subgoal','BabyAI-GoToLocalS6N4-v0',0.2),('subgoal','BabyAI-GoToLocalS7N4-v0',0.2),('subgoal','BabyAI-GoToLocalS8N4-v0',0.2),('subgoal','BabyAI-GoToLocalS8N5-v0',0.2),('subgoal','BabyAI-GoToLocalS8N6-v0',0.2),('subgoal','BabyAI-GoToLocalS8N7-v0',0.2)]

    # type_list = [(None,'BabyAI-GoToRedBall-v0'),(None,'BabyAI-PickupDistDebug-v0'),(None,'BabyAI-ActionObjDoor-v0'),(None,'BabyAI-GoToLocalS6N4-v0'),('subgoal','BabyAI-GoToLocalS6N4-v0'),('subgoal','BabyAI-ActionObjDoor-v0'),('high_level','BabyAI-GoToLocalS6N4-v0'),('high_level','BabyAI-PickupDistDebug-v0'),('highlevel_subgoal','BabyAI-GoToLocalS6N4-v0'),('highlevel_subgoal','BabyAI-PickupDistDebug-v0')]
    
    # type_list = [('subgoal','BabyAI-GoToLocalS6N4-v0'),('subgoal','BabyAI-PickupDistDebug-v0'),('highlevel_subgoal','BabyAI-PickupDistDebug-v0'),('highlevel_subgoal','BabyAI-GoToLocalS6N4-v0')]
    # for (thought_type_i, env_type_i, explore_rate) in type_list:
    #     print('model type : ' + config_args.lamorel_args.llm_args.model_type)
    
    thought_type_i = config_args.rl_script_args.thought_type
    env_type_i = config_args.rl_script_args.name_environment
    explore_rate = config_args.rl_script_args.explore_rate

    # Instantiate environment
    name_env = env_type_i
    env = gym.make(name_env)
    # actions = ["turn left", "turn right", "go forward"] #"pick_up", "drop", "toggle"]
    actions = config_args.rl_script_args.action_space
    actions_wo_forward = [i for i in actions if i != 'go_forward'] #config_args.rl_script_args.action_space_wo_forward
    action_wo_pickup = [i for i in actions if i != 'pick_up']
    action_wo_pickup_forward = [i for i in actions if i != 'pick_up' and i != 'go_forward']


    # Set up experience buffer
    # buf = PPOBuffer(config_args.rl_script_args.steps_per_epoch, config_args.rl_script_args.gamma, config_args.rl_script_args.lam)

    # Prepare for interaction with environment
    (_o, _infos), ep_ret, ep_len = env.reset(), 0, 0
    if config_args.rl_script_args.short_term_memory:
        o = {
        "mission": _o["mission"],
        "descriptions": [_infos["descriptions"]]
        }
    else:
        o = {
        "mission": _o["mission"],
        "descriptions": _infos["descriptions"]
        }
    memory = {
    "thought": [],
    "action": []
    }

    # Main loop: collect experience in env and update/log each epoch
    n_episodes = 0
    success_num = 0
    invalid_num = 0
    _time = time.time()
    history = {
        "ep_len": [],
        "ep_ret": [],
        "loss": [],
        "policy_loss": [],
        "value_loss": [],
        "actions": [],
        "prompts": [],
    }

    for epoch in range(config_args.rl_script_args.epochs):
        for t in range(config_args.rl_script_args.steps_per_epoch):
            a_is_avilable = False
            act_text_changed = False
            need_answer = True
            random_number = random.random()
            use_high_level = thought_type_i == 'high_level' or thought_type_i == 'highlevel_subgoal'
            if config_args.rl_script_args.short_term_memory:
                obs_text = ', '.join(o['descriptions'][-1])+','
            else:
                obs_text = ', '.join(o['descriptions'])+','

            if "wall 1 step forward," in obs_text:
                available_act = action_wo_pickup_forward
            elif "box 1 step forward," in obs_text or "ball 1 step forward," in obs_text or "key 1 step forward," in obs_text:
                available_act = actions_wo_forward
            else:
                available_act = action_wo_pickup
            # if "box 1 step forward," in obs_text or "wall 1 step forward," in obs_text or "ball 1 step forward," in obs_text or "key 1 step forward," in obs_text:
            #     available_act = actions_wo_forward
            # else:
            #     if "wall 1 step forward," in obs_text:
            #         available_act = action_wo_pickup_forward
            #     else:
            #         available_act = action_wo_pickup
            if thought_type_i == None:
                prompt = generate_prompt(o,available_act,None)
            else:
                if config_args.rl_script_args.short_term_memory:
                    thought_prompt = generate_thought_prompt_memory(o,available_act,memory,thought_type_i)
                else:
                    thought_prompt = generate_thought_prompt(o,available_act,thought_type_i)
                if config_args.rl_script_args.reflection:
                    thought_list = []
                    for _ in range(config_args.rl_script_args.rollout_num):
                        if config_args.lamorel_args.llm_args.model_type == 'seq2seq':
                            thought_i = lm_server.generate(contexts=[thought_prompt], max_length=256)
                        else:
                            thought_i = lm_server.generate(contexts=[thought_prompt], 
                                                             max_new_tokens=64, 
                                                             do_sample = config_args.rl_script_args.do_sample,
                                                             temperature = config_args.rl_script_args.temperature,
                                                             repetition_penalty=1., 
                                                             eos_token_id=2, 
                                                             bos_token_id=1, 
                                                             pad_token_id=0)
                        thought_list.append(get_thought_text(thought_i))
                    action_sequence_list = get_actions(thought_list,thought_type_i)
                    action_sequence_list = [list(x) for x in set(tuple(x) for x in action_sequence_list)]
                    action_sequence_list = [i for i in action_sequence_list if i != []]
                    # if len(action_sequence_list) < 2 or random_number < explore_rate:
                    if len(action_sequence_list) == 0 or random_number < explore_rate:
                        action_sequence_list.append([random.choice(available_act)])
                elif config_args.lamorel_args.llm_args.model_type == 'seq2seq':
                    generate_thought = lm_server.generate(contexts=[thought_prompt], max_length=256)
                    thought_text = get_thought_text(generate_thought)
                else:
                    generate_thought = lm_server.generate(contexts=[thought_prompt], 
                                                     max_new_tokens=64, 
                                                     do_sample = config_args.rl_script_args.do_sample,
                                                     temperature = config_args.rl_script_args.temperature,
                                                     repetition_penalty=1., 
                                                     eos_token_id=2, 
                                                     bos_token_id=1, 
                                                     pad_token_id=0)
                    thought_text = get_thought_text(generate_thought)
                if config_args.rl_script_args.short_term_memory:
                    prompt = generate_prompt_memory(o,available_act,memory,thought_text)
                elif config_args.rl_script_args.reflection:
                    prompt = generate_reflect_prompt(o,available_act,action_sequence_list)
                else:
                    if config_args.rl_script_args.cot_prompt:
                        prompt = generate_prompt_cot(o,available_act,thought_text)
                    else:
                        prompt = generate_prompt(o,available_act,thought_text)
            print("prompt is : " + str(prompt))

            # generate_answer = lm_server.generate(contexts=[prompt], max_length=25)
            if not config_args.rl_script_args.reflection and use_high_level and config_args.rl_script_args.highlevel_auto_answer:
                act_temp = get_actions([thought_text],thought_type_i)[0]
                if act_temp != []:
                    act_text = act_temp[0]
                else:
                    act_text = ''
                need_answer = False

            if need_answer:
                if config_args.lamorel_args.llm_args.model_type == 'seq2seq':
                    generate_answer = lm_server.generate(contexts=[prompt], max_new_tokens=16)
                else:
                    generate_answer = lm_server.generate(contexts=[prompt], 
                                                         max_new_tokens=16, 
                                                         do_sample = True,
                                                         repetition_penalty=1., 
                                                         eos_token_id=2, 
                                                         bos_token_id=1, 
                                                         pad_token_id=0)
                act_text = str(generate_answer[0][0]['text']).lower()
            print("answer is : " + str(act_text))

            # output = lm_server.custom_module_fns(['score', 'value'],
            #                                      contexts=[prompt],
            #                                      candidates=[available_act],
            #                                      minibatch_size=len(available_act))[0]
            # _scores = torch.reshape(output['score'], (1, len(available_act)))
            # proba_dist = torch.distributions.Categorical(logits=_scores)
            # print("scores are : " + str(_scores))
            # value = output["value"][0]

            for act in available_act:
                if config_args.rl_script_args.reflection and 'action ' + str(len(action_sequence_list)) in act_text:
                    print('answer invalid')
                    break
                if use_high_level and config_args.rl_script_args.reflection:
                    break
                if act in act_text:
                    a = actions.index(act)
                    a_is_avilable = True
                    invalid_num = 0
                    break
            if not a_is_avilable:
                if config_args.rl_script_args.reflection:
                    for i in range(len(action_sequence_list)):
                        if str(i) in act_text:
                        # if 'action ' + str(i) in act_text:
                            act_text = action_sequence_list[i]
                            if use_high_level:
                                act_text = act_text[0]
                            act_text_changed = True
                            break
                    if act_text_changed:
                        for act in available_act:
                            if act in act_text:
                                a = actions.index(act)
                                a_is_avilable = True
                                invalid_num = 0
                                break
            if not a_is_avilable:
                print("action invalid")
                invalid_num += 1
                print('invalid_num : ' + str(invalid_num))
                if invalid_num > config_args.rl_script_args.invalid_num:
                    print('exceed max invalid number, choose random action instead')
                    action = random.choice(available_act)
                    a = actions.index(action)
                    invalid_num = 0
                    a_is_avilable = True
                # action = proba_dist.sample()
                # log_prob = proba_dist.log_prob(action) #torch.index_select(_scores, 1, action) #proba_dist.log_prob(action)
                # a = actions.index(available_act[action.cpu().item()])

            if a_is_avilable:
                print(a)
                _o, r, d, _infos = env.step(a)

                ep_ret += r
                ep_len += 1


                # edited 8/27
                if config_args.rl_script_args.short_term_memory:
                    o["descriptions"].append(_infos["descriptions"])
                    if thought_type_i != None:
                        memory["thought"].append(generate_thought[0][0]['text'])
                    memory["action"].append(actions[a])
                    if len(o["descriptions"]) > config_args.rl_script_args.memory_length:
                        o["descriptions"].remove(o["descriptions"][0])
                        if thought_type_i != None:
                            memory["thought"].remove(memory["thought"][0])
                        memory["action"].remove(memory["action"][0])
                else:
                    o = {
                    "mission": _o["mission"],
                    "descriptions": _infos["descriptions"]
                    }
            else:
                d = 0

            timeout = ep_len == config_args.rl_script_args.max_ep_len
            terminal = d or timeout
            epoch_ended = t == config_args.rl_script_args.steps_per_epoch - 1

            if terminal or epoch_ended:
                if not terminal:
                    print('Warning: trajectory cut off by epoch at %d steps.' % ep_len, flush=True)

                if terminal:
                    n_episodes += 1
                    if ep_ret>0:
                        success_num += 1

                    print(f"Episode {n_episodes}:")
                    print(f"Ret: {ep_ret}")
                    print(f"Len: {ep_len}")
                    history["ep_len"].append(ep_len)
                    history["ep_ret"].append(ep_ret)
                    (_o, _infos), ep_ret, ep_len = env.reset(), 0, 0
                    invalid_num = 0
                    if config_args.rl_script_args.short_term_memory:
                        o = {
                        "mission": _o["mission"],
                        "descriptions": [_infos["descriptions"]]
                        }
                        memory = {
                        "thought": [],
                        "action": []
                        }
                    else:
                        o = {
                        "mission": _o["mission"],
                        "descriptions": _infos["descriptions"]
                        }

        # Perform PPO update!
        print(f"PPO update number {epoch + 1}")
        # save_model = (epoch % config_args.rl_script_args.save_freq == 0 or
        #               epoch == config_args.rl_script_args.epochs - 1) and epoch != 0
        # collected_trajectories = buf.get()
        # update_results = lm_server.update(collected_trajectories['obs'],
        #                                     [actions for _ in range(config_args.rl_script_args.steps_per_epoch)],
        #                                     actions=collected_trajectories['act'],
        #                                     returns=collected_trajectories['ret'],
        #                                     advantages=collected_trajectories['adv'],
        #                                     logprobs=collected_trajectories['logp'],
        #                                     values=collected_trajectories['val'],
        #                                     lr=config_args.rl_script_args.lr,
        #                                     clip_eps=config_args.rl_script_args.clip_eps,
        #                                     entropy_coef=config_args.rl_script_args.entropy_coef,
        #                                     value_loss_coef=config_args.rl_script_args.value_loss_coef,
        #                                     max_grad_norm=config_args.rl_script_args.max_grad_norm,
        #                                     ppo_epochs=config_args.rl_script_args.ppo_epochs,
        #                                     save_after_update=save_model,
        #                                     output_dir=config_args.rl_script_args.output_dir)
        # avg_loss = np.mean([_r['loss'].detach().cpu().item() for _r in update_results])
        # avg_policy_loss = np.mean([_r['policy_loss'].detach().cpu().item() for _r in update_results])
        # avg_value_loss = np.mean([_r['value_loss'].detach().cpu().item() for _r in update_results])
        # history["loss"].append(avg_loss)
        # history["policy_loss"].append(avg_policy_loss)
        # history["value_loss"].append(avg_value_loss)
        # history["actions"].append([actions[int(_a.item())] for _a in collected_trajectories['act']])
        # history["prompts"].append(collected_trajectories['obs'])
        # print(f"Update loss: {avg_loss}")
        # with open(config_args.rl_script_args.output_dir + "/history.pkl", "wb") as file:
        #     pickle.dump(history, file)

    r_list = []
    sucess_list = []
    len_list = []
    for i in range(len(history["ep_ret"])):
        if history["ep_ret"][i]!=0:
            r_list.append(history["ep_ret"][i])
            len_list.append(history["ep_len"][i])
            sucess_list.append(1)
        else:
            sucess_list.append(0)

    success_rate = success_num/n_episodes
    r_mean = np.mean(r_list)
    r_std = np.std(r_list)
    len_mean = np.mean(len_list)
    len_std = np.std(len_list)
    print("success_rate is: {}".format(str(success_rate)))
    print(f"Training took {time.time() - _time} seconds")
    # with open(config_args.rl_script_args.output_dir + "/history.pkl", "wb") as file:
    #     pickle.dump(history, file)

    output_log = {
        "ep_len": history["ep_len"],
        "ep_ret": history["ep_ret"],
        "r_list": r_list,
        "len_list": len_list,
        "sucess_list": sucess_list,
        "r_mean": r_mean,
        "r_std": r_std,
        "len_mean": len_mean,
        "len_std": len_std,
        "success_rate": success_rate
    }
    json_object = json.dumps(output_log, indent=5)
    if thought_type_i == None:
        name_thought = 'wo_thought'
    else:
        name_thought = thought_type_i
    if config_args.rl_script_args.reflection:
        name_reflect = 'with_reflect'
    else:
        name_reflect = 'wo_reflect'
    if config_args.rl_script_args.short_term_memory:
        name_memory = 'with_memory'
    else:
        name_memory = 'wo_memory'
    file_name = f"/{thought_type_i}_{name_reflect}_{explore_rate}_{name_memory}_{config_args.rl_script_args.memory_length}_{env_type_i}.json"
    with open(config_args.rl_script_args.log_dir + file_name, "w") as outfile:
        outfile.write(json_object)

    lm_server.close()

if __name__ == '__main__':
    main()