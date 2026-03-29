"""
Ejemplo de uso de AgentFunctions para LangGraph
Este archivo muestra cómo tu compañero debe usar las funciones.
"""

import asyncio
from agents import AgentFunctions, parse_swebench_instance

# ============================================================================
# EJEMPLO 1: Uso Básico (sin LangGraph)
# ============================================================================

async def ejemplo_basico():
    """Muestra el uso básico de cada función"""
    
    print("="*60)
    print("EJEMPLO 1: Uso Básico de AgentFunctions")
    print("="*60)
    
    # 1. Crear instancia
    agent_funcs = AgentFunctions(model="gpt-4o-mini", temperature=0.0)
    
    # 2. Inicializar agente
    state = {}
    state = agent_funcs.initialize_agent(state)
    print(f"\n✓ {state['message']}")
    print(f"  Agent ID: {state['agent_id']}")
    
    # 3. Generar código
    state["instance_id"] = "test-001"
    state["repo"] = "django"
    state["problem_statement"] = "Fix the authentication bug in login"
    state["test_patch"] = "# Test patch content"
    
    print(f"\n⏳ Generando código...")
    state = await agent_funcs.generate_code(state)
    print(f"✓ {state['message']}")
    print(f"  Código generado: {state['model_patch'][:100]}...")
    
    # 4. Obtener info del agente
    state = agent_funcs.get_current_agent_info(state)
    print(f"\n✓ {state['message']}")
    print(f"  Total de agentes: {state['total_agents']}")
    
    # 5. Simular análisis de errores
    state["predicted_patch"] = state["model_patch"]
    state["agent_patch_log"] = "Error: Test failed..."
    state["correct_patch"] = "# Correct patch"
    
    print(f"\n⏳ Analizando errores...")
    state = agent_funcs.analyze_errors(state)
    print(f"✓ {state['message']}")
    print(f"  Mejoras encontradas: {len(state['potential_improvements'])}")
    
    # 6. Consolidar análisis
    state["analyses"] = [state["analysis"]]
    state = agent_funcs.consolidate_analysis(state)
    print(f"\n✓ {state['message']}")
    
    # 7. Evolucionar agente
    print(f"\n⏳ Evolucionando agente...")
    state = agent_funcs.evolve_agent(state)
    print(f"✓ {state['message']}")
    print(f"  Nuevo agent ID: {state['new_agent_id']}")
    
    # 8. Ver historial
    state = agent_funcs.get_agent_history(state)
    print(f"\n✓ {state['message']}")
    for agent in state['agent_history']:
        print(f"  - Agent {agent['id']}: {agent['prompt'][:50]}...")


# ============================================================================
# EJEMPLO 2: Simular Grafo de LangGraph (sin LangGraph)
# ============================================================================

async def ejemplo_grafo_simulado():
    """Simula cómo sería usar las funciones en un grafo"""
    
    print("\n" + "="*60)
    print("EJEMPLO 2: Simulación de Grafo LangGraph")
    print("="*60)
    
    agent_funcs = AgentFunctions()
    
    # Estado inicial
    state = {
        "instance_id": "django__django-12497",
        "repo": "django",
        "problem_statement": "Fix ManyToMany hint message",
        "test_patch": "# Test patch",
        "iteration": 0
    }
    
    # Nodo 1: Initialize
    print(f"\n[Nodo: initialize]")
    state = agent_funcs.initialize_agent(state)
    print(f"  {state['message']}")
    
    # Loop de 3 iteraciones
    for i in range(3):
        print(f"\n--- Iteración {i+1} ---")
        
        # Nodo 2: Generate
        print(f"[Nodo: generate]")
        state = await agent_funcs.generate_code(state)
        print(f"  {state['message']}")
        
        # Nodo 3: Analyze (simular)
        print(f"[Nodo: analyze]")
        state["predicted_patch"] = state["model_patch"]
        state["agent_patch_log"] = f"Iteration {i+1} log..."
        state["correct_patch"] = "# Correct solution"
        state = agent_funcs.analyze_errors(state)
        print(f"  {state['message']}")
        
        # Nodo 4: Consolidate
        print(f"[Nodo: consolidate]")
        state["analyses"] = [state["analysis"]]
        state = agent_funcs.consolidate_analysis(state)
        print(f"  {state['message']}")
        
        # Nodo 5: Evolve
        print(f"[Nodo: evolve]")
        state = agent_funcs.evolve_agent(state)
        print(f"  {state['message']}")
    
    # Nodo final: Get history
    print(f"\n[Nodo: get_history]")
    state = agent_funcs.get_agent_history(state)
    print(f"  {state['message']}")
    print(f"\n📊 Resumen:")
    print(f"  - Iteraciones completadas: 3")
    print(f"  - Agentes creados: {state['total_agents']}")
    print(f"  - Agente final ID: {state['current_agent_id']}")


