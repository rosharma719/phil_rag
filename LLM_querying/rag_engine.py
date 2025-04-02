def build_rag_prompt(context_chunks, question):
    """
    Constructs the final prompt with context and question for Mistral.
    """
    context = "\n\n".join(context_chunks)
    prompt = f"""
<context>
{context}
</context>

Using the context above, answer the following philosophical question as precisely and insightfully as possible.

Question: {question}
Answer:
"""
    return prompt.strip()
