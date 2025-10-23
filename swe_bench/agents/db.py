from .src import CodeAgent

class DataBase():
    def __init__(self):
        self.len = -1
        self.agents = []
    
    def add(self,agent:CodeAgent):
        agent.set_id(self.len + 1)
        self.len = self.len + 1
        self.agents.append(agent)

    def get_agents(self):
        return self.agents