def get_client_ip(request):
    """Get client IP address from request"""

    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def clean_search_query(query):
    """Clean and normalize search query"""

    import re
    query = re.sub(r'[^\w\s\-\.]', '', query)
    query = ' '.join(query.split())
    query = query.lower()
    return query.strip()


def highlight_search_terms(text, query, max_length=200):
    """Highlight search terms in text"""

    import re
    if not query or not text:
        return text[:max_length] + "..." if len(text) > max_length else text
    pattern = re.compile(re.escape(query), re.IGNORECASE)
    highlighted = pattern.sub(f'<mark>{query}</mark>', text)
    if len(highlighted) > max_length:
        highlighted = highlighted[:max_length] + "..."
    return highlighted


def extract_search_keywords(query):
    """Extract keywords from search query"""

    import re
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have',
        'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'
    }
    words = re.findall(r'\b\w+\b', query.lower())
    keywords = [word for word in words if word not in stop_words and len(word) > 2]
    return keywords


def calculate_search_relevance(text, query):
    """Calculate relevance score for search results"""

    if not query or not text:
        return 0
    text_lower = text.lower()
    query_lower = query.lower()
    score = 0
    if query_lower in text_lower:
        score += 10
    keywords = extract_search_keywords(query)
    for keyword in keywords:
        if keyword in text_lower:
            score += 2
    if text_lower.startswith(query_lower):
        score += 5
    return score