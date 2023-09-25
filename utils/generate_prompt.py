import random

# type 1
# def generate_prompt(obs,action_list,thought = None):
#     action_options = ', '.join(action_list)
#     prompt = "Based on the goal, observation and thought from agent, choose an availabel action from following: {}\n".format(action_options)
#     prompt += "Goal of the agent: {}\n".format(obs["mission"])
#     prompt += "Observation: {}\n".format(', '.join(obs['descriptions']))
#     if thought != None:
#         prompt += "Thought: {}\n".format(thought)
#     prompt += "Action: "
#     return prompt

# type 2
def generate_prompt(obs,action_list,thought = None):
    action_options = ', '.join(action_list)
    prompt = "Goal of the agent: {}\n".format(obs["mission"])
    prompt += "Observation: {}\n".format(', '.join(obs['descriptions']))
    if thought != None:
        prompt += "Thought: {}\n".format(thought)
    prompt += "Based on the goal, observation and thought from agent, choose an availabel action from following: {}\n".format(action_options)
    prompt += "Action: "
    return prompt

def generate_prompt_cot(obs,action_list,thought = None):
    action_options = ', '.join(action_list)
    prompt = "Based on the goal, observation and thought from agent, choose an availabel action from following: {}\n ".format(action_options)
    random.shuffle(prompt_action_single)
    prompt += ''.join(prompt_action_single[:2]) # random.choice(prompt_hard_evn_subgoal) 
    prompt += " \n Next Goal of the agent: {}\n".format(obs["mission"])
    prompt += "Next Observation: {}\n ".format(', '.join(obs['descriptions']))
    if thought != None:
        prompt += "Next Thought: {}\n ".format(thought)
    # prompt += "Based on the goal, observation and thought from agent, choose an availabel action from following: {}\n ".format(action_options)
    prompt += "Next Action: "
    return prompt

def generate_prompt_memory(obs,action_list,memory_list,thought = None):
    prompt = "Goal of the agent: {}\n".format(obs["mission"])
    action_memory_list = memory_list["action"] + ['']
    thought_memory_list = memory_list["thought"] + ['']
    if len(obs['descriptions']) == 1:
        prompt += "Observation {}: {}\n".format(0, ', '.join(obs['descriptions'][0]))
    else:
        for i in range(len(obs['descriptions'])-1):
            prompt += "Observation {}: {}\n".format(i, ', '.join(obs['descriptions'][i]))
            prompt += "Thought {}: {}\n".format(i, thought_memory_list[i])
            prompt += "Action {}: {}\n".format(i, action_memory_list[i])
        prompt += "Observation {}: {}\n".format(i + 1, ', '.join(obs['descriptions'][-1]))
        if thought != None:
            prompt += "Thought {}: {}\n".format(i + 1, thought)
    action_options = ', '.join(action_list)
    prompt += "Based on the goal, observation and thought from agent, choose an availabel action from following: {}\n".format(action_options)
    prompt += "Next Action : "
    return prompt

