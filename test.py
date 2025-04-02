from LLM_querying.thinker_agent import loop_until_ready

# 🔍 Try a complex philosophical query
query = "What does Marxism have to say about blockchain?"

# 🔁 Let the agent plan, search, reflect, and answer
final_answer = loop_until_ready(query)

# 🧠 Output
print("\n🧠 FINAL ANSWER:\n")
print(final_answer)

