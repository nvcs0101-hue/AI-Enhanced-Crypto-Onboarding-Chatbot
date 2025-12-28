"""Check available Gemini models"""
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.secrets')

# Configure with API key from environment
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

print("🔍 Checking available Gemini models...\n")

try:
    models = genai.list_models()
    print("✅ Available models:")
    for model in models:
        if 'generateContent' in model.supported_generation_methods:
            print(f"  - {model.name}")
except Exception as e:
    print(f"❌ Error: {e}")