# ============================================================================
# EJEMPLO 3: Código Mínimo para Tu Compañero
# ============================================================================

def ejemplo_codigo_minimo():
    """
    Este es el código MÍNIMO que tu compañero necesita.
    Solo debe conectar estas funciones en LangGraph.
    """
    
    print("\n" + "="*60)
    print("EJEMPLO 3: Código Mínimo para LangGraph")
    print("="*60)
    
    print("""
    # ============================================
    # CÓDIGO QUE TU COMPAÑERO DEBE USAR
    # ============================================
    
    from langgraph.graph import StateGraph, END
    from agents import AgentFunctions
    
    # 1. Crear funciones
    funcs = AgentFunctions()
    
    # 2. Crear grafo
    graph = StateGraph(dict)
    
    # 3. Añadir nodos (solo conectar, no implementar)
    graph.add_node("init", funcs.initialize_agent)
    graph.add_node("generate", funcs.generate_code)
    graph.add_node("analyze", funcs.analyze_errors)
    graph.add_node("consolidate", funcs.consolidate_analysis)
    graph.add_node("evolve", funcs.evolve_agent)
    
    # 4. Definir flujo
    graph.set_entry_point("init")
    graph.add_edge("init", "generate")
    graph.add_edge("generate", "analyze")
    graph.add_edge("analyze", "consolidate")
    graph.add_edge("consolidate", "evolve")
    graph.add_edge("evolve", END)
    
    # 5. Compilar y ejecutar
    app = graph.compile()
    result = app.invoke(initial_state)
    
    # ============================================
    # FIN - TU COMPAÑERO NO NECESITA MÁS CÓDIGO
    # ============================================
    """)


# ============================================================================
# EJEMPLO 4: Con SWE-bench Real
# ============================================================================

async def ejemplo_swebench_real():
    """Muestra cómo usar con datos reales de SWE-bench"""
    
    print("\n" + "="*60)
    print("EJEMPLO 4: Uso con SWE-bench Real")
    print("="*60)
    
    try:
        from datasets import load_dataset
        
        print("\n⏳ Cargando SWE-bench Lite...")
        swebench = load_dataset('princeton-nlp/SWE-bench_Lite', split='test')
        print(f"✓ Dataset cargado: {len(swebench)} instancias")
        
        # Obtener primera instancia
        instance = swebench[0]
        print(f"\n📝 Instancia: {instance['instance_id']}")
        
        # Parsear instancia
        parsed = parse_swebench_instance(instance)
        print(f"✓ Instancia parseada")
        
        # Usar con AgentFunctions
        agent_funcs = AgentFunctions()
        
        # Inicializar
        state = parsed
        state = agent_funcs.initialize_agent(state)
        print(f"\n{state['message']}")
        
        # Generar código
        print(f"\n⏳ Generando código para instancia real...")
        state = await agent_funcs.generate_code(state)
        print(f"✓ {state['message']}")
        print(f"  Parche: {state['model_patch'][:200]}...")
        
    except ImportError:
        print("⚠️ Dataset no disponible (necesita 'datasets' instalado)")


# ============================================================================
# Ejecutar Ejemplos
# ============================================================================

async def main():
    """Ejecuta todos los ejemplos"""
    
    print("\n" + "🚀 "*20)
    print("EJEMPLOS DE USO DE AGENTFUNCTIONS PARA LANGGRAPH")
    print("🚀 "*20)
    
    # Ejemplo 1: Básico
    await ejemplo_basico()
    
    # Ejemplo 2: Grafo simulado
    await ejemplo_grafo_simulado()
    
    # Ejemplo 3: Código mínimo
    ejemplo_codigo_minimo()
    
    # Ejemplo 4: SWE-bench real (comentado por defecto)
    # await ejemplo_swebench_real()
    
    print("\n" + "="*60)
    print("✓ Todos los ejemplos completados")
    print("="*60)
    print("\n📚 Para tu compañero:")
    print("  1. Ver LANGGRAPH_USAGE.md")
    print("  2. Usar AgentFunctions directamente")
    print("  3. Conectar funciones en el grafo")
    print("  4. ¡Listo!")


if __name__ == "__main__":
    # Ejecutar
    asyncio.run(main())

