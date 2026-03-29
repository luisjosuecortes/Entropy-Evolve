from datasets import load_dataset, disable_progress_bar
import asyncio
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
import os
import json
import subprocess
from dotenv import load_dotenv

from agents import CodeAgent
from agents.db import DataBase
from agents.promts import BASE_AGENT, TASK_IMPROVEMENT_REASONER, META_IMPROMENT_GENERATOR

# Cargar variables de entorno desde .env
load_dotenv()

disable_progress_bar()

# Chain reutilizable (LCEL best practice)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
chain = llm | StrOutputParser()

async def get_swebench_code(agent: CodeAgent, instance_id: str, repo: str, problem_statement: str, test_patch: str, semaphore) -> dict:
    async with semaphore:
        try:
            # Usar el PromptTemplate del agente directamente si existe, sino crear uno
            prompt_template = agent.prompt_template if agent.prompt_template else PromptTemplate.from_template(agent.prompt)
            code = await (prompt_template | chain).ainvoke({"repo": repo, "problem_statement": problem_statement, "test_patch": test_patch})
            return {"instance_id": instance_id, "model_patch": code, "model_name_or_path": f"model-{agent.id}"}
        except Exception as e:
            return {"instance_id": instance_id, "error": str(e)}

def get_log(log_file):
    with open(log_file, "r") as f:
        lineas = f.readlines()
    return "\n".join(lineas[:50])

def get_task_improments(model_id, logs_file, predictions_file, swebench):
    os.makedirs(f"task_improvement/model-{model_id}/", exist_ok=True)
    print(f"Carpeta task_improvement/model-{model_id}/ creada")
    with open(predictions_file, 'r') as file:
        predictions = json.load(file)
    
    for instance_id in os.listdir(logs_file):
        log_file = f"{logs_file}/{instance_id}/run_instance.log"
        filtered = swebench.filter(lambda ex: ex["instance_id"] == instance_id)
        
        data = filtered[0]
        predicted = next((x for x in predictions if x["instance_id"] == instance_id), None)
        
        try:
            # Usar LCEL con PromptTemplate directamente
            result = (TASK_IMPROVEMENT_REASONER | chain).invoke({
                "problem_statement": data['problem_statement'],
                "test_patch": data['test_patch'],
                "predicted_patch": predicted["model_patch"],
                "agent_patch_log": get_log(log_file),
                "patch": data['patch']
            })
            with open(f"task_improvement/model-{model_id}/{instance_id}.json", "w") as f:
                f.write(result.strip())
        except Exception as e:
            print(f"Error en {instance_id}: {e}")
            continue

def get_analysis(directory: str):
    analyses = []
    for task in os.listdir(directory):
        with open(f"{directory}/{task}", 'r') as f:
            analyses.extend(json.load(f)["potential_improvements"])
    return "\n".join(f"- {a}" for a in analyses)

def test_agent(path):
    with open(path, "r") as f:
        agent_json = json.load(f)
        PromptTemplate.from_template(agent_json["new_agent"]).format(repo="", problem_statement="", test_patch="")

def run_evolving_algorithm(num_iters: int, n_samples: int):
    
    def get_responses(data, current_agent):
        semaphore = asyncio.Semaphore(3)
        async def run_all(data, current_agent):
            tasks = [get_swebench_code(current_agent, row['instance_id'], row['repo'], row['problem_statement'], row['test_patch'], semaphore) for row in data]
            return await asyncio.gather(*tasks)
        return asyncio.run(run_all(data, current_agent))
         
    swebench = load_dataset('princeton-nlp/SWE-bench_Lite', split='test')
    database = DataBase()

    initial_code_agent = CodeAgent(prompt=BASE_AGENT)
    current_agent = initial_code_agent
    best_agent = initial_code_agent
    database.add(current_agent)

    for iter in range(num_iters):
        data = swebench.shuffle().select(range(n_samples))

        print(f"Creando respuestas de iteracion {iter}")
        results = get_responses(data, current_agent)

        pred_file = f"predictions/model-{current_agent.id}.json"
        with open(pred_file, "w") as f:
            json.dump(results, f)
        print(f"Respuestas guardadas en: {pred_file}")

        print(f"Evaluando modelo {current_agent.id}")
        subprocess.run([
            "python", "-m", "swebench.harness.run_evaluation",
            "--dataset_name", "princeton-nlp/SWE-bench_Lite",
            "--predictions_path", pred_file,
            "--max_workers", "20",
            "--run_id", "improve_process_one",
            "--report_dir", "reports"
        ], capture_output=True, text=True)
        print("Evaluacion completa")

        logs_dir = f"logs/run_evaluation/improve_process_one/model-{current_agent.id}/"
        print(f"Creando task improvements desde {logs_dir}")
        get_task_improments(current_agent.id, logs_dir, pred_file, swebench)
        analysis = get_analysis(f"task_improvement/model-{current_agent.id}/")
        print(f"Task improvements listo:\n{analysis}")

        # Obtener prompts de agentes pasados (solo el template string, no el objeto)
        past_prompts = [a.prompt if isinstance(a.prompt, str) else a.prompt.template for a in database.get_agents()]
        
        try:
            # Usar LCEL para meta-mejora
            current_prompt = current_agent.prompt if isinstance(current_agent.prompt, str) else current_agent.prompt.template
            new_prompt = (META_IMPROMENT_GENERATOR | chain).invoke({
                "code": current_prompt,
                "error_analyzer_analysis": analysis,
                "subsequent_agent_codes": "----------Past Agent----------\n".join(past_prompts)
            }).strip()
            
            agent_file = f"evolve_agents/model-{current_agent.id + 1}.json"
            with open(agent_file, "w") as f:
                f.write(new_prompt)
            
            test_agent(agent_file)
            new_code_agent = CodeAgent(prompt=new_prompt)
            database.add(new_code_agent)
            current_agent = new_code_agent
            print(f"Nuevo agente creado:\n{new_prompt}")
        except Exception as e:
            print(f"Error agente: {e}")

run_evolving_algorithm(5, 10)

