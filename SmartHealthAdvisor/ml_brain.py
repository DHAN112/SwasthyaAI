import json
import os
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# 1. ROBUST PATH SETUP
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, 'ayurveda_data.json')

def load_data():
    """
    Loads the JSON data safely with UTF-8 encoding for multilingual support.
    """
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ ERROR: Could not find file at {DATA_FILE}")
        return []
    except json.JSONDecodeError:
        print(f"❌ ERROR: ayurveda_data.json has invalid JSON format")
        return []

# 2. LOAD & PREPARE DATA
data = load_data()

# Separate answers for retrieval
answers = [item['answer'] for item in data] if data else []

# 3. BUILD MULTILINGUAL TRAINING CORPUS
training_corpus = []
if data:
    for item in data:
        # STRATEGY: 'Weighted Context'
        # We combine Question + Answer. 
        # CRITICAL: We repeat the 'question' 3 times. 
        # Why? Because your questions now contain Language Tags like "(Answer in Hindi)".
        # Repeating them increases the TF-IDF weight of the language tag, ensuring 
        # the bot strictly respects the selected language.
        
        combined_text = f"{item['question']} {item['question']} {item['question']} {item['answer']}"
        training_corpus.append(combined_text)

# 4. TRAIN INTELLIGENT VECTORIZER
if training_corpus:
    # IMPROVEMENTS FOR MULTILINGUAL SUPPORT:
    # 1. ngram_range=(1, 3): Captures phrases like "Answer in Hindi" or "immune system".
    # 2. token_pattern=r'(?u)\b\w+\b': Ensures Hindi/Marathi/Sanskrit characters are treated as valid words.
    # 3. stop_words=None: We keep all words because "in" or "ka/ki" might be relevant for language detection.
    
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 3), 
        token_pattern=r'(?u)\b\w+\b'
    ).fit(training_corpus)
    
    corpus_vectors = vectorizer.transform(training_corpus)
else:
    vectorizer = None
    corpus_vectors = None

def get_response(user_input):
    """
    Takes user input (potentially with language tags), finds the best match,
    and returns the corresponding HTML answer.
    """
    if not vectorizer:
        return "System Error: Brain not loaded. Please check ayurveda_data.json."

    # 1. Clean Input
    # We do NOT use .lower() here aggressively because some scripts might be case-sensitive 
    # or the vectorizer handles it better natively with UTF-8.
    cleaned_input = user_input.strip()

    # 2. Vectorize User Input
    user_vec = vectorizer.transform([cleaned_input])
    
    # 3. Calculate Cosine Similarity
    similarity_scores = cosine_similarity(user_vec, corpus_vectors)
    
    # 4. Find Best Match
    best_match_index = np.argmax(similarity_scores)
    confidence_score = similarity_scores[0][best_match_index]
    
    # --- DEBUGGING LOGS (Visible in Terminal) ---
    # This helps you verify if it matched the Hindi/Marathi entry correctly
    print(f"\n🔍 Query: '{cleaned_input}'")
    print(f"✅ Best Match Key: '{data[best_match_index]['question']}'")
    print(f"📊 Confidence: {confidence_score:.2f}")
    # --------------------------------------------

    # 5. Smart Thresholding
    # Lower threshold slightly (0.1) to allow flexible matching in vernacular languages
    if confidence_score > 0.1:
        return answers[best_match_index]
    else:
        # Fallback for low confidence
        return (
            "I am not entirely sure about that yet. 🧘‍♂️<br>"
            "Please check if you selected the correct language or try asking about specific topics like:<br>"
            "<b>'Tulsi'</b>, <b>'Acidity'</b>, <b>'Hair Fall'</b>, or <b>'Yoga'</b>."
        )