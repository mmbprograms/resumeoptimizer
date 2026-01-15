"""
Configuration file for Resume Optimizer Web App
"""
import os

# Anthropic API Configuration
# This will be set as environment variable on Render
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# Web scraping configuration
SCRAPING_TIMEOUT = 10
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