def generate_thought_prompt(obs,action_list,thought_type = None):
    prompt = "You are an agent in a Minigrid environment."
    action_options = ', '.join(action_list)
    prompt += "The availabel actions may includes: {}\n".format(action_options)
    # thought_prompt_temp = "Give me a thought about the next step or a sequence of steps. Format answer as following:"
    if thought_type == "subgoal":
        thought_prompt_temp = "Give me a thought about the next step. Format answer as following:"
        if 'go' in obs["mission"]:
            examples = subgoal_goto
        elif 'put' in obs["mission"]:
            examples = subgoal_put
        elif 'open' in obs["mission"]:
            examples = subgoal_open
        elif 'pick' in obs["mission"]:
            examples = subgoal_pick
        else:
            examples = prompt_subgoal
        prompt += thought_prompt_temp
        random.shuffle(examples)
        prompt += ''.join(examples) # random.choice(prompt_hard_evn_subgoal) 
    elif thought_type == "high_level":
        thought_prompt_temp = "Give me a thought about the next step or a sequence of steps. Format answer as following:"
        if 'go' in obs["mission"]:
            examples = highlevel_goto
        elif 'put' in obs["mission"]:
            examples = highlevel_put
        elif 'open' in obs["mission"]:
            examples = highlevel_open
        elif 'pick' in obs["mission"]:
            examples = highlevel_pick
        prompt += thought_prompt_temp
        random.shuffle(examples)
        prompt += ''.join(examples) # random.choice(prompt_hard_evn_subgoal) 
    elif thought_type == "highlevel_subgoal":
        thought_prompt_temp = "Give me a thought about the next step or a sequence of steps. Format answer as following:"
        if 'go' in obs["mission"]:
            examples = highlevel_subgoal_goto
        elif 'put' in obs["mission"]:
            examples = highlevel_subgoal_put
        elif 'open' in obs["mission"]:
            examples = highlevel_subgoal_open
        elif 'pick' in obs["mission"]:
            examples = highlevel_subgoal_pick
        prompt += thought_prompt_temp
        random.shuffle(examples)
        prompt += ''.join(examples) # random.choice(prompt_hard_evn_subgoal) 
    prompt += "\n Next Goal of the agent: {}\n ".format(obs["mission"])
    prompt += "Next Observation: {}\n ".format(', '.join(obs['descriptions']))
    prompt += "Next Thought: "
    return prompt

def generate_thought_prompt_memory(obs,action_list,memory_list, thought_type = None):
    if thought_type == 'reflection':
        print('reflection cannot be used with short term memory')
        raise NotImplmentedError
    prompt = "You are an agent in a Minigrid environment."
    action_options = ', '.join(action_list)
    prompt += "The availabel actions may includes: {}\n".format(action_options)
    thought_prompt_temp = "Give me a thought about the next step. Format answer as following:"
    obs_list = obs['descriptions']
    thought_list = memory_list["thought"] + [""]
    if thought_type == "subgoal":
        prompt += thought_prompt_temp
        if len(action_list) <= 3:
            random.shuffle(prompt_subgoal_memory)
            prompt += ''.join(prompt_subgoal_memory) # random.choice(prompt_subgoal_memory)
        else:
            random.shuffle(prompt_hard_evn_subgoal_memory)
            prompt += ''.join(prompt_hard_evn_subgoal_memory) # random.choice(prompt_hard_evn_subgoal_memory)
    prompt += "\n Goal of the agent: {}\n".format(obs["mission"])
    for i in range(len(obs['descriptions'])):
        prompt += "Observation {}: {}\n".format(i, ', '.join(obs['descriptions'][i]))
        prompt += "Thought {}: {}\n".format(i, thought_list[i])
    return prompt

def generate_reflect_prompt(obs,action_list,action_sequence_list):
    prompt = "You are an agent in a Minigrid environment.\n"
    action_options = ', '.join(action_list)
    prompt += "The availabel actions may includes: {}\n".format(action_options)
    prompt += "Goal of the agent: {}\n".format(obs["mission"])
    prompt += "Observation: {}\n".format(', '.join(obs['descriptions']))
    # prompt += "The availabel actions may includes: {}\n".format(action_options)
    prompt += 'Based on the goal and observation above, which of the following action is best: \n'
    for i, action_sequence in enumerate(action_sequence_list):
        prompt += 'Action {}:'.format(i)
        prompt += ', '.join(action_sequence)
        prompt += ' \n'
    prompt += 'Answer:'
    return prompt

