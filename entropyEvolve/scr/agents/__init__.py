"""
Módulo de agentes - Réplica exacta de swe_bench/agents/__init__.py
"""

from .promts import (
    BASE_AGENT, 
    TASK_IMPROVEMENT_REASONER, 
    META_IMPROMENT_GENERATOR,
    BASE_AGENT_STR,
    TASK_IMPROVEMENT_REASONER_STR,
    META_IMPROMENT_GENERATOR_STR
)
from .src import Agent, CodeAgent, MetaImprovementAgent, TaskIprovementAgent
from .calling import agent_prompt, SafeDict

__all__ = [
    'BASE_AGENT',
    'TASK_IMPROVEMENT_REASONER',
    'META_IMPROMENT_GENERATOR',
    'BASE_AGENT_STR',
    'TASK_IMPROVEMENT_REASONER_STR',
    'META_IMPROMENT_GENERATOR_STR',
    'Agent',
    'CodeAgent',
    'MetaImprovementAgent',
    'TaskIprovementAgent',
    'agent_prompt',
    'SafeDict'
]

