import json
import random
import os
from difflib import SequenceMatcher

try:
    from Levenshtein import distance as levenshtein_distance
    HAS_LEVENSHTEIN = True
except ImportError:
    HAS_LEVENSHTEIN = False
    print("⚠️  python-Levenshtein not installed. Using SequenceMatcher fallback.")

# Map letters to array indices
ANSWER_MAP = {"a": 0, "b": 1, "c": 2, "d": 3}

# WAEC Topic Dictionary for fuzzy matching
WAEC_TOPICS = [
    # Mathematics
    "algebra", "polynomials", "quadratic equations", "indices", "logarithms",
    "surds", "sequences", "series", "binomial theorem", "matrices", "determinants",
    "geometry", "trigonometry", "vectors", "coordinate geometry", "calculus",
    "differentiation", "integration", "statistics", "probability",
    # Physics
    "mechanics", "motion", "forces", "energy", "work", "power", "momentum",
    "waves", "optics", "light", "electricity", "magnetism", "circuits",
    "thermodynamics", "heat", "temperature", "specific heat capacity",
    # Chemistry
    "atomic structure", "periodic table", "chemical bonding", "acids", "bases",
    "salts", "oxidation", "reduction", "electrolysis", "organic chemistry",
    "hydrocarbons", "alkanes", "alkenes", "alkynes", "equilibrium", "rates",
    # English
    "adjectives", "adverbs", "nouns", "pronouns", "verbs", "tenses",
    "comprehension", "essay writing", "letter writing", "grammar", "vocabulary",
    # Biology
    "cells", "tissues", "organs", "genetics", "evolution", "ecology",
    "photosynthesis", "respiration", "digestion", "circulation"
]

def fuzzy_match_topic(query, threshold=0.7):
    """
    Find best matching topic using fuzzy string matching.
    Returns (best_match, confidence) or (None, 0) if no good match.
    """
    if not query or len(query) < 3:
        return None, 0
    
    query_lower = query.lower().strip()
    best_match = None
    best_score = 0
    
    for topic in WAEC_TOPICS:
        if HAS_LEVENSHTEIN:
            # Calculate normalized Levenshtein distance
            dist = levenshtein_distance(query_lower, topic)
            max_len = max(len(query_lower), len(topic))
            score = 1 - (dist / max_len) if max_len > 0 else 0
        else:
            # Fallback to SequenceMatcher
            score = SequenceMatcher(None, query_lower, topic).ratio()
        
        # Check if query is substring of topic or vice versa
        if query_lower in topic or topic in query_lower:
            score = max(score, 0.9)  # Boost substring matches
        
        if score > best_score:
            best_score = score
            best_match = topic
    
    if best_score >= threshold:
        return best_match, best_score
    return None, 0

def format_questions(raw_questions_list):
    formatted = []
    for q in raw_questions_list:
        if "options" not in q or "question" not in q:
            continue
            
        # SMART ANSWER MATCHING
        idx = 0
        raw_ans = str(q.get("answer", "A")).strip()
        
        # Case 1: Answer is an index integer (0, 1, 2)
        if isinstance(q.get("answer"), int):
            idx = q["answer"]
            
        # Case 2: Answer is a Letter (A, B, C)
        elif raw_ans.lower() in ANSWER_MAP:
            idx = ANSWER_MAP[raw_ans.lower()]
            
        # Case 3: Answer is the full text (e.g. "12cm")
        # We try to find the text inside the options list
        else:
            # Clean up LaTeX/Symbols for comparison
            clean_raw = raw_ans.lower().replace('$','').replace(' ','')
            found = False
            for i, opt in enumerate(q["options"]):
                clean_opt = str(opt).lower().replace('$','').replace(' ','')
                # Check for exact match or substring match
                if clean_raw == clean_opt or clean_raw in clean_opt:
                    idx = i
                    found = True
                    break
            if not found:
                idx = 0 # Default to A if we can't match (prevents crash)

        formatted.append({
            "id": q.get("id", random.randint(1000, 9999)),
            "question": q["question"],
            "options": q["options"],
            "correct_index": idx,
            "explanation": q.get("explanation", "Check the marking scheme.")
        })
    return formatted


def get_static_quiz(subject_filter, topic_filter=None, count=3):
    """
    Reads from local JSON file and returns a formatted quiz object.
    Improved topic search with partial matching and case-insensitive comparison.
    """
    try:
        base_dir = os.path.dirname(os.path.dirname(__file__))
        file_path = os.path.join(base_dir, 'data', 'waec_questions.json')
        
        with open(file_path, 'r', encoding='utf-8') as f:
            all_questions = json.load(f)
            
        candidates = []
        
        # 1. Subject Filter - handle variations
        if subject_filter and subject_filter.lower() != "general":
            subject_lower = subject_filter.lower()
            # Handle common variations (e.g., "English" matches "English Language")
            candidates = [q for q in all_questions 
                         if subject_lower in q['subject'].lower() 
                         or q['subject'].lower() in subject_lower]
            
            # If no match, try exact match
            if not candidates:
                candidates = [q for q in all_questions 
                             if q['subject'].lower() == subject_lower]
        else:
            candidates = all_questions

        # 2. Topic Filter - enhanced with FUZZY matching
        if topic_filter and topic_filter.lower() not in ["general", "none", ""]:
            topic_matches = []
            topic_lower = topic_filter.lower()
            
            # Try fuzzy matching first
            corrected_topic, confidence = fuzzy_match_topic(topic_filter)
            if corrected_topic and confidence > 0.7:
                print(f"🔍 Fuzzy match: '{topic_filter}' → '{corrected_topic}' (confidence: {confidence:.2f})")
                topic_lower = corrected_topic
            
            for q in candidates:
                q_topic = q.get('topic', '').lower()
                q_text = q.get('question', '').lower()
                
                # Priority 1: Topic field contains the search term
                if topic_lower in q_topic:
                    topic_matches.append(q)
                # Priority 2: Question text contains the search term
                elif topic_lower in q_text:
                    topic_matches.append(q)
                # Priority 3: Search term is in topic field (reverse)
                elif q_topic and any(word in topic_lower for word in q_topic.split() if len(word) > 3):
                    topic_matches.append(q)
            
            if topic_matches:
                candidates = topic_matches
                print(f"Found {len(topic_matches)} questions matching topic '{topic_filter}'")
            else:
                print(f"No specific topic match for '{topic_filter}', using subject filter only")

        # 3. Selection
        if not candidates:
            print(f"No matches found for subject='{subject_filter}' topic='{topic_filter}', using all questions")
            candidates = all_questions # Fallback to all if nothing found

        sample_size = min(len(candidates), count)
        selected = random.sample(candidates, sample_size)
        
        # 4. Use the shared formatter
        final_data = format_questions(selected)
            
        return json.dumps({"questions": final_data})

    except Exception as e:
        print(f"Error loading static quiz: {e}")
        return json.dumps({"questions": []})