prompt_action_single = [' \n Goal of the agent: put the grey key next to the blue ball \n Observation: You see a wall 3 steps right, You see a blue ball 1 step left and 1 step forward, You see a grey key 1 step right and 1 step forward \n Thought: The mission is put the grey key next to the blue ball, since agent is not carrying grey key so the next subgoal is pick up grey key, since observed grey key 1 step right and 1 step forward, so next step is go_forward \n Action: go_forward',
                        '\n Goal of the agent: open the green door \n Observation: You see a wall 2 steps right, You see a green key 1 step forward, You see a closed grey door 1 step right and 2 steps forward \n Thought: The mission is open the green door, since agent is not carrying green key so the next subgoal is pick up the green key, since observed green key 1 steps forward, so next step is pick_up \n Action: pick_up',
                        '\n Goal of the agent: pick up the red ball \n Observation: You carry a purple box, You see a wall 1 step forward, You see a wall 2 steps right, You see a red ball 1 step left \n Thought: The mission is pick up the red ball, since agent is carrying purple box which is wrong, so next step is drop \n Action: drop',
                        '\n Goal of the agent: open the red door \n Observation: You carry a red key, You see a wall 1 step left, You see a closed grey door 1 step left and 1 step forward, You see a yellow ball 1 step forward, You see a closed red door 2 steps right \n Thought: The mission is open the red door, since agent is carrying red key so the next subgoal is go to the red door, since observed red door 2 steps right, so next step is turn_right \n Action: turn_right'
                       ]

prompt_subgoal = [' \n Goal of the agent: go to the green ball \n Observation: You see a wall 2 step left, You see a purple key 1 step left and 2 steps forward, You see a yellow key 1 step left and 1 step forward, You see a green ball 3 steps forward, You see a grey ball 1 step right and 5 steps forward, You see a green key 1 step right and 2 steps forward, You see a grey ball 1 step right and 1 step forward, You see a green key 2 steps right and 4 steps forward, You see a red box 2 steps right and 2 steps forward, \n Thought: In order to go to the green ball, need to get close to it, since observed a green ball 3 steps forward, so the next step is go_forward',
                  ' \n Goal of the agent: open the purple door \n Observation: You see a wall 3 steps forward, You see a wall 3 steps left, You see a yellow key 1 step right and 1 step forward, You see a locked purple door 2 steps right and 3 steps forward, You see a purple ball 3 steps right and 1 step forward, You see a green box 3 steps right, You see a purple key 2 steps left \n Thought: In order to open the purple door, need to find the purple key firstly and then unlock the purple door, since observed a purple key 2 steps left, so the next step is turn_left',
                  ' \n Goal of the agent: pick up green box \n Observation: You see a wall 2 steps forward, You see a wall 2 steps left, You see a yellow ball 1 step left and 1 step forward, You see a green box 2 steps right \n Thought: In order to pick up green box, need to find the green box first and then go to it, since observed a green box 2 steps right, so the next step is turn_right']

prompt_subgoal_memory = [' \n Goal of the agent: go to the green ball \n Observation 0: A wall 2 step left, A purple key 1 step left and 2 steps forward, A yellow key 1 step left and 1 step forward, A green ball 3 steps forward, A grey ball 1 step right and 5 steps forward, A green key 1 step right and 2 steps forward, A grey ball 1 step right and 1 step forward, A green key 2 steps right and 4 steps forward, A red box 2 steps right and 2 steps forward, \n Thought 0: In order to go to the green ball, need to get close to it, since observed a green ball 3 steps forward, so the next step is go_forward \n Observation 1: A purple key 1 step left and 1 step forward, A yellow key 1 step left, A green ball 2 steps forward, A grey ball 1 step right and 4 steps forward, A green key 1 step right and 1 step forward, A grey ball 1 step right, A green key 2 steps right and 3 steps forward, A red box 2 steps right and 1 step forward, \n Thought 1: In order to go to the green ball, need to get close to it, since observed a green ball 2 steps forward, so the next step is go_forward',
                        ' \n Goal of the agent: open the purple door \n Observation 0: You see a wall 3 steps forward, You see a wall 3 steps left, You see a yellow key 1 step right and 1 step forward, You see a locked purple door 2 steps right and 3 steps forward, You see a purple ball 3 steps right and 1 step forward, You see a green box 3 steps right, You see a purple key 2 steps left \n Thought 0: In order to open the purple door, need to pick up purple key first and then toggle purple door, since agent is not carrying purple key and observed purple key 2 steps left, so the next step is turn_left \n Observation 1: You see a wall 3 steps forward, You see a wall 3 steps right, You see a purple key 2 steps forward \n Thought 1: In order to open the purple door, need to pick up purple key first and then toggle purple door, since agent is not carrying purple key and observed purple key 2 steps forward, so the next step is go_forward \n Observation 2: You see a wall 2 steps forward, You see a wall 3 steps right, You see a purple key 1 step forward \n Thought 2: In order to open the purple door, need to pick up purple key first and then toggle purple door, since agent is not carrying purple key and observed purple key 1 steps forward, so the next step is pick_up']

