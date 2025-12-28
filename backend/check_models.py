"""Check available Gemini models"""
import os
import google.generativeai as genai

genai.configure(api_key='REDACTED_GOOGLE_API_KEY')

print("🔍 Checking available Gemini models...\n")

try:
    models = genai.list_models()
    print("✅ Available models:")
    for model in models:
        if 'generateContent' in model.supported_generation_methods:
            print(f"  - {model.name}")
except Exception as e:
    print(f"❌ Error: {e}")
