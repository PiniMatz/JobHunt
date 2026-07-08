import re

def pre_screen_job(title: str, description: str, settings: dict) -> tuple[bool, str]:
    """
    Determine if a job listing is relevant for Product Manager positions
    and matches user criteria BEFORE calling the LLM matching engine.
    
    Returns:
        (is_relevant: bool, reason: str)
    """
    title_lower = title.lower()
    desc_lower = description.lower()
    
    must_haves = settings.get("must_have_keywords", ["Product Manager", "Product Owner", "PM"])
    exclusions = settings.get("exclusion_keywords", ["Junior", "Intern", "Student"])
    
    # 1. Check must-have keywords
    # At least one must-have keyword must appear in the title or the description.
    # To reduce false positives, we check for word boundaries or exact substrings.
    has_must_have = False
    for kw in must_haves:
        kw_clean = kw.strip().lower()
        if not kw_clean:
            continue
        # Use regex search for word boundaries where possible (e.g. for "PM")
        # to avoid matching "Development" as containing "PM"
        if len(kw_clean) <= 2:
            pattern = re.compile(rf"\b{re.escape(kw_clean)}\b")
            if pattern.search(title_lower) or pattern.search(desc_lower):
                has_must_have = True
                break
        else:
            if kw_clean in title_lower or kw_clean in desc_lower:
                has_must_have = True
                break
                
    if not has_must_have:
        return False, f"Job description does not contain any must-have keywords: {must_haves}"
        
    # 2. Check exclusion keywords
    # None of these keywords must appear in the job TITLE (exclusion is typically based on title seniority/type).
    for kw in exclusions:
        kw_clean = kw.strip().lower()
        if not kw_clean:
            continue
        pattern = re.compile(rf"\b{re.escape(kw_clean)}\b")
        if pattern.search(title_lower):
            return False, f"Excluded due to keyword '{kw}' present in job title."
            
    return True, "Passed pre-screening."