prompt_hard_evn_subgoal_memory = [' \n Goal of the agent: go to the green ball \n Observation 0: A wall 2 step left, A purple key 1 step left and 2 steps forward, A yellow key 1 step left and 1 step forward, A green ball 3 steps forward, A grey ball 1 step right and 5 steps forward, A green key 1 step right and 2 steps forward, A grey ball 1 step right and 1 step forward, A green key 2 steps right and 4 steps forward, A red box 2 steps right and 2 steps forward, \n Thought 0: In order to go to the green ball, need to get close to it, since observed a green ball 3 steps forward, so the next step is go_forward \n Observation 1: A purple key 1 step left and 1 step forward, A yellow key 1 step left, A green ball 2 steps forward, A grey ball 1 step right and 4 steps forward, A green key 1 step right and 1 step forward, A grey ball 1 step right, A green key 2 steps right and 3 steps forward, A red box 2 steps right and 1 step forward, \n Thought 1: In order to go to the green ball, need to get close to it, since observed a green ball 2 steps forward, so the next step is go_forward',
                 ' \n Goal of the agent: open the purple door \n Observation 0: You see a wall 3 steps forward, You see a wall 3 steps left, You see a yellow key 1 step right and 1 step forward, You see a locked purple door 2 steps right and 3 steps forward, You see a purple ball 3 steps right and 1 step forward, You see a green box 3 steps right, You see a purple key 2 steps left \n Thought 0: In order to open the purple door, need to pick up purple key first and then toggle purple door, since agent is not carrying purple key and observed purple key 2 steps left, so the next step is turn_left \n Observation 1: You see a wall 3 steps forward, You see a wall 3 steps right, You see a purple key 2 steps forward \n Thought 1: In order to open the purple door, need to pick up purple key first and then toggle purple door, since agent is not carrying purple key and observed purple key 2 steps forward, so the next step is go_forward \n Observation 2: You see a wall 2 steps forward, You see a wall 3 steps right, You see a purple key 1 step forward \n Thought 2: In order to open the purple door, need to pick up purple key first and then toggle purple door, since agent is not carrying purple key and observed purple key 1 steps forward, so the next step is pick_up',
                 ' \n Goal of the agent: open the purple door \n Observation 0: You carry a purple key, You see a wall 3 steps forward, You see a wall 5 steps left, You see a yellow key 1 step left and 1 step forward, You see a locked purple door 3 steps forward, You see a purple ball 1 step right and 1 step forward, You see a green box 1 step right \n Thought 0: In order to open the purple door, need to pick up purple key first and then toggle purple door, since you carry a purple key and now need to toggle the purple door, since observed locked purple door 3 steps forward, so the next step is go_forward \n Observation 1: You carry a purple key, You see a wall 2 steps forward, You see a wall 5 steps left, You see a yellow key 1 step left, You see a locked purple door 2 steps forward, You see a purple ball 1 step right \n Thought 1: In order to open the purple door, need to pick up purple key first and then toggle purple door, since you carry a purple key and now need to toggle the purple door, since observed locked purple door 2 steps forward, so the next step is go_forward \n Observation 2: You carry a purple key, You see a wall 1 step forward, You see a wall 5 steps left, You see a locked purple door 1 step forward \n Thought 2: In order to open the purple door, need to pick up purple key first and then toggle purple door, since you carry a purple key and now need to toggle the purple door, since observed locked purple door 1 steps forward, so the next step is toggle',
                 ' \n Goal of the agent: pick up green box \n Observation 0: You see a wall 2 steps forward, You see a wall 2 steps left, You see a yellow ball 1 step left and 1 step forward, You see a green box 2 steps right \n Thought 0: In order to pick up green box, need to find green box first, since observed green box 2 steps right, so the next step is turn_right \n Observation 1: You see a wall 2 steps left, You see a blue key 1 step right, You see a red ball 2 steps right and 1 step forward, You see a green box 2 steps forward \n Thought 1: In order to pick up green box, need to find green box first, since observed green box 2 steps forward, so the next step is go_forward \n Observation 2: You see a wall 2 steps left, You see a red ball 2 steps right, You see a green box 1 step forward \n Thought 2: In order to pick up green box, need to find green box first, since observed green box 1 steps forward, so the next step is pick_up']

