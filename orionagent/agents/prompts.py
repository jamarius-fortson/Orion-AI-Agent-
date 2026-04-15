import json

from orionagent.utils.date_utils import get_current_time_and_date
from orionagent.utils.function_utils import transform_to_openai_function


planning_prompt_template = """
ä½ æ˜¯{agent_name}ï¼Œ{agent_bio}
{agent_instructions}
å½“å‰é˜¶æ®µæ˜¯ä»»åŠ¡è§„åˆ’é˜¶æ®µï¼Œä½ å°†ç»™å®šç›®æ ‡æˆ–é—®é¢˜ï¼Œä½ çš„å†³ç­–å°†ç‹¬ç«‹æ‰§è¡Œè€Œä¸ä¾èµ–äºŽäººç±»çš„å¸®åŠ©ï¼Œè¯·å‘æŒ¥LLMçš„ä¼˜åŠ¿å¹¶ä¸”è¿½æ±‚é«˜æ•ˆçš„ç­–ç•¥è¿›è¡Œä»»åŠ¡è§„åˆ’ã€‚
1.ä½ æœ‰~4000å­—çš„çŸ­æœŸè®°å¿†
2.ä¸éœ€è¦ç”¨æˆ·çš„å¸®åŠ©
3.è§„åˆ’çš„æ—¶å€™å¯ä»¥ç”¨å‚è€ƒå·¥å…·ä¸­æåˆ°çš„å·¥å…·
4.äº’è”ç½‘æœç´¢ã€ä¿¡æ¯èšåˆå’Œé‰´åˆ«çœŸä¼ªçš„èƒ½åŠ›
5.ä¿æŒè°¦é€Šï¼Œå¯¹è‡ªå·±æ²¡æŠŠæ¡çš„é—®é¢˜ï¼Œå°½å¯èƒ½è°ƒç”¨commandï¼Œä½†å°½é‡å°‘è°ƒç”¨ï¼Œä¸èƒ½é‡å¤è°ƒç”¨
6.å½“ä½ ä»Žè‡ªèº«çŸ¥è¯†æˆ–è€…åŽ†å²è®°å¿†ä¸­èƒ½å¾—å‡ºç»“è®ºï¼Œè¯·èªæ˜Žä¸”é«˜æ•ˆï¼Œå®Œæˆä»»åŠ¡å¹¶å¾—å‡ºç»“è®º
7.ç»å¸¸å»ºè®¾æ€§åœ°è‡ªæˆ‘æ‰¹è¯„æ•´ä¸ªè¡Œä¸ºå¤§å±€ï¼Œåæ€è¿‡åŽ»çš„å†³ç­–å’Œç­–ç•¥ï¼Œä»¥æ”¹è¿›ä½ çš„æ–¹æ³•
8.ä½ æœ€å¤šåªèƒ½è¿›è¡Œ{max_iter_num}æ­¥æ€è€ƒï¼Œè§„åˆ’{max_iter_num}ä¸ªä»»åŠ¡ï¼Œæ‰€ä»¥å°½å¯èƒ½é«˜æ•ˆè§„åˆ’ä»»åŠ¡
9.ä½ æœ‰åæ€èƒ½åŠ›ï¼Œå¦‚æžœå·²å®Œæˆçš„ä»»åŠ¡å’Œç»“æžœæš‚ä¸èƒ½å¾—åˆ°å›žç­”é—®é¢˜æ‰€éœ€ä¿¡æ¯æˆ–å°šä¸èƒ½å®Œæˆç›®æ ‡ï¼Œåº”ç»§ç»­è§„åˆ’ï¼Œä½†ä¸èƒ½è·Ÿä¹‹å‰ä»»åŠ¡é‡å¤

{tool_specification}

{current_date_and_time}

{memory}

GOAL:{goal}

\næ ¹æ®ç›®æ ‡å’Œå·²æœ‰ä»»åŠ¡ï¼Œè§„åˆ’ä¸€ä¸ªæ–°Task(ä¸èƒ½é‡å¤)ï¼Œä½ åªèƒ½ä»¥ä»¥ä¸‹jsonåˆ—è¡¨çš„æ ¼å¼ç”ŸæˆTask
{{
    "task_name": "ä»»åŠ¡æè¿°",
    "command":{{
        "name":"command name",
        "args":{{
            "arg name":"value"
        }}
    }}
}}
ç¡®ä¿Taskå¯ä»¥è¢«Pythonçš„json.loadsè§£æž

å½“å·²å®Œæˆçš„Taskså·²ç»èƒ½å¤Ÿå¸®åŠ©å›žç­”è¿™ä¸ªç›®æ ‡ï¼Œåˆ™å°½å¯èƒ½ç”Ÿæˆä»»åŠ¡å®ŒæˆTaskï¼Œå¦åˆ™ç”Ÿæˆä¸€ä¸ªå…¶ä»–Taskã€‚ä¸€ä¸ªæ–°Task:
""".strip()

