# Objective
Fix agent hallucinations, improve strict adherence to rules, and strengthen the intent matching for human handoffs.
 
# Context
The `llama-3.1-8b-instant` model struggles with complex instructions. Patients expressing frustration or asking for pricing get stuck in a loop instead of being transferred to a human. The agent also hallucinated non-existent rules about availability.
 
# Modifications
1.  **Upgrade Model**: Switch `agent.py` to use `llama-3.3-70b-versatile` for much better reasoning.
2.  **Refine Prompt**: Reorder rules in `agent.py` so human handoffs and knowledge base searches take priority. Add explicit instructions to never invent availabilities.
3.  **Enhance Webhook Intents**: Add `INTENT_PATTERNS` in `webhooks.py` to catch frustration phrases ("chata", "ruim") and "falar_atendente" intents early.
4.  **Strengthen Knowledge Base Fallback**: In `tools.py`, if `search_knowledge_base` yields no results for queries containing "valor" or "preço", return a system hint to transfer to a human.