prompt_hard_evn_subgoal = [' \n Goal of the agent: open the purple door \n Observation : You see a wall 3 steps forward, You see a wall 3 steps left, You see a yellow key 1 step right and 1 step forward, You see a locked purple door 2 steps right and 3 steps forward, You see a purple ball 3 steps right and 1 step forward, You see a green box 3 steps right, You see a purple key 2 steps left \n Thought : In order to open the purple door, need to pick up purple key first and then toggle purple door, since agent is not carrying purple key and observed purple key 2 steps left, so the next step is turn_left',
                           ' \n Goal of the agent: open the purple door \n Observation : You see a wall 3 steps forward, You see a wall 3 steps right, You see a purple key 2 steps forward \n Thought : In order to open the purple door, need to pick up purple key first and then toggle purple door, since agent is not carrying purple key and observed purple key 2 steps forward, so the next step is go_forward',
                           ' \n Goal of the agent: open the purple door \n Observation : You see a wall 3 steps forward, You see a wall 3 steps right, You see a purple key 2 steps forward \n Thought : In order to open the purple door, need to pick up purple key first and then toggle purple door, since agent is not carrying purple key and observed purple key 1 steps forward, so the next step is pick_up',
                          ' \n Goal of the agent: pick up yellow ball \n Observation : You see a wall 2 steps forward, You see a wall 2 steps left, You see a yellow ball 1 step left and 1 step forward, You see a green box 2 steps right \n Thought : In order to pick up yellow ball, need to find yellow ball first, since observed yellow ball 1 step left and 1 step forward, so the next step is go_forward',
                          ' \n Goal of the agent: pick up red ball \n Observation : You see a wall 2 steps left, You see a red ball 2 steps right, You see a green box 1 step forward \n Thought 2: In order to pick up red ball, need to find red ball first, since observed red ball 2 steps right, so the next step is turn_right']

subgoal_goto = ['\n Goal of the agent: go to the green ball \n Observation: You see a wall 2 step left, You see a green ball 3 steps forward, You see a grey ball 1 step right and 5 steps forward, You see a green key 2 steps right and 4 steps forward \n Thought: The mission is go to the green ball, since observed a green ball 3 steps forward, so the next step is go_forward',
                '\n Goal of the agent: go to the red ball \n Observation: You see a wall 5 steps forward, You see a wall 2 steps left, You see a grey key 1 step right and 2 steps forward, You see a red box 3 steps forward \n Thought: The mission is go to the red ball, since the agent did not observed a red ball, so the next step is turn_right or go_forward to explore',
                '\n Goal of the agent: go to the grey ball \n Observation: You see a green ball 3 steps forward, You see a grey ball 5 steps right, You see a red key 2 steps right and 4 steps forward \n Thought: The mission is go to the grey ball, since observed a grey ball 5 steps right, so the next step is turn_right'
               ]