planning_prompt_template_en = """
You are a {agent_name}ï¼Œ{agent_bio}
{agent_instructions}
Currently, you are in the task planning phase, where you will be given specific goals or problems to address. \
Your decisions will be executed independently without relying on human assistance. \
Please utilize LLM's advantages and pursue efficient strategies for task planning.\

1. You have a short-term memory of approximately 4,000 characters.
2. You do not require assistance from users.
3. You can use the reference tools mentioned when planning.
4. You have the abilities to perform internet searches, aggregate information, and discern between genuine and fake information.
5. Remain humble and, if unsure about an issue, make use of commands when possible but minimize their usage and avoid repetition.
6. When drawing conclusions from your knowledge or historical memory, be clever and efficient in task completion and conclusion.
7. Regularly engage in constructive self-criticism to reflect on past decisions and strategies and improve your approach.
8. You can think and plan up to {max_iter_num} steps, so strive to plan tasks as efficiently as possible.
9. You have the capability for reflection; if a completed task and its results cannot provide the necessary information to answer a question or achieve a goal, continue planning but avoid repeating previous tasks.

{tool_specification}

{current_date_and_time}

{memory}

GOAL:{goal}

\nBased on the goal and existing tasks, plan a new Task (no repetitions), and you can only generate the Task in the following json list format:
{{
    "task_name": "task description",
    "command":{{
        "name":"command name",
        "args":{{
            "arg name":"value"
        }}
    }}
}}
Ensure that the Task can be parsed by Python's json.loads function. 

If the already completed Tasks are sufficient to answer the goal, then try to generate the Task to complete it as much as possible. Otherwise, create another Task. 
A new Task:
""".strip()


conclusion_prompt_template = """
ä½ æ˜¯{agent_name}ï¼Œ{agent_bio}ï¼Œ{agent_instructions}
å½“å‰é˜¶æ®µæ˜¯æ€»ç»“é˜¶æ®µï¼Œåœ¨å‰å‡ æ¬¡äº¤äº’ä¸­ï¼Œå¯¹äºŽç”¨æˆ·ç»™å®šçš„ç›®æ ‡å’Œé—®é¢˜ï¼Œä½ å·²ç»é€šè¿‡è‡ªå·±æœå¯»å‡ºäº†ä¸€å®šä¿¡æ¯ï¼Œä½ éœ€è¦æ•´åˆè¿™äº›ä¿¡æ¯ç”¨ä¸­æ–‡ç»™å‡ºæœ€ç»ˆçš„ç»“è®ºã€‚
1. æœå¯»çš„ä¿¡æ¯ä»Žå¾ˆå¤šå·¥å…·ä¸­èŽ·å–ï¼Œä¼šå‡ºçŽ°å†—ä½™
2. å½“ä¸åŒå·¥å…·èŽ·å–çš„ä¿¡æ¯å†²çªçš„æ—¶å€™ï¼Œä½ åº”è¯¥éµå¾ªä¸€å®šçš„ä¼˜å…ˆçº§(Wiki > search)åŽ»è§£å†³å†²çª

{current_date_and_time}

{memory}

é—®é¢˜æˆ–ç›®æ ‡ï¼š{goal}\nç”Ÿæˆå¯¹ç”¨æˆ·æœ‰å¸®åŠ©çš„ä¸­æ–‡å›žç­”:
"""

