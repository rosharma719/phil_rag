import json
import re
import logging
from LLM_querying.mistral_api import call_mistral_chat

logger = logging.getLogger(__name__)

def decompose_question(question: str) -> dict:
    """
    Uses Mistral to break down a philosophical question into a structured reasoning/search plan.
    Returns a dictionary with a list of {action, target} steps.
    Also logs detailed trace information.
    """
    prompt = f"""
You are a philosophical research planner.

Your task is to break down the user's question into concrete information-gathering steps
using available tools. For each step, return:
  - an `action`: one of [search_beliefs, search_concepts, expand_concepts, expand_beliefs, get_concept_path]
  - a `target`: what to search or relate (e.g., a concept, belief fragment, or pair of concepts)

  If you're searching a belief, structure it like an opinionated statement. 
  And if you're searching a concept, structure it like a concept (ie. a word or short phrase).

You will receive no further instruction, so just do your best in detail.

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

    logger.info("🔁 Decomposing question — %s", question)

    try:
        response = call_mistral_chat(prompt)
        logger.info("🧠 Mistral raw output:\n%s", response)

        match = re.search(r"\{.*\}", response, re.DOTALL)
        if match:
            try:
                steps = json.loads(match.group())
                logger.info("🧭 Decomposed Plan:\n%s", json.dumps(steps, indent=2))
                return steps
            except json.JSONDecodeError as e:
                logger.warning("❌ JSON parsing error: %s", str(e))
                logger.debug("Raw matched block:\n%s", match.group())
                return {"steps": []}
        else:
            logger.warning("⚠️ No JSON block found in response.")
            return {"steps": []}
    except Exception as e:
        logger.error("❌ Error during decompose_question: %s", str(e))
        return {"steps": []}
