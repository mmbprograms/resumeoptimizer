# Resume Optimizer Web App

A web-based application for generating customized, ATS-optimized resumes using AI.

## Features

- **User Authentication**: Simple password-based login system
- **Profile Management**: Store personal information, education, and skills
- **Work Experience & Bullet Bank**: Add multiple work experiences with accomplishment bullets
- **Target Job Management**: Add and manage jobs you're applying to
- **AI Resume Generation**: Automatically select and tailor bullets for each job
- **PDF Export**: Download professional PDF resumes
- **Usage Limits**: 50 resumes per user to manage API costs

## Local Development

### Prerequisites

- Python 3.8+
- Pip package manager

### Setup

1. Install dependencies:
```bash
cd web_app
pip install -r requirements.txt
```

2. Install Playwright browsers:
```bash
python -m playwright install chromium
```

3. Run the app:
```bash
streamlit run app.py
```

4. Open browser to: `http://localhost:8501`

## Deployment to Render

### Step 1: Prepare Repository

1. Make sure all files are in the `web_app` directory
2. Commit and push to GitHub:
```bash
cd "c:\Users\mmbia\OneDrive\Desktop\17 - Job Search 2026"
git init
git add web_app
git commit -m "Initial commit - Resume Optimizer Web App"
git branch -M main
git remote add origin https://github.com/mmbprograms/resumeoptimizer.git
git push -u origin main
```

### Step 2: Create Render Web Service

1. Log into [Render Dashboard](https://dashboard.render.com/)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository: `mmbprograms/resumeoptimizer`
4. Configure the service:
   - **Name**: `resume-optimizer` (or your choice)
   - **Region**: Choose closest to you
   - **Branch**: `main`
   - **Root Directory**: `web_app`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt && python -m playwright install chromium && python -m playwright install-deps`
   - **Start Command**: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`

### Step 3: Set Environment Variables

In the Render dashboard, go to "Environment" and add:

- **Key**: `ANTHROPIC_API_KEY`
- **Value**: `your_anthropic_api_key_here`

### Step 4: Deploy

1. Click "Create Web Service"
2. Render will build and deploy your app (takes 5-10 minutes)
3. Once complete, you'll get a URL like: `https://resume-optimizer.onrender.com`

### Step 5: Create First User

1. Visit your app URL
2. Go to "Register" tab
3. Create your account
4. Login and start using!

## Usage

### First Time Setup

1. **Login** with your credentials
2. **My Profile**: Fill in personal info, education, skills
3. **Manage Work Experience**: Add your work history and accomplishment bullets (10-20 per job)
4. **Manage Target Jobs**: Add jobs you're applying to
5. **Generate Resumes**: Select a job and generate customized resume
6. **Download**: Get your PDF resume

### Tips

- Add 10-20 bullets per work experience for best results
- The AI will select the most relevant 5 bullets per job
- More bullets in your bank = better AI matching
- Job descriptions can be scraped automatically or pasted manually

## File Structure

```
web_app/
├── app.py                  # Main Streamlit application
├── database.py            # SQLite database models and operations
├── config.py              # Configuration (API keys, settings)
├── web_scraper.py         # Job description scraping
├── llm_processor.py       # AI bullet generation
├── document_processor.py  # HTML/PDF generation
├── resume_template.html   # Resume HTML template
├── requirements.txt       # Python dependencies
├── .streamlit/
│   └── config.toml       # Streamlit configuration
├── output/               # Generated PDFs (created automatically)
└── README.md            # This file
```

## Troubleshooting

### "Cannot connect to database"
- Database file is created automatically on first run
- Make sure app has write permissions

### "Playwright browser not found"
- Run: `python -m playwright install chromium`
- On Render, this is handled by build command

### "API key not found"
- Check environment variable is set correctly
- For local dev: update `config.py`
- For Render: set in Environment tab

### "Resume generation failed"
- Check you have work experience with bullets added
- Check job description is not empty
- Check API key is valid

## API Costs

- Each resume generation costs ~$0.10-0.20
- With 50 resume limit per user, max cost is ~$10 per user
- Monitor usage in Anthropic dashboard

## Security Notes

- Passwords are hashed with SHA-256 and salt
- API key stored as environment variable (not in code)
- Database stored locally on server
- HTTPS enforced by Render

## Support

For issues or questions, check the troubleshooting section above or contact the administrator.