conclusion_prompt_template_en = """
You are a {agent_name},{agent_bio},{agent_instructions}
The current stage is the concluding stage. In the previous interactions, \
you have already found some information by searching on your own for the user's given goals and problems. \
You need to integrate this information and provide the final conclusion in Chinese.
If there is information from Knowledge info, and the information can answer the question, \
you can use the Knowledge info information as much as possible to answer the question without using external tool results or creating your own content.
1. The information you search for comes from many sources and may be redundant.
2. When the information obtained from different tools conflicts, you should follow a certain priority (Knowledge info > Wiki > search) to resolve the conflict.

{current_date_and_time}

{memory}

Goal: {goal}
Generate helpful answers **in English** for users:
"""


def make_planning_prompt(agent_profile, goal, used_tools, memory, max_tokens_num, tokenizer, lang="en"):
    tool_spec = make_tool_specification(used_tools, lang)
    template = planning_prompt_template if lang == "zh" else planning_prompt_template_en
    prompt = template.format(**{
        "agent_name": agent_profile.name,
        "agent_bio": agent_profile.bio,
        "agent_instructions": agent_profile.instructions,
        "max_iter_num": agent_profile.max_iter_num,
        "tool_specification": tool_spec,
        "current_date_and_time": get_current_time_and_date(lang),
        "memory": memory,
        "goal": goal
    })
    prompt = prompt_truncate(tokenizer, prompt, memory, max_tokens_num)
    return prompt


def make_tool_specification(tools, lang="en"):
    functions = [transform_to_openai_function(t) for t in tools]

    commands, cnt = [], 1
    for f in functions:
        func_str = json.dumps(f, ensure_ascii=False)
        commands.append(f"{cnt}:{func_str}")
        cnt += 1

    used_commands = "\n".join(commands)

    tool_spec = f'Commands:\n{used_commands}\n'

    return tool_spec


def make_task_conclusion_prompt(agent_profile, goal, memory, max_tokens_num, tokenizer, lang="en"):
    template = conclusion_prompt_template if lang == "zh" else conclusion_prompt_template_en
    prompt = template.format(**{
        "agent_name": agent_profile.name,
        "agent_bio": agent_profile.bio,
        "agent_instructions": agent_profile.instructions,
        "current_date_and_time": get_current_time_and_date(lang),
        "memory": memory,
        "goal": goal
    })
    prompt = prompt_truncate(tokenizer, prompt, memory, max_tokens_num)
    return prompt


def make_no_task_conclusion_prompt(query, conversation_history=""):
    prompt = ""
    if conversation_history:
        for tmp in conversation_history[-3:]:
            prompt += f"User: {tmp['query']}\nAssistant:{tmp['answer']}\n"
        prompt += f"User: {query}\nAssistant:"
    else:
        prompt = query
    return prompt


def prompt_truncate(tokenizer, prompt, memory, input_max_length):
    kwargs = dict(add_special_tokens=False)
    prompt_tokens = tokenizer.encode(prompt, **kwargs)
    if len(prompt_tokens) > input_max_length:
        if memory is None or memory not in prompt:
            prompt_tokens = prompt_tokens[:input_max_length//2] + prompt_tokens[-input_max_length//2:]
        else:
            memory_prompt_tokens = tokenizer.encode(memory, add_special_tokens=False)
            sublst_len = len(memory_prompt_tokens)
            start_index = None
            for i in range(len(prompt_tokens) - sublst_len + 1):
                if prompt_tokens[i:i+sublst_len] == memory_prompt_tokens:
                    start_index = i
                    break
            
            if start_index is None:
                prompt_tokens = prompt_tokens[:input_max_length//2] + prompt_tokens[-input_max_length//2:]
            else:
                other_len = len(prompt_tokens) -  sublst_len
                if input_max_length > other_len:
                    max_memory_len = input_max_length - other_len
                    memory_prompt_tokens = memory_prompt_tokens[:max_memory_len//2] + memory_prompt_tokens[-max_memory_len//2:]
                    prompt_tokens = prompt_tokens[:start_index] + memory_prompt_tokens + prompt_tokens[start_index + sublst_len:]
    prompt = tokenizer.decode(prompt_tokens, skip_special_tokens=True)
    return prompt
