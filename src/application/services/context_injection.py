import logging
from src.infrastructure.vector_store import search_store

logger = logging.getLogger(__name__)

def truncate_context_to_limit(context_string: str, max_chars: int = 1500) -> str:
    """
    Limits the context to a certain number of characters as a proxy for tokens.
    """
    if len(context_string) <= max_chars:
        return context_string
    logger.warning("Context exceeded limit, truncating to %d chars.", max_chars)
    return context_string[:max_chars] + "\n...[Context truncated due to length limits]"

def get_dynamic_context_for_query(query: str, k: int = 2, max_chars: int = 1500) -> str:
    """
    Fetches relevant documents from the knowledge base for a specific query
    and formats them as a context string.
    """
    if not query or len(query.strip()) < 3:
        return ""
    
    try:
        results = search_store(query, k=k)
        if not results:
            return ""
        
        context_parts = []
        for res in results:
            context_parts.append(f"- {res.page_content}")
            
        full_context = "\n".join(context_parts)
        return truncate_context_to_limit(full_context, max_chars)
    except Exception as e:
        logger.error("Error fetching dynamic context: %s", e)
        return ""

def inject_context_into_prompt(messages: list) -> str:
    """
    Extracts the latest user message to retrieve context.
    """
    if not messages:
        return ""
        
    # Get last user message
    last_user_msg = next((m for m in reversed(messages) if getattr(m, 'role', '') == 'user'), None)
    
    if not last_user_msg:
        return ""
        
    content = getattr(last_user_msg, 'content', '')
    if isinstance(content, str):
        dynamic_context = get_dynamic_context_for_query(content)
        if dynamic_context:
            return f"\n\n--- INJECTED DYNAMIC CONTEXT (PRIORITY OVER GENERAL KNOWLEDGE) ---\n{dynamic_context}\n--- END INJECTED CONTEXT ---\n"
    
    return ""
