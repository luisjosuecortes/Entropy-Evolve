import numpy as np
import multiprocessing as mp
import random
from datasets import load_dataset,disable_progress_bar
import asyncio
from openai import OpenAI,AsyncOpenAI
import os
import json
import subprocess
import re
from string import Template

from agents import CodeAgent,MetaImprovementAgent,TaskIprovementAgent
from agents.db import DataBase
from agents.promts import BASE_AGENT
from agents.calling import agent_prompt,SafeDict
from agents.promts import TASK_IMPROVEMENT_REASONER,META_IMPROMENT_GENERATOR

# {
#         "instance_id": "astropy__astropy-14182",
#         "model_patch": "```diff\ndiff --git a/astropy/io/ascii/core.py b/astropy/io/ascii/core.py\n--- a/astropy/io/ascii/core.py\n+++ b/astropy/io/ascii/core.py\n@@ -171,7 +171,7 @@ class RST(Writer):\n \n     def __init__(self, **kwargs):\n         super().__init__(**kwargs)\n-        # Additional initialization code\n+        self.header_rows = kwargs.get('header_rows', None)\n \n     def write(self, table, **kwargs):\n         # Implementation of the write method\n         if self.header_rows is not None:\n             # Handle header rows in the output\n             pass\n```",
#         "model_name_or_path": "gpt-4o-mini"
# }
disable_progress_bar()

client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

client_sync = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

async def get_swebench_code(agent:CodeAgent,instance_id: str,repo:str,problem_statement:str,test_patch:str,semaphore) -> dict:

    values = {"repo":repo,"problem_statement":problem_statement,"test_patch":test_patch}
    template = Template(agent.prompt)
    prompt = template.safe_substitute(values)

    async with semaphore:
        try:
            resp = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}]
            )
            code = resp.choices[0].message.content
            return {"instance_id": instance_id, "model_patch": code,"model_name_or_path":"model-"+str(agent.id)}
        except Exception as e:
            return {"instance_id": instance_id, "error": str(e)}

def get_log(log_file):
    with open(log_file, "r") as f:
        lineas = f.readlines()
    return "\n".join(lineas[:50])

def get_task_improments(model_id,logs_file,predictions_file,swebench):

    os.makedirs("task_improvement/"+"model-"+str(model_id)+"/", exist_ok=True)
    print("Carpeta ","task_improvement/"+"model-"+str(model_id)+"/"+" creada")
    with open(predictions_file, 'r') as file:
            predictions = json.load(file)
    #logs/run_evaluation/'run_id'/'model_id'/
    instaces_ids = os.listdir(logs_file)

    for instance_id in instaces_ids:
            log_file = logs_file+'/'+instance_id+"/run_instance.log"

            filtered = swebench.filter(lambda ex: ex["instance_id"] == instance_id)
            
            problem_statement = filtered[0]['problem_statement']
            test_patch = filtered[0]['test_patch']
            predicted_patch = next((x for x in predictions if x["instance_id"] == instance_id), None)["model_patch"]
            agent_patch_log = get_log(log_file)
            correct_patch =  filtered[0]['patch']
            
            template = Template(TASK_IMPROVEMENT_REASONER)
            prompt = template.substitute(problem_statement=problem_statement,test_patch=test_patch,predicted_patch=predicted_patch,agent_patch_log=agent_patch_log,patch=correct_patch)
        
            try:
                    response = client_sync.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.0
                    )

                    patch = response.choices[0].message.content.strip()

                    with open("task_improvement/"+"model-"+str(model_id)+"/"+instance_id+".json", "w") as fichero:
                            fichero.write(patch)

            except Exception as e:
                    print(f"Error en {instance_id}: {e}")
                    continue  
