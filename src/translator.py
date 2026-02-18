"""
Translation utilities for NPS Bondhu
Uses Google Translate via deep-translator for translating between English, Hindi, and Assamese
"""

from deep_translator import GoogleTranslator
from functools import lru_cache
import hashlib

# Language code mapping
LANG_CODES = {
    "en": "en",
    "hi": "hi",
    "as": "as"
}

# Translation cache to avoid redundant API calls
_translation_cache = {}

def get_cache_key(text, source_lang, target_lang):
    """Generate cache key for translation"""
    combined = f"{text}_{source_lang}_{target_lang}"
    return hashlib.md5(combined.encode()).hexdigest()

def translate_to_english(text, source_lang_code):
    """
    Translate text from source language to English.
    
    Args:
        text: Text to translate
        source_lang_code: Source language code ('en', 'hi', 'as')
    
    Returns:
        Translated text in English
    """
    # If already English, return as-is
    if source_lang_code == "en":
        return text
    
    # Check cache
    cache_key = get_cache_key(text, source_lang_code, "en")
    if cache_key in _translation_cache:
        return _translation_cache[cache_key]
    
    try:
        # Translate to English
        translator = GoogleTranslator(source=source_lang_code, target="en")
        translated_text = translator.translate(text)
        
        # Cache the result
        _translation_cache[cache_key] = translated_text
        
        return translated_text
    except Exception as e:
        print(f"Translation error (to English): {e}")
        # Fallback: return original text
        return text

def translate_from_english(text, target_lang_code):
    """
    Translate text from English to target language.
    
    Args:
        text: Text to translate (in English)
        target_lang_code: Target language code ('en', 'hi', 'as')
    
    Returns:
        Translated text in target language
    """
    # If target is English, return as-is
    if target_lang_code == "en":
        return text
    
    # Check cache
    cache_key = get_cache_key(text, "en", target_lang_code)
    if cache_key in _translation_cache:
        return _translation_cache[cache_key]
    
    try:
        # Translate from English
        translator = GoogleTranslator(source="en", target=target_lang_code)
        translated_text = translator.translate(text)
        
        # Cache the result
        _translation_cache[cache_key] = translated_text
        
        return translated_text
    except Exception as e:
        print(f"Translation error (from English): {e}")
        # Fallback: return original text
        return text

def translate_query_and_response(query, response, user_lang_code):
    """
    Complete translation flow:
    1. Translate query to English (if needed)
    2. Process with RAG (handled externally)
    3. Translate response back to user language (if needed)
    
    Args:
        query: User's query in their selected language
        response: AI response in English
        user_lang_code: User's selected language code
    
    Returns:
        tuple: (translated_query_to_english, translated_response_to_user_lang)
    """
    # Translate query to English for RAG processing
    query_in_english = translate_to_english(query, user_lang_code)
    
    # Translate response back to user's language
    response_in_user_lang = translate_from_english(response, user_lang_code)
    
    return query_in_english, response_in_user_lang

def clear_translation_cache():
    """Clear the translation cache"""
    global _translation_cache
    _translation_cache = {}
