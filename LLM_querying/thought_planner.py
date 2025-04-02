from LLM_querying.mistral_api import call_mistral_chat
import json
import re

def decompose_question(question: str) -> dict:
    """
    Uses Mistral to break down a philosophical question into a structured reasoning/search plan.
    Returns a dictionary with a list of {action, target} steps.
    """
    prompt = f"""
You are a philosophical research planner.

Your task is to break down the user's question into concrete information-gathering steps
using available tools. For each step, return:
  - an `action`: one of [search_beliefs, search_concepts, expand_concepts, expand_beliefs, get_concept_path]
  - a `target`: what to search or relate (e.g., a concept, belief fragment, or pair of concepts)

Only return a JSON object with this format:
{{
  "steps": [
    {{"action": "search_beliefs", "target": "Kant on moral autonomy"}},
    {{"action": "search_beliefs", "target": "Nietzsche critique of reason"}},
    {{"action": "get_concept_path", "target": ["autonomy", "will to power"]}}
  ]
}}

User Question: {question}
"""

    response = call_mistral_chat(prompt)
    match = re.search(r"\{.*\}", response, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            return {"steps": []}
    return {"steps": []}

