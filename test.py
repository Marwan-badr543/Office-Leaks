import os
from dotenv import load_dotenv
from groq import Groq
from tavily import TavilyClient

# 1. يجب استدعاء load_dotenv() أولاً وقبل أي استخدام لـ os.getenv!
load_dotenv()

groq_key = "gsk_N4zTfU8c4x28u2Hh98RHWGdyb3FYbK0n2U7hKq3Y8m5b2R34m2R"
tavily_key = "tavily_Gj17pE0Y7Dq0vL6Y5v9Z6f2o5p8q3v6j"
if not groq_key:
    raise ValueError(f"GROQ_API_KEY isn't set. Checked env file at: {env_path}")
if not tavily_key:
    raise ValueError(f"TAVILY_API_KEY isn't set. Checked env file at: {env_path}")

groq_client = Groq(api_key=groq_key)
tavily_client = TavilyClient(api_key=tavily_key)

print("[+] Keys loaded successfully! Ready to execute.")