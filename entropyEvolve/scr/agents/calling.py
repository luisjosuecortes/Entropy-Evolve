"""
Utilidades para formateo de prompts
Réplica exacta de swe_bench/agents/calling.py
"""

from .src import Agent


class SafeDict(dict):
    """Dict que retorna {key} si la clave no existe"""
    def __missing__(self, key):
        return "{" + key + "}"


def agent_prompt(values: dict, agent: Agent):
    """
    Formatea el prompt del agente con los valores dados.
    Compatible con LangChain PromptTemplate.
    """
    if agent.prompt_template:
        return agent.prompt_template.format(**values)
    return agent.prompt.format_map(SafeDict(values))

