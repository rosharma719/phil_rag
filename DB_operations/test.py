from neon_operations import (
    get_mistral_output,
    get_title,
    get_section,
    get_content,
    get_beliefs_in_document,
    get_concepts_in_document,
    get_associated_thinkers,
    get_associated_eras
)

# Sample belief ID for testing
test_belief_id = "28218_belief_26626928"  # Replace with an actual belief ID

# **Test: Mistral JSON**
print(f"Mistral Output: {get_mistral_output(28218)}")

# **Test: Document Metadata**
print(f"Title: {get_title(28218)}")
print(f"Section: {get_section(28218)}")
print(f"Content: {get_content(28218)}")

# **Test: Get Beliefs in Document**
print(f"Beliefs in Document: {get_beliefs_in_document(test_belief_id)}")

# **Test: Get Concepts in Document**
print(f"Concepts in Document: {get_concepts_in_document(test_belief_id)}")

# **Test: Get Associated Thinkers**
print(f"Associated Thinkers: {get_associated_thinkers(test_belief_id)}")

# **Test: Get Associated Eras**
print(f"Associated Eras: {get_associated_eras(test_belief_id)}")
