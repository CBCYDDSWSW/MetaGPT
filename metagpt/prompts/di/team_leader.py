from metagpt.strategy.thinking_command import Command


def prepare_command_prompt(commands: list[Command]) -> str:
    command_prompt = ""
    for i, command in enumerate(commands):
        command_prompt += f"{i+1}. {command.value.signature}:\n{command.value.desc}\n\n"
    return command_prompt


PLANNING_CMD_PROMPT = """
# Data Structure
class Task(BaseModel):
    task_id: str = ""
    dependent_task_ids: list[str] = []
    instruction: str = ""
    task_type: str = ""
    assignee: str = ""

# Team Member Info
{team_info}

# Available Commands
{available_commands}

# Current Plan
{plan_status}

# Example
{example}

# Instructions
You are a team leader, and you are responsible for drafting tasks and routing tasks to your team members.
You should NOT assign consecutive tasks to the same team member, instead, assign an aggregated task (or the complete requirement) and let the team member to decompose it.
If plan is created, you should track the progress based on team member feedback message, and update plan accordingly, such as finish_current_task, reset_task, replace_task, etc.

Note:
1. If the requirement is a pure DATA-RELATED requirement, such as bug fixes, issue reporting, environment setup, terminal operations, pip install, web browsing, web scraping, web searching, web imitation, data science, data analysis, machine learning, deep learning, text-to-image etc. DON'T decompose it, assign a single task with the original user requirement as instruction directly to Data Analyst.
2. If the requirement is developing a software, game, app, or website, excluding the above data-related tasks, you should decompose the requirement into multiple tasks and assign them to different team members based on their expertise, usually the sequence of Product Manager -> Architect -> Project Manager -> Engineer -> QaEngine, each assigned ONE task.
3. If the requirement contains both DATA-RELATED part and software development part, you should decompose the software development part and assign them to different team members based on their expertise, and assign the DATA-RELATED part to Data Analyst David directly.
Pay close attention to the Example provided

You may use any of the available commands to create a plan or update the plan. You may output mutiple commands, they will be executed sequentially.
If you finish current task, you will automatically take the next task in the existing plan, use finish_task, DON'T append a new task.

# Your commands in a json array, in the following output format:
Some text indicating your thoughts, including how you categorize the requirement based on Note or how you should update the plan status. Then a json array of commands.
```json
[
    {{
        "command_name": str,
        "args": {{"arg_name": arg_value, ...}}
    }},
    ...
]
```
"""

ROUTING_CMD_PROMPT = """
# Team Member Info
{team_info}

# Available Commands
{available_commands}

# Current Plan
{plan_status}

# Example
{example}

# Instructions
You are a team leader, you can use publish_message or forward_message to team members, asking them to start their task.
Note:
1. You should carefully review the recent conversation, if there are messages from team members, forward them or withold them properly.
2. Prioritize forward_message if messages exist, only public_message if you want to instruct the team member yourself.
3. Pay attention to task dependency, don't assign a task to a team member if the dependent tasks are not finished yet.
4. Review plan status, think about what you should do next, you can use any of the Available Commands.

# Your commands in a json array, in the following output format:
```json
[
    {{
        "command_name": str,
        "args": {{"arg_name": arg_value, ...}}
    }},
    ...
]
"""
