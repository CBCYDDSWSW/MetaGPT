from pydantic import BaseModel


class ExpRetriever(BaseModel):
    """interface for experience retriever"""

    def retrieve(self, context: str) -> str:
        raise NotImplementedError


class SimplePlanningExpRetriever(ExpRetriever):
    """A simple experience retriever that returns manually crafted planning examples."""

    EXAMPLE: str = """
    ## example 1
    User Requirement: Create a cli snake game
    Explanation: The requirement is about software development. Assign each tasks to a different team member based on their expertise.
    ```json
    [
        {
            "command_name": "append_task",
            "args": {
                "task_id": "1",
                "dependent_task_ids": [],
                "instruction": "Create a product requirement document (PRD) outlining the features, user interface, and user experience of the CLI snake game.",
                "assignee": "Alice"
            }
        },
        {
            "command_name": "append_task",
            "args": {
                "task_id": "2",
                "dependent_task_ids": ["1"],
                "instruction": "Design the software architecture for the CLI snake game, including the choice of programming language, libraries, and data flow.",
                "assignee": "Bob"
            }
        },
        {
            "command_name": "append_task",
            "args": {
                "task_id": "3",
                "dependent_task_ids": ["2"],
                "instruction": "Break down the architecture into manageable tasks, identify task dependencies, and prepare a detailed task list for implementation.",
                "assignee": "Eve"
            }
        },
        {
            "command_name": "append_task",
            "args": {
                "task_id": "4",
                "dependent_task_ids": ["3"],
                "instruction": "Implement the core game logic for the CLI snake game, including snake movement, food generation, and score tracking.",
                "assignee": "Alex"
            }
        },
        {
            "command_name": "append_task",
            "args": {
                "task_id": "5",
                "dependent_task_ids": ["4"],
                "instruction": "Write comprehensive tests for the game logic and user interface to ensure functionality and reliability.",
                "assignee": "Edward"
            }
        }
    ]
    ```

    ## example 2
    User requirement: Run data analysis on sklearn Wine recognition dataset, include a plot, and train a model to predict wine class (20% as validation), and show validation accuracy.
    Explanation: DON'T decompose requirement if it is a DATA-RELATED task, assign a single task directly to Data Analyst David. He will manage the decomposition and implementation.
    ```json
    [
        {
            "command_name": "append_task",
            "args": {
                "task_id": "1",
                "dependent_task_ids": [],
                "instruction": "Run data analysis on sklearn Wine recognition dataset, include a plot, and train a model to predict wine class (20% as validation), and show validation accuracy.",
                "assignee": "David"
            }
        }
    ]
    ```

    ## example 3
    Conversation History:
    [
        ...,
        {'role': 'assistant', 'content': 'id: 739d9b4983fd4e97a0f78fde5e9ef158, from Alice(Product Manager) to {'Bob'}: {'docs': {'20240424153821.json': {'root_path': 'docs/prd', 'filename': '20240424153821.json', 'content': '{"Language":"en_us","Programming Language":"Python","Original Requirements":"create a cli snake game","Project Name":"snake_game","Product Goals":["Develop an intuitive and addictive snake game",...], ...}}}}},
    ]
    Explanation: You received a message from Alice, the Product Manager, that she has completed the PRD, use finish_current_task, this marks her task as finished and moves the plan to the next task.
    ```json
    [
        {
            "command_name": "finish_current_task",
            "args": {}
        }
    ]
    ```
    """

    def retrieve(self, context: str = "") -> str:
        return self.EXAMPLE


class SimpleRoutingExpRetriever(ExpRetriever):
    """A simple experience retriever that returns manually crafted routing examples."""

    EXAMPLE: str = """
    ## example 1: Forward a message from one team member to another
    Conversation History:
    [
        ...,
        {'role': 'assistant', 'content': 'id: 739d9b4983fd4e97a0f78fde5e9ef158, from Alice(Product Manager) to {'Bob'}: {'docs': {'20240424153821.json': {'root_path': 'docs/prd', 'filename': '20240424153821.json', 'content': '{"Language":"en_us","Programming Language":"Python","Original Requirements":"create a cli snake game","Project Name":"snake_game","Product Goals":["Develop an intuitive and addictive snake game",...], ...}}}}},
        {'role': 'assistant', 'content': 'Based on the feedback from Alice, the Product Manager, it seems that the PRD for the snake game has been successfully created. Since the PRD is complete and there are no indications of issues with the task, we can mark the current task as finished and move on to the next task in the plan. The next task is assigned to Bob, the Architect, who will be responsible for designing the software architecture for the game based on the PRD provided by Alice.\n\nHere are the commands to update the plan status:\n\n```json\n[\n    {\n        "command_name": "finish_current_task"\n    }\n]\n```'}
    ]
    Command:
    ```json
    [
        {
            "command_name": "forward_message",
            "args": {
                "message_id": "739d9b4983fd4e97a0f78fde5e9ef158"
            }
        }
    ]
    """

    def retrieve(self, context: str = "") -> str:
        return self.EXAMPLE