def get_analysis(directory:str):
    tasks_improvement = os.listdir(directory)

    analysis = ""
    for task in tasks_improvement:
        with open(directory+'/'+task, 'r') as file:
            task_info = json.load(file)
        potential_improvements = task_info["potential_improvements"]
        joined_analyses = "\n".join(f"- {a}" for a in potential_improvements)
        analysis += joined_analyses
    return analysis

def test_agent(path):
     with open(path,"r") as agent:
        agent_json = json.load(agent)

        template = Template(agent_json["new_agent"])

        values = {"repo":"","problem_statement":"","test_patch":""}

        template.substitute(values)



def run_evolving_algorithm(num_iters:int,n_samples:int):
    
    def get_responses(data,current_agent):
        semaphore = asyncio.Semaphore(3)
        async def run_all(data,current_agent):
            tasks = [get_swebench_code(current_agent,row['instance_id'],row['repo'],row['problem_statement'],row['test_patch'],semaphore) for row in data]
            return await asyncio.gather(*tasks)

        return asyncio.run(run_all(data,current_agent))
         
    #Carga de swe-bench
    swebench =  load_dataset('princeton-nlp/SWE-bench_Lite', split='test')
    database = DataBase()

    initial_code_agent = CodeAgent(prompt=BASE_AGENT)
    
    current_agent = initial_code_agent
    best_agent = initial_code_agent
    database.add(current_agent)

    for iter in range(num_iters):
        data = swebench.shuffle().select(range(n_samples))


        print("Creando respuestas de iteracion ",iter)
        results =  get_responses(data,current_agent)

        with open("predictions/model-"+str(current_agent.id)+".json", "w") as f:
            json.dump(results, f)
        print("Respuestas guardadas en: ","predictions/model-"+str(current_agent.id)+".json")

        cmd = [
            "python", "-m", "swebench.harness.run_evaluation",
            "--dataset_name", "princeton-nlp/SWE-bench_Lite",
            "--predictions_path", "predictions/"+"model-"+str(current_agent.id)+".json",
            "--max_workers", "20",
            "--run_id", "improve_process_one",
            "--report_dir", "reports"
            ]
        
        print("Evaluando modelo ",current_agent.id)
        result = subprocess.run(cmd, capture_output=True, text=True)
        print("Evaluacion completa")

        #logs/run_evaluation/'run_id'/'model_id'/

        print("Creando task improvements")
        print("Logs files en : ","logs/run_evaluation/improve_process_one/model-"+str(current_agent.id)+"/")
        get_task_improments(current_agent.id,"logs/run_evaluation/improve_process_one/model-"+str(current_agent.id)+"/","predictions/model-"+str(current_agent.id)+".json",swebench)
        analysis = get_analysis("task_improvement/model-"+str(current_agent.id)+"/")
        print("Task improvements listo, estos son: \n",analysis)

        agent_code = current_agent.prompt
        error_analyzer_analysis = analysis

        past_agents = [agent.prompt for agent in database.get_agents()]
        subsequent_agent_codes = "----------Past Agent----------\n".join(f"{a}" for a in past_agents)

        values = {"code":agent_code,"error_analyzer_analysis":error_analyzer_analysis,"subsequent_agent_codes":subsequent_agent_codes}

        template = Template(META_IMPROMENT_GENERATOR)
        new_agent_prompt = template.safe_substitute(values)
        
        print("Prompt para mejorar modelo: \n",new_agent_prompt)

        try:
            response = client_sync.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": new_agent_prompt}],
            temperature=0.0
            )
                        
            patch = response.choices[0].message.content.strip()

            with open("evolve_agents/model-"+str(current_agent.id+1)+".json", "w") as fichero:
                fichero.write(patch)
            
            test_agent("evolve_agents/model-"+str(current_agent.id+1)+".json")

            new_code_agent = CodeAgent(prompt=patch)
            database.add(new_code_agent)

            current_agent = new_code_agent
            print("Nuevo agente: \n",patch)
        except Exception as e:
            print(f"Error agente: {e}")
        

run_evolving_algorithm(5,10)
