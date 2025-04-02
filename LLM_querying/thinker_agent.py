from LLM_querying.thought_planner import decompose_question
from LLM_querying.tools import *
from LLM_querying.rag_engine import build_rag_prompt
from LLM_querying.mistral_api import call_mistral_chat


def is_context_sufficient(question, context_chunks):
    """
    Ask Mistral whether the current context is sufficient to answer the question.
    Returns True or False.
    """
    joined = "\n\n".join(context_chunks[-5:])  # recent context
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
    """
    Ask Mistral how to revise the search plan given current context.
    """
    context = "\n\n".join(context_chunks[-5:])
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
    prompt = build_rag_prompt(context_chunks, question)
    return call_mistral_chat(prompt).strip()


def loop_until_ready(question, max_loops=3):
    context_chunks = []
    current_query = question
    loops = 0

    while loops < max_loops:
        print(f"\n🔁 Loop {loops+1}: Planning for — {current_query}")
        plan = decompose_question(current_query)

        for step in plan.get("steps", []):
            action = step["action"]
            target = step["target"]

            if action == "search_beliefs":
                for bid in search_beliefs(target):
                    snippet = get_belief_content(bid)
                    if snippet: context_chunks.append(snippet)

            elif action == "search_concepts":
                for cid in search_concepts(target):
                    context_chunks.append(f"Concept result: {cid}")

            elif action == "expand_concepts":
                if isinstance(target, list):
                    for t in target:
                        context_chunks.append(f"Expanded: {expand_concepts(t)}")
                else:
                    context_chunks.append(f"Expanded: {expand_concepts(target)}")

            elif action == "expand_beliefs":
                if isinstance(target, list):
                    for t in target:
                        context_chunks.append(f"Expanded: {expand_beliefs(t)}")
                else:
                    context_chunks.append(f"Expanded: {expand_beliefs(target)}")

            elif action == "get_concept_path":
                if isinstance(target, list) and len(target) == 2:
                    path = get_concept_path(target[0], target[1])
                    context_chunks.append(f"Path: {path}")

        if is_context_sufficient(question, context_chunks):
            print("\n✅ Context sufficient. Generating final answer...")
            return generate_final_answer(question, context_chunks)

        print("\n⚠️ Context insufficient. Revising plan...")
        current_query = revise_search_plan(question, context_chunks)
        loops += 1

    print("\n🚨 Max loops reached. Generating best-effort answer...")
    return generate_final_answer(question, context_chunks)
