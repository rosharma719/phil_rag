from LLM_querying.thought_planner import decompose_question
from LLM_querying.tools import *
from LLM_querying.rag_engine import build_rag_prompt
from LLM_querying.mistral_api import call_mistral_chat

def is_context_sufficient(question, context_chunks):
    joined = "\n\n".join(context_chunks)
    prompt = f"""
<context>
{joined}
</context>

Given the context above, do you have enough information to answer the following question?

Question: {question}

Respond with YES or NO only.
"""
    response = call_mistral_chat(prompt).strip().upper()
    return response.startswith("YES")

def revise_search_plan(question, context_chunks):
    context = "\n\n".join(context_chunks)
    prompt = f"""
<context>
{context}
</context>

You are a philosophical RAG planner.

The user question is: {question}
You do not yet have enough information. Suggest a revised search direction or query.
Respond with a short updated natural language query.
"""
    return call_mistral_chat(prompt).strip()

def generate_final_answer(question, context_chunks):
    print("\n🧠 Final context used:\n")
    for chunk in context_chunks:
        print(f"- {chunk[:200]}...\n")  # print preview of each chunk
    prompt = build_rag_prompt(context_chunks, question)
    return call_mistral_chat(prompt).strip()

def loop_until_ready(question, max_loops=3):
    context_chunks = []
    current_query = question
    loops = 0

    while loops < max_loops:
        print(f"\n🔁 Loop {loops+1}: Planning for — {current_query}")
        plan = decompose_question(current_query)

        new_chunks = []

        for step in plan.get("steps", []):
            action = step["action"]
            target = step["target"]

            if action == "search_beliefs":
                for bid in search_beliefs(target):
                    snippet = get_belief_content(bid)
                    if snippet: new_chunks.append(snippet)

            elif action == "search_concepts":
                if isinstance(target, list):
                    for t in target:
                        for cid in search_concepts(t):
                            snippet = get_concept_content(cid)
                            if snippet: new_chunks.append(snippet)
                else:
                    for cid in search_concepts(target):
                        snippet = get_concept_content(cid)
                        if snippet: new_chunks.append(snippet)

            elif action == "expand_concepts":
                if isinstance(target, list):
                    for t in target:
                        try:
                            result = expand_concepts(t)
                            if result:
                                new_chunks.append(f"Expanded: {result}")
                        except Exception as e:
                            print(f"⚠️ expand_concepts failed for {t}: {e}")
                else:
                    try:
                        result = expand_concepts(target)
                        if result:
                            new_chunks.append(f"Expanded: {result}")
                    except Exception as e:
                        print(f"⚠️ expand_concepts failed for {target}: {e}")

            elif action == "expand_beliefs":
                if isinstance(target, list):
                    for t in target:
                        try:
                            result = expand_beliefs(t)
                            if result:
                                new_chunks.append(f"Expanded: {result}")
                        except Exception as e:
                            print(f"⚠️ expand_beliefs failed for {t}: {e}")
                else:
                    try:
                        result = expand_beliefs(target)
                        if result:
                            new_chunks.append(f"Expanded: {result}")
                    except Exception as e:
                        print(f"⚠️ expand_beliefs failed for {target}: {e}")

            elif action == "get_concept_path":
                if isinstance(target, list) and len(target) == 2:
                    try:
                        path = get_concept_path(target[0], target[1])
                        if path:
                            new_chunks.append(f"Path: {path}")
                    except Exception as e:
                        print(f"⚠️ get_concept_path failed for {target}: {e}")

        context_chunks.extend(new_chunks)

        if is_context_sufficient(question, context_chunks):
            print("\n✅ Context sufficient. Generating final answer...")
            return generate_final_answer(question, context_chunks)

        print("\n⚠️ Context insufficient. Revising plan...")
        current_query = revise_search_plan(question, context_chunks)
        loops += 1

    print("\n🚨 Max loops reached. Generating best-effort answer...")
    return generate_final_answer(question, context_chunks)