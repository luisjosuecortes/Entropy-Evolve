from .src import Agent

class SafeDict(dict):
    def __missing__(self, key):
        return "{" + key + "}"

def agent_prompt(values:dict,agent:Agent):
    formated_promt = agent.prompt.format_map(SafeDict(values))
    return formated_promt


