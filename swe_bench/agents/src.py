from .promts import BASE_AGENT,TASK_IMPROVEMENT_REASONER,META_IMPROMENT_GENERATOR

class Agent():
    def __init__(self,prompt:str):
        self.prompt = prompt

class TaskIprovementAgent(Agent):
    def __init__(self, prompt=TASK_IMPROVEMENT_REASONER):
        super().__init__(prompt)


class MetaImprovementAgent(Agent):
    def __init__(self, prompt=META_IMPROMENT_GENERATOR):
        super().__init__(prompt)

class CodeAgent(Agent):
    def __init__(self, prompt):
        super().__init__(prompt)
        self.id:int
    
    def set_id(self,id):
        self.id = id
    