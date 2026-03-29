"""
Módulo de agentes

Para LangGraph: usa AgentFunctions
Para uso directo: usa las clases y prompts individuales
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
from .agent_functions import AgentFunctions, format_predictions_for_evaluation, parse_swebench_instance

__all__ = [
    # Prompts
    'BASE_AGENT',
    'TASK_IMPROVEMENT_REASONER',
    'META_IMPROMENT_GENERATOR',
    'BASE_AGENT_STR',
    'TASK_IMPROVEMENT_REASONER_STR',
    'META_IMPROMENT_GENERATOR_STR',
    # Clases
    'Agent',
    'CodeAgent',
    'MetaImprovementAgent',
    'TaskIprovementAgent',
    # Utilidades
    'agent_prompt',
    'SafeDict',
    # LangGraph Functions (⭐ NUEVO)
    'AgentFunctions',
    'format_predictions_for_evaluation',
    'parse_swebench_instance'
]

