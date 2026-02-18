"""
Test script for translation layer
"""

from src.translator import translate_to_english, translate_from_english

print("Testing Translation Layer...")
print("=" * 80)

# Test 1: Hindi to English
hindi_query = "NPS क्या है?"
print(f"\n1. Hindi → English")
print(f"   Input:  {hindi_query}")
english_result = translate_to_english(hindi_query, "hi")
print(f"   Output: {english_result}")

# Test 2: English to Hindi
english_answer = "The National Pension System (NPS) is a voluntary retirement savings scheme."
print(f"\n2. English → Hindi")
print(f"   Input:  {english_answer}")
hindi_result = translate_from_english(english_answer, "hi")
print(f"   Output: {hindi_result}")

# Test 3: Assamese to English
assamese_query = "NPS কি?"
print(f"\n3. Assamese → English")
print(f"   Input:  {assamese_query}")
english_result_as = translate_to_english(assamese_query, "as")
print(f"   Output: {english_result_as}")

# Test 4: English to Assamese
print(f"\n4. English → Assamese")
print(f"   Input:  {english_answer}")
assamese_result = translate_from_english(english_answer, "as")
print(f"   Output: {assamese_result}")

# Test 5: English to English (should return as-is)
print(f"\n5. English → English (no translation)")
print(f"   Input:  What is NPS?")
english_passthrough = translate_to_english("What is NPS?", "en")
print(f"   Output: {english_passthrough}")

print("\n" + "=" * 80)
print("✅ Translation tests complete!")
