"""
Test the updated resume HTML formatting
"""
from xhtml2pdf import pisa
import os

# Sample data
profile = {
    'full_name': 'John Smith',
    'email': 'john.smith@email.com',
    'phone': '(555) 123-4567',
    'linkedin_url': 'linkedin.com/in/johnsmith',
    'location': 'New York, NY',
    'education': [
        {'degree': 'MBA', 'school': 'Harvard Business School', 'year': '2020'},
        {'degree': 'BA in Economics', 'school': 'University of Pennsylvania', 'year': '2016'}
    ],
    'skills': ['Python', 'SQL', 'Strategic Planning', 'Project Management', 'Data Analysis', 'Financial Modeling']
}

experiences = [
    {
        'id': 1,
        'company_name': 'McKinsey & Company',
        'job_title': 'Senior Consultant',
        'start_date': 'January 2020',
        'end_date': None
    },
    {
        'id': 2,
        'company_name': 'Deloitte Consulting',
        'job_title': 'Business Analyst',
        'start_date': 'June 2016',
        'end_date': 'December 2019'
    }
]

generated_bullets = {
    1: [
        'Led cross-functional team of 12 to deliver $2M digital transformation project 2 weeks ahead of schedule',
        'Developed strategic framework that increased client operational efficiency by 40% and reduced costs by $1.5M annually',
        'Conducted comprehensive market analysis resulting in identification of $5M revenue opportunity',
        'Built financial models to evaluate M&A opportunities, supporting $50M acquisition decision',
        'Mentored 3 junior consultants, resulting in 100% promotion rate within 18 months'
    ],
    2: [
        'Analyzed complex datasets using SQL and Python to identify cost-saving opportunities worth $800K',
        'Created executive dashboards in Tableau that improved decision-making speed by 30%',
        'Collaborated with C-suite executives to design and implement process improvements across 5 departments',
        'Presented strategic recommendations to Fortune 500 clients, resulting in 95% implementation rate',
        'Developed automated reporting system that reduced manual work by 20 hours per week'
    ]
}

# Build HTML using the same function from app.py
def build_resume_html(profile, experiences, generated_bullets):
    """Build complete HTML resume with professional formatting"""
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 40px;
            line-height: 1.4;
            color: #333;
        }}

        /* Name - Largest */
        h1 {{
            text-align: center;
            margin: 0 0 8px 0;
            font-size: 24px;
            font-weight: bold;
        }}

        /* Contact info - Medium (same as section headers) */
        .contact {{
            text-align: center;
            margin: 0 0 20px 0;
            font-size: 12px;
            line-height: 1.3;
        }}

        /* Section headers - Medium */
        h2 {{
            font-size: 12px;
            font-weight: bold;
            border-bottom: 1px solid #333;
            padding-bottom: 3px;
            margin: 16px 0 8px 0;
            text-transform: uppercase;
        }}

        /* Job section */
        .job {{
            margin-bottom: 12px;
        }}

        /* Company name - bold, small text */
        .company {{
            font-weight: bold;
            font-size: 11px;
            margin: 0 0 2px 0;
            line-height: 1.2;
        }}

        /* Job title - small text */
        .title {{
            font-size: 11px;
            margin: 0 0 2px 0;
            line-height: 1.2;
        }}

        /* Dates - small text, italic */
        .dates {{
            font-size: 11px;
            font-style: italic;
            margin: 0 0 4px 0;
            line-height: 1.2;
        }}

        /* Bullets - Small text */
        ul {{
            margin: 0 0 0 0;
            padding-left: 18px;
        }}

        li {{
            font-size: 11px;
            margin: 0 0 3px 0;
            line-height: 1.3;
        }}

        /* Education and Skills content - Small text */
        .content {{
            font-size: 11px;
            margin: 4px 0;
            line-height: 1.3;
        }}

        .edu-item {{
            margin: 4px 0;
        }}
    </style>
</head>
<body>
    <h1>{profile['full_name'] or 'Your Name'}</h1>
    <div class="contact">
        {profile['email'] or ''} | {profile['phone'] or ''} | {profile['linkedin_url'] or ''} | {profile['location'] or ''}
    </div>

    <h2>Professional Experience</h2>
"""

    # Add experience (now comes first)
    for exp in experiences:
        bullets_html = ""
        if exp['id'] in generated_bullets:
            for bullet in generated_bullets[exp['id']]:
                bullets_html += f"        <li>{bullet}</li>\n"

        html += f"""    <div class="job">
        <div class="company">{exp['company_name']}</div>
        <div class="title">{exp['job_title']}</div>
        <div class="dates">{exp['start_date']} - {exp['end_date'] if exp['end_date'] else 'Present'}</div>
        <ul>
{bullets_html}        </ul>
    </div>
"""

    # Add education (now comes after experience)
    html += "\n    <h2>Education</h2>\n"
    for edu in profile.get('education', []):
        html += f'    <div class="content edu-item"><strong>{edu["degree"]}</strong> - {edu["school"]} ({edu["year"]})</div>\n'

    # Add skills
    html += "\n    <h2>Skills</h2>\n"
    html += f'    <div class="content">{", ".join(profile.get("skills", []))}</div>\n'

    html += "</body>\n</html>"

    return html


# Generate resume
html_content = build_resume_html(profile, experiences, generated_bullets)

# Create output directory
os.makedirs("output", exist_ok=True)

# Save HTML
html_path = "output/test_formatted_resume.html"
with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"+ HTML saved: {html_path}")

# Generate PDF
pdf_path = "output/test_formatted_resume.pdf"
with open(pdf_path, "wb") as pdf_file:
    pisa_status = pisa.CreatePDF(html_content, dest=pdf_file)

if not pisa_status.err:
    print(f"+ PDF generated: {pdf_path}")
    print(f"+ File size: {os.path.getsize(pdf_path)} bytes")
    print("\nFormatting test complete!")
    print("Open the PDF to verify:")
    print("  - Professional Experience comes BEFORE Education")
    print("  - Name is largest (24px)")
    print("  - Contact info and section headers are medium (12px)")
    print("  - Content is small (11px)")
    print("  - Company/Title/Dates are on 3 separate lines")
    print("  - No weird spacing between lines")
else:
    print("- PDF generation had errors")