subgoal_open = ['\n Goal of the agent: open the grey door \n Observation: You see a closed red door 2 steps left and 1 step forward, You see a grey key 2 steps right and 2 steps forward \n Thought: The mission is open the grey door, since agent is not carrying grey key and so the next subgoal is pick up the grey key, since observed grey key 2 steps right and 2 steps forward, so next step is go_forward',
                  '\n Goal of the agent: open the green door \n Observation: You see a wall 2 steps right, You see a green key 1 step forward, You see a closed grey door 1 step right and 2 steps forward \n Thought: The mission is open the green door, since agent is not carrying green key so the next subgoal is pick up the green key, since observed green key 1 steps forward, so next step is pick_up',
                  '\n Goal of the agent: open the red door \n Observation: You carry a red key, You see a wall 1 step left, You see a closed grey door 1 step left and 1 step forward, You see a yellow ball 1 step forward, You see a closed red door 2 steps right \n Thought: The mission is open the red door, since agent is carrying red key so the next subgoal is go to the red door, since observed red door 2 steps right, so next step is turn_right',
                  '\n Goal of the agent: open the yellow door \n Observation: You carry a yellow key, You see a closed grey door 3 steps left, You see a closed yellow door 1 step forward \n Thought: The mission is open the yellow door, since agent is carrying yellow key so the next subgoal is open the yellow door, since observed yellow door 1 step forward, so next step is toggle'
                 ]

subgoal_put = ['\n Goal of the agent: put the grey key next to the blue ball \n Observation: You see a wall 3 steps right, You see a blue ball 1 step left and 1 step forward, You see a grey key 1 step right and 1 step forward \n Thought: The mission is put the grey key next to the blue ball, since agent is not carrying grey key so the next subgoal is go to grey key, since observed grey key 1 step right and 1 step forward, so next step is go_forward',
                   '\n Goal of the agent: put the red key next to the blue ball \n Observation: You see a wall 2 steps left, You see a wall 3 steps right, You see a red key 1 step forward, You see a blue ball 2 steps right and 1 step forward \n Thought: The mission is put the red key next to the blue ball, since agent is not carrying red key so the next subgoal is go to red key, since observed red key 1 step forward, so next step is pick_up',
               '\n Goal of the agent: put the red ball next to the blue ball \n Observation: You carry a purple box, You see a wall 2 step forward, You see a wall 2 steps right, You see a red ball 1 step left \n Thought: The mission is put the red ball next to the blue ball, since agent is carrying purple box which is wrong, so next step is drop',
                   '\n Goal of the agent: put the grey key next to the blue ball \n Observation: You carry a grey key, You see a wall 2 steps left, You see a blue ball 1 step left and 2 steps forward, You see a blue key 1 step right \n Thought: The mission is put the grey key next to the blue ball, since agent is carrying grey key so the next subgoal is go to blue ball, since observed blue ball 1 step left and 2 steps forward, so next step is go_forward',
                   '\n Goal of the agent: put the grey key next to the blue ball \n Observation: You carry a blue ball, You see a wall 1 step right, You see a purple key 3 steps left and 1 step forward, You see a grey key 2 steps forward \n Thought: The mission is put the grey key next to the blue ball, since agent is carrying blue ball so the next subgoal is go to grey key, since observed grey key 2 steps forward, and next step is drop'
              ]

subgoal_pick = ['\n Goal of the agent: pick up a grey object \n Observation: You see a wall 3 steps right, You see a blue ball 1 step left and 1 step forward, You see a grey key 1 step right and 1 step forward \n Thought: The mission is pick up a grey object, since agent is not carrying any object so the next subgoal is go to a grey object, since observed grey key 1 step right and 1 step forward, so next step is go_forward',
                   '\n Goal of the agent: pick up the red key \n Observation: You see a wall 2 steps left, You see a wall 3 steps right, You see a red key 1 step forward, You see a blue ball 2 steps right and 1 step forward \n Thought: The mission is put the red key next to the blue ball, since agent is not carrying any key so the next subgoal is go to red key, since observed red key 1 step forward, so next step is pick_up',
               '\n Goal of the agent: pick up the red ball \n Observation: You carry a purple box, You see a wall 1 step forward, You see a wall 2 steps right, You see a red ball 1 step left \n Thought: The mission is pick up the red ball, since agent is carrying purple box which is wrong, so next step is drop'
              ]

