"""Evalate by llm."""
import inspect
import json
from typing import Any, Callable

from pydantic import Field

from metagpt.exp_pool.schema import Score
from metagpt.exp_pool.scorers.base import ExperienceScorer
from metagpt.llm import LLM
from metagpt.provider.base_llm import BaseLLM
from metagpt.utils.common import parse_json_code_block

SIMPLE_SCORER_TEMPLATE = """
Role: You're an expert score evaluator. You specialize in assessing the output of the given function, based on its intended requirement and produced result.

## Context
### Function Name
{func_name}

### Function Document
{func_doc}

### Function Signature
{func_signature}

### Function Parameters
args: {func_args}
kwargs: {func_kwargs}

### Produced Result By Function and Parameters
{func_result}

## Format Example
```json
{{
    "val": "the value of the score, int from 1 to 10, higher is better.",
    "reason": "an explanation supporting the score."
}}
```

## Instructions
- Understand the function and requirements given by the user.
- Analyze the results produced by the function.
- Grade the results based on level of alignment with the requirements.
- Provide a score on a scale defined by user or a default scale (1 to 10).

## Constraint
Format: Just print the result in json format like **Format Example**.

## Action
Follow instructions, generate output and make sure it follows the **Constraint**.
"""


class SimpleScorer(ExperienceScorer):
    llm: BaseLLM = Field(default_factory=LLM)

    async def evaluate(self, func: Callable, result: Any, args: tuple = None, kwargs: dict = None) -> Score:
        """Evaluate the quality of content."""

        prompt = SIMPLE_SCORER_TEMPLATE.format(
            func_name=func.__name__,
            func_doc=func.__doc__,
            func_signature=inspect.signature(func),
            func_args=args,
            func_kwargs=kwargs,
            func_result=result,
        )
        resp = await self.llm.aask(prompt)
        resp_json = json.loads(parse_json_code_block(resp)[0])

        return Score(**resp_json)
