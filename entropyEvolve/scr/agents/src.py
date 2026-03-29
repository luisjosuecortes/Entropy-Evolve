"""
Clases de Agentes migradas a LangChain
Réplica exacta de swe_bench/agents/src.py pero integrando LangChain
"""

from langchain_core.prompts import PromptTemplate
from .promts import BASE_AGENT, TASK_IMPROVEMENT_REASONER, META_IMPROMENT_GENERATOR


class Agent():
    """Clase base para todos los agentes"""
    def __init__(self, prompt):
        """
        Args:
            prompt: Puede ser un string o un PromptTemplate de LangChain
        """
        if isinstance(prompt, PromptTemplate):
            self.prompt_template = prompt
            self.prompt = prompt.template
        else:
            # String o cualquier otro tipo
            self.prompt = prompt
            self.prompt_template = None


class TaskIprovementAgent(Agent):
    """Agente para análisis de mejoras en tareas"""
    def __init__(self, prompt=TASK_IMPROVEMENT_REASONER):
        super().__init__(prompt)


class MetaImprovementAgent(Agent):
    """Agente para generar mejoras meta-nivel"""
    def __init__(self, prompt=META_IMPROMENT_GENERATOR):
        super().__init__(prompt)


class CodeAgent(Agent):
    """Agente para generación de código"""
    def __init__(self, prompt):
        super().__init__(prompt)
        self.id: int = None
    
    def set_id(self, id: int):
        """Asigna un ID al agente"""
        self.id = id