highlevel_goto = ['\n Goal of the agent: go to the green ball \n Observation: You see a wall 2 step left, You see a green ball 3 steps forward, You see a grey ball 1 step right and 5 steps forward, You see a green key 2 steps right and 4 steps forward \n Thought: The mission is go to the green ball, since observed a green ball 2 steps forward 1 step right, so next steps are go_forward, go_forward, turn_right',
                  '\n Goal of the agent: go to the red ball \n Observation: You see a wall 5 steps forward, You see a wall 2 steps left, You see a grey key 1 step right and 2 steps forward, You see a red box 3 steps forward \n Thought: The mission is go to the red ball, since the agent did not observed a red ball, so the next step is turn_right or go_forward to explore',
                  '\n Goal of the agent: go to the red ball \n Observation: You see a wall 2 steps left, You see a blue key 3 step right and 2 steps forward, You see a red ball 3 steps forward \n Thought: The mission is go to the red ball, since observed a red ball 3 steps forward, so next steps are go_forward, go_forward'
                 ]

highlevel_open = ['\n Goal of the agent: open the grey door \n Observation: You see a closed red door 2 steps left and 1 step forward, You see a grey key 2 steps right and 2 steps forward \n Thought: The mission is open the grey door, since observed grey key 2 steps right and 2 steps forward, so next steps are go_forward, go_forward, turn_right, go_forward, pick_up',
                 '\n Goal of the agent: open the red door \n Observation: You carry a red key, You see a wall 1 step left, You see a closed grey door 1 step left and 1 step forward, You see a yellow ball 1 step forward, You see a closed red door 2 steps right \n Thought: The mission is open the red door, since agent is carrying red key and observed red door 2 steps right, so next steps are turn_right, go_forward, toggle'
                ]

highlevel_put = ['\n Goal of the agent: put the grey key next to the blue ball \n Observation: You see a wall 3 steps right, You see a blue ball 1 step left and 1 step forward, You see a grey key 1 step right and 1 step forward \n Thought: The mission is put the grey key next to the blue ball, since agent is not carrying grey key and observed grey key 1 step right and 1 step forward, so next steps are go_forward, turn_right',
                 '\n Goal of the agent: put the red key next to the blue ball \n Observation: You see a wall 2 steps left, You see a wall 3 steps right, You see a red key 1 step forward, You see a blue ball 2 steps right and 1 step forward \n Thought: The mission is put the red key next to the blue ball, since agent is not carrying red key and observed red key 1 step forward, so next step is pick_up',
                 '\n Goal of the agent: put the grey key next to the blue ball \n Observation: You carry a grey key, You see a wall 2 steps left, You see a blue ball 1 step left and 2 steps forward, You see a blue key 1 step right \n Thought: The mission is put the grey key next to the blue ball, since agent is carrying grey key and observed blue ball 1 step left and 2 steps forward, so next steps are go_forward, drop']

highlevel_pick = ['\n Goal of the agent: pick up a grey object \n Observation: You see a wall 3 steps right, You see a blue ball 1 step left and 1 step forward, You see a grey key 1 step right and 1 step forward \n Thought: The mission is pick up a grey object, since agent is not carrying any object and observed grey key 1 step right and 1 step forward, so next steps are go_forward, turn_right, pick_up',
                   '\n Goal of the agent: pick up the red key \n Observation: You see a wall 2 steps left, You see a wall 3 steps right, You see a red key 1 step forward, You see a blue ball 2 steps right and 1 step forward \n Thought: The mission is put the red key next to the blue ball, since agent is not carrying any key and observed red key 1 step forward, so next step is pick_up',
               '\n Goal of the agent: pick up the red ball \n Observation: You carry a purple box, You see a wall 1 step forward, You see a wall 2 steps right, You see a red ball 1 step left \n Thought: The mission is pick up the red ball, since agent is carrying purple box which is wrong, so next step is drop',
                  '\n Goal of the agent: pick up the purple key \n Observation: You see a purple key 2 steps left, You see a red key 1 step forward, You see a red ball 1 step right and 2 steps forward \n Thought: The mission is pick up the purple key, since agent is not carrying any key and observed purple key 2 steps left, so next steps are turn_left, go_forward, pick_up'
              ]

