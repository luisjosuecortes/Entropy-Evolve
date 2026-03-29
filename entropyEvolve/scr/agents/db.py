"""
Base de datos en memoria para agentes
Réplica exacta de swe_bench/agents/db.py
"""

from .src import CodeAgent


class DataBase():
    """Base de datos simple para almacenar agentes"""
    def __init__(self):
        self.len = -1
        self.agents = []
    
    def add(self, agent: CodeAgent):
        """Añade un agente y le asigna un ID"""
        agent.set_id(self.len + 1)
        self.len = self.len + 1
        self.agents.append(agent)

    def get_agents(self):
        """Retorna todos los agentes"""
        return self.agents

