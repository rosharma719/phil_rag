from LLM_querying.thinker_agent import loop_until_ready

# 🔍 Try a complex philosophical query
query = "What is the relationship between blockchain, society, and quantum computing? Use much detail"

# 🔁 Let the agent plan, search, reflect, and answer
final_answer = loop_until_ready(query)

# 🧠 Output
print("\n🧠 FINAL ANSWER:\n")
print(final_answer)