highlevel_subgoal_goto = ['\n Goal of the agent: go to the green ball \n Observation: You see a wall 2 step left, You see a green ball 3 steps forward, You see a grey ball 1 step right and 5 steps forward, You see a green key 2 steps right and 4 steps forward \n Thought: The mission is go to the green ball, since observed a green ball 2 steps forward 1 step right, so the next steps are go_forward, go_forward, turn_right',
                  '\n Goal of the agent: go to the red ball \n Observation: You see a wall 5 steps forward, You see a wall 2 steps left, You see a grey key 1 step right and 2 steps forward, You see a red box 3 steps forward \n Thought: The mission is go to the red ball, since the agent did not observed a red ball, so the next step is turn_right or go_forward to explore',
                  '\n Goal of the agent: go to the red ball \n Observation: You see a wall 2 steps left, You see a blue key 3 step right and 2 steps forward, You see a red ball 3 steps forward \n Thought: The mission is go to the red ball, since observed a red ball 3 steps forward, so the next steps are go_forward, go_forward'
                 ]

highlevel_subgoal_open = ['\n Goal of the agent: open the grey door \n Observation: You see a closed red door 2 steps left and 1 step forward, You see a grey key 2 steps right and 2 steps forward \n Thought: The mission is open the grey door, since agent is not carrying grey key and so the next subgoal is pick up the grey key, since observed grey key 2 steps right and 2 steps forward, so next steps are go_forward, go_forward, turn_right, go_forward, pick_up',
                         '\n Goal of the agent: open the red door \n Observation: You carry a red key, You see a wall 1 step left, You see a closed grey door 1 step left and 1 step forward, You see a yellow ball 1 step forward, You see a closed red door 2 steps right \n Thought: The mission is open the red door, since agent is carrying red key so the next subgoal is unlock the red door, since observed red door 2 steps right, so next steps are turn_right, go_forward, toggle']

highlevel_subgoal_put = ['\n Goal of the agent: put the grey key next to the blue ball \n Observation: You see a wall 3 steps right, You see a blue ball 1 step left and 1 step forward, You see a grey key 1 step right and 1 step forward \n Thought: The mission is put the grey key next to the blue ball, since agent is not carrying grey key so the next subgoal is pick up grey key, since observed grey key 1 step right and 1 step forward, so next steps are go_forward, turn_right',
                        '\n Goal of the agent: put the grey key next to the blue ball \n Observation: You carry a grey key, You see a wall 2 steps left, You see a blue ball 1 step left and 2 steps forward, You see a blue key 1 step right \n Thought: The mission is put the grey key next to the blue ball, since agent is carrying grey key so the next subgoal is go to blue ball, since observed blue ball 1 step left and 2 steps forward, so next steps are go_forward, drop']

highlevel_subgoal_pick = ['\n Goal of the agent: pick up a grey object \n Observation: You see a wall 3 steps right, You see a blue ball 1 step left and 1 step forward, You see a grey key 1 step right and 1 step forward \n Thought: The mission is pick up a grey object, since agent is not carrying any object so the next subgoal is go to a grey object, since observed grey key 1 step right and 1 step forward, so next steps are go_forward, turn_right, pick_up',
                   '\n Goal of the agent: pick up the red key \n Observation: You see a wall 2 steps left, You see a wall 3 steps right, You see a red key 1 step forward, You see a blue ball 2 steps right and 1 step forward \n Thought: The mission is put the red key next to the blue ball, since agent is not carrying any key so the next subgoal is go to red key, since observed red key 1 step forward, so next step is pick_up',
         '\n Goal of the agent: pick up the red ball \n Observation: You carry a purple box, You see a wall 1 step forward, You see a wall 2 steps right, You see a red ball 1 step left \n Thought: The mission is pick up the red ball, since agent is carrying purple box which is wrong, so next step is drop',
            '\n Goal of the agent: pick up a red object \n Observation: You see a wall 3 steps right, You see a blue ball 1 step left and 1 step forward, You see a red key 2 steps right \n Thought: The mission is pick up a red object, since agent is not carrying any object so the next subgoal is go to a red object, since observed red key 2 steps right, so next steps are turn_right, go_forward, pick_up',
              ]