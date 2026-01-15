#!/bin/bash

# Install Playwright browsers
python -m playwright install chromium
python -m playwright install-deps

# Create output directory
mkdir -p web_app/output
