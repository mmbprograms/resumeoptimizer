"""
Resume Optimizer Web App - Main Streamlit Application
"""
import streamlit as st
import sys
import os

# Local imports
from database import Database
from web_scraper import scrape_job_description
from llm_processor_web import ResumeOptimizer
import config

# Helper function for filename generation
def generate_output_filename(company_name: str) -> str:
    """Generate output filename"""
    from datetime import datetime
    date_str = datetime.now().strftime("%y%m%d")
    clean_company = company_name.replace(" ", "_").replace("/", "-")
    return f"Bianco_Resume_{clean_company}_{date_str}"

# Page configuration
st.set_page_config(
    page_title="Resume Optimizer",
    page_icon="📄",
    layout="wide"
)

# Initialize database
@st.cache_resource
def get_database():
    return Database()

db = get_database()

# Session state initialization
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'page' not in st.session_state:
    st.session_state.page = 'login'

# Check if we have remembered credentials in query params or cache
try:
    # Try to get cached credentials from browser storage simulation
    if hasattr(st, 'query_params'):
        if 'remembered_user' in st.query_params:
            remembered_username = st.query_params['remembered_user']
            remembered_id = st.query_params['remembered_id']
            if st.session_state.user_id is None:
                st.session_state.user_id = int(remembered_id)
                st.session_state.username = remembered_username
except:
    pass


def login_page():
    """Login/Register page"""
    st.title("📄 Resume Optimizer")
    st.markdown("---")

    tab1, tab2 = st.tabs(["Login", "Register (Admin Only)"])

    with tab1:
        st.subheader("Login")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        remember_me = st.checkbox("Remember me", value=True)

        if st.button("Login", type="primary"):
            user_id = db.authenticate_user(username, password)
            if user_id:
                st.session_state.user_id = user_id
                st.session_state.username = username
                st.session_state.page = 'dashboard'

                # Store credentials for session persistence
                if remember_me:
                    try:
                        st.query_params['remembered_user'] = username
                        st.query_params['remembered_id'] = str(user_id)
                    except:
                        pass

                st.success("✅ Login successful!")
                st.rerun()
            else:
                st.error("❌ Invalid username or password")

    with tab2:
        st.subheader("Register New User")
        st.info("This section is for admin use only to create new accounts.")

        new_username = st.text_input("New Username", key="reg_username")
        new_password = st.text_input("New Password", type="password", key="reg_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm")

        if st.button("Create Account"):
            if not new_username or not new_password:
                st.error("Please fill in all fields")
            elif new_password != confirm_password:
                st.error("Passwords do not match")
            else:
                user_id = db.create_user(new_username, new_password)
                if user_id:
                    st.success(f"Account created successfully! You can now login.")
                else:
                    st.error("Username already exists")


def dashboard():
    """Main dashboard"""
    # Sidebar
    with st.sidebar:
        st.title(f"👤 {st.session_state.username}")

        user_info = db.get_user_info(st.session_state.user_id)
        st.metric("Resumes Generated", f"{user_info['resume_count']}/{user_info['resume_limit']}")

        st.markdown("---")

        page = st.radio(
            "Navigation",
            ["My Profile", "Manage Work Experience", "Manage Target Jobs", "Generate Resumes", "My Generated Resumes"],
            key="nav_radio"
        )

        st.markdown("---")

        if st.button("Logout", type="secondary"):
            st.session_state.user_id = None
            st.session_state.username = None
            st.session_state.page = 'login'
            # Clear remembered credentials
            try:
                if 'remembered_user' in st.query_params:
                    del st.query_params['remembered_user']
                if 'remembered_id' in st.query_params:
                    del st.query_params['remembered_id']
            except:
                pass
            st.rerun()

    # Main content
    if page == "My Profile":
        profile_page()
    elif page == "Manage Work Experience":
        work_experience_page()
    elif page == "Manage Target Jobs":
        target_jobs_page()
    elif page == "Generate Resumes":
        generate_resumes_page()
    elif page == "My Generated Resumes":
        generated_resumes_page()


def profile_page():
    """Profile management page"""
    st.title("My Profile")

    # Show success message if profile was just saved
    if 'profile_saved' in st.session_state and st.session_state.profile_saved:
        st.success("✅ Profile updated successfully!")
        st.session_state.profile_saved = False

    profile = db.get_profile(st.session_state.user_id)

    with st.form("profile_form"):
        st.subheader("Personal Information")

        col1, col2 = st.columns(2)

        with col1:
            full_name = st.text_input("Full Name", value=profile.get('full_name') or "")
            email = st.text_input("Email", value=profile.get('email') or "")
            phone = st.text_input("Phone", value=profile.get('phone') or "")

        with col2:
            linkedin_url = st.text_input("LinkedIn URL", value=profile.get('linkedin_url') or "")
            location = st.text_input("Location", value=profile.get('location') or "")

        st.subheader("Education")
        education_text = st.text_area(
            "Education (one per line: Degree | School | Year)",
            value="\n".join([f"{e['degree']} | {e['school']} | {e['year']}" for e in profile.get('education', [])]) if profile.get('education') else "",
            height=100,
            help="Example: MBA | Harvard Business School | 2020"
        )

        st.subheader("Skills")
        skills_text = st.text_area(
            "Skills (comma-separated)",
            value=", ".join(profile.get('skills', [])) if profile.get('skills') else "",
            height=100,
            help="Example: Python, SQL, Project Management, Strategic Planning"
        )

        submitted = st.form_submit_button("Save Profile", type="primary")

        if submitted:
            # Parse education
            education = []
            if education_text.strip():
                for line in education_text.strip().split('\n'):
                    parts = [p.strip() for p in line.split('|')]
                    if len(parts) == 3:
                        education.append({
                            'degree': parts[0],
                            'school': parts[1],
                            'year': parts[2]
                        })

            # Parse skills
            skills = [s.strip() for s in skills_text.split(',') if s.strip()]

            profile_data = {
                'full_name': full_name,
                'email': email,
                'phone': phone,
                'linkedin_url': linkedin_url,
                'location': location,
                'education': education,
                'skills': skills
            }

            db.update_profile(st.session_state.user_id, profile_data)
            st.session_state.profile_saved = True
            st.rerun()


def work_experience_page():
    """Work experience management page"""
    st.title("Manage Work Experience")

    # Show success message if experience was just added
    if 'experience_saved' in st.session_state and st.session_state.experience_saved:
        st.success(f"✅ {st.session_state.experience_saved}")
        st.session_state.experience_saved = False

    # Get existing work experiences
    experiences = db.get_work_experiences(st.session_state.user_id)

    # Add new experience section
    with st.expander("➕ Add New Work Experience", expanded=len(experiences) == 0):
        with st.form("add_experience_form"):
            col1, col2 = st.columns(2)

            with col1:
                company = st.text_input("Company Name")
                job_title = st.text_input("Job Title")

            with col2:
                start_date = st.text_input("Start Date", placeholder="e.g., January 2022")
                is_current = st.checkbox("Current Position")
                end_date = st.text_input("End Date", placeholder="e.g., December 2023", disabled=is_current)

            st.subheader("Accomplishment Bullets")
            st.info("Add 10-20 bullets describing your accomplishments. The AI will select the best ones for each resume.")

            bullets_text = st.text_area(
                "Bullets (one per line, optional bullet point symbols)",
                height=200,
                placeholder="Led cross-functional team of 12 to deliver $2M project 2 weeks ahead of schedule\nDeveloped strategic framework that increased client satisfaction by 40%\n..."
            )

            submitted = st.form_submit_button("Add Work Experience", type="primary")

            if submitted:
                if not company or not job_title or not start_date:
                    st.error("Please fill in company, title, and start date")
                else:
                    # Add experience
                    exp_id = db.add_work_experience(
                        st.session_state.user_id,
                        company,
                        job_title,
                        start_date,
                        end_date if not is_current else None,
                        is_current
                    )

                    # Add bullets
                    if bullets_text.strip():
                        bullets = []
                        for line in bullets_text.strip().split('\n'):
                            # Remove bullet symbols
                            cleaned = line.strip().lstrip('•-*→ ')
                            if cleaned:
                                bullets.append(cleaned)

                        db.add_bullets_bulk(exp_id, bullets)

                    st.session_state.experience_saved = f"Added {company} - {job_title}"
                    st.rerun()

    # Display existing experiences
    st.markdown("---")
    st.subheader("Your Work Experience")

    if not experiences:
        st.info("No work experience added yet. Add your first one above!")
    else:
        for exp in experiences:
            with st.expander(f"📁 {exp['company_name']} - {exp['job_title']}", expanded=False):
                st.write(f"**Dates:** {exp['start_date']} - {exp['end_date'] if exp['end_date'] else 'Present'}")

                # Get bullets
                bullets = db.get_bullets(exp['id'])

                st.write(f"**Bullets:** {len(bullets)}")

                if bullets:
                    for bullet in bullets:
                        col1, col2, col3 = st.columns([8, 1, 1])
                        with col1:
                            st.write(f"• {bullet['bullet_text']}")
                        with col2:
                            if st.button("✏️", key=f"edit_{bullet['id']}", help="Edit"):
                                st.session_state[f"editing_{bullet['id']}"] = True
                        with col3:
                            if st.button("🗑️", key=f"del_{bullet['id']}", help="Delete"):
                                db.delete_bullet(bullet['id'])
                                st.rerun()

                        # Inline edit
                        if st.session_state.get(f"editing_{bullet['id']}", False):
                            with st.form(f"edit_form_{bullet['id']}"):
                                new_text = st.text_area("Edit bullet", value=bullet['bullet_text'])
                                col_a, col_b = st.columns(2)
                                with col_a:
                                    if st.form_submit_button("Save"):
                                        db.update_bullet(bullet['id'], new_text)
                                        st.session_state[f"editing_{bullet['id']}"] = False
                                        st.rerun()
                                with col_b:
                                    if st.form_submit_button("Cancel"):
                                        st.session_state[f"editing_{bullet['id']}"] = False
                                        st.rerun()
                else:
                    st.info("No bullets added yet")

                # Add more bullets
                with st.form(f"add_bullets_{exp['id']}"):
                    new_bullets = st.text_area("Add more bullets (one per line)", key=f"new_bullets_{exp['id']}")
                    if st.form_submit_button("Add Bullets"):
                        if new_bullets.strip():
                            bullets_list = [b.strip().lstrip('•-*→ ') for b in new_bullets.split('\n') if b.strip()]
                            db.add_bullets_bulk(exp['id'], bullets_list)
                            st.success(f"Added {len(bullets_list)} bullets")
                            st.rerun()

                # Delete experience
                if st.button(f"🗑️ Delete Entire Experience", key=f"delete_exp_{exp['id']}", type="secondary"):
                    if st.session_state.get(f"confirm_delete_{exp['id']}", False):
                        db.delete_work_experience(exp['id'])
                        st.success("Deleted")
                        st.rerun()
                    else:
                        st.session_state[f"confirm_delete_{exp['id']}"] = True
                        st.warning("Click again to confirm deletion")


def target_jobs_page():
    """Target jobs management page"""
    st.title("Manage Target Jobs")

    # Show success message if job was just added
    if 'job_saved' in st.session_state and st.session_state.job_saved:
        st.success(f"✅ {st.session_state.job_saved}")
        st.session_state.job_saved = False

    # Add new job section
    with st.expander("➕ Add New Target Job", expanded=True):
        with st.form("add_job_form"):
            col1, col2 = st.columns(2)

            with col1:
                company = st.text_input("Company Name")
                job_title = st.text_input("Job Title")

            with col2:
                job_url = st.text_input("Job URL (optional)")

            job_description = st.text_area(
                "Job Description",
                height=200,
                help="Paste the full job description here, or leave blank to scrape from URL"
            )

            col_a, col_b = st.columns(2)

            with col_a:
                submitted = st.form_submit_button("Add Job", type="primary")

            with col_b:
                scrape = st.form_submit_button("Scrape from URL")

            if submitted:
                if not company or not job_title:
                    st.error("Please provide company name and job title")
                else:
                    job_id = db.add_target_job(
                        st.session_state.user_id,
                        company,
                        job_title,
                        job_url,
                        job_description
                    )
                    st.session_state.job_saved = f"Added {company} - {job_title}"
                    st.rerun()

            if scrape:
                if not job_url:
                    st.error("Please provide a job URL to scrape")
                else:
                    with st.spinner("Scraping job description..."):
                        description = scrape_job_description(job_url)
                        if description:
                            # Add job with scraped description
                            job_id = db.add_target_job(
                                st.session_state.user_id,
                                company or "Company",
                                job_title or "Position",
                                job_url,
                                description
                            )
                            st.session_state.job_saved = f"Scraped and added job! ({len(description)} characters)"
                            st.rerun()
                        else:
                            st.error("Failed to scrape job description. Please paste it manually.")

    # Display existing jobs
    st.markdown("---")
    st.subheader("Your Target Jobs")

    jobs = db.get_target_jobs(st.session_state.user_id)

    if not jobs:
        st.info("No target jobs added yet. Add your first one above!")
    else:
        for job in jobs:
            with st.expander(f"💼 {job['company_name']} - {job['job_title']}", expanded=False):
                st.write(f"**URL:** {job['job_url'] or 'N/A'}")
                st.write(f"**Added:** {job['date_added']}")

                if job['job_description']:
                    st.write(f"**Description:** ({len(job['job_description'])} characters)")
                    with st.container():
                        st.text_area(
                            "Job Description",
                            value=job['job_description'][:500] + "..." if len(job['job_description']) > 500 else job['job_description'],
                            height=150,
                            key=f"desc_{job['id']}",
                            disabled=True
                        )
                else:
                    st.warning("No job description available")

                if st.button(f"🗑️ Delete Job", key=f"delete_job_{job['id']}"):
                    db.delete_target_job(job['id'])
                    st.success("Deleted")
                    st.rerun()


def generate_resumes_page():
    """Resume generation page"""
    st.title("Generate Resumes")

    # Check if profile is complete
    profile = db.get_profile(st.session_state.user_id)
    experiences = db.get_work_experiences(st.session_state.user_id)
    target_jobs = db.get_target_jobs(st.session_state.user_id)

    # Validation
    warnings = []
    if not profile.get('full_name'):
        warnings.append("⚠️ Profile incomplete - please fill in your personal information")
    if not experiences:
        warnings.append("⚠️ No work experience added - please add your work history")
    if not target_jobs:
        warnings.append("⚠️ No target jobs added - please add jobs you're applying to")

    # Check if has bullets
    has_bullets = False
    for exp in experiences:
        bullets = db.get_bullets(exp['id'])
        if bullets:
            has_bullets = True
            break

    if not has_bullets and experiences:
        warnings.append("⚠️ No accomplishment bullets added - please add bullets to your work experience")

    if warnings:
        for warning in warnings:
            st.warning(warning)
        return

    # Check resume limit
    if not db.can_generate_resume(st.session_state.user_id):
        st.error("You've reached your resume generation limit (50 resumes). Please contact the administrator.")
        return

    user_info = db.get_user_info(st.session_state.user_id)
    st.info(f"Resumes remaining: {user_info['resume_limit'] - user_info['resume_count']}")

    # Select job
    st.subheader("Select Target Job")

    job_options = {f"{job['company_name']} - {job['job_title']}": job['id'] for job in target_jobs}
    selected_job_name = st.selectbox("Choose a job", list(job_options.keys()))
    selected_job_id = job_options[selected_job_name]

    if st.button("Generate Resume", type="primary"):
        generate_resume(selected_job_id)


def generate_resume(job_id: int):
    """Generate resume for specific job"""
    with st.spinner("Generating your customized resume..."):
        try:
            # Get job details
            job = db.get_target_job(job_id)

            if not job['job_description']:
                st.error("Job description is missing. Please add it in Manage Target Jobs.")
                return

            # Get user profile and experiences
            profile = db.get_profile(st.session_state.user_id)
            experiences = db.get_work_experiences(st.session_state.user_id)

            # Build bullet bank
            bullet_bank = {}
            for exp in experiences:
                bullets = db.get_bullets(exp['id'])
                bullet_bank[exp['id']] = {
                    'company': exp['company_name'],
                    'title': exp['job_title'],
                    'dates': f"{exp['start_date']} - {exp['end_date'] if exp['end_date'] else 'Present'}",
                    'bullets': [b['bullet_text'] for b in bullets]
                }

            # Initialize AI processor
            optimizer = ResumeOptimizer(config.ANTHROPIC_API_KEY)

            # Generate bullets for each experience
            generated_bullets = {}
            for exp_id, exp_data in bullet_bank.items():
                st.write(f"Generating bullets for {exp_data['company']}...")

                # Use AI to select and tailor bullets
                selected_bullets = optimizer.generate_bullets(
                    job_description=job['job_description'],
                    experience_bullets=exp_data['bullets'],
                    target_count=5,
                    context=f"Position: {exp_data['title']} at {exp_data['company']}"
                )

                generated_bullets[exp_id] = selected_bullets

            # Create custom HTML with user's profile
            html_content = build_resume_html(profile, experiences, generated_bullets)

            # Save HTML
            output_filename = generate_output_filename(job['company_name'])
            output_dir = "output"
            os.makedirs(output_dir, exist_ok=True)

            html_path = os.path.join(output_dir, f"{output_filename}.html")
            pdf_path = os.path.join(output_dir, f"{output_filename}.pdf")

            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)

            # Generate PDF
            st.write("Converting to PDF...")
            from playwright.sync_api import sync_playwright

            try:
                with sync_playwright() as p:
                    # Try chromium first, fallback to webkit if chromium fails
                    try:
                        browser = p.chromium.launch(
                            headless=True,
                            args=['--disable-dev-shm-usage', '--no-sandbox']
                        )
                    except Exception as chromium_error:
                        # Fallback to webkit which is more reliable on some platforms
                        st.info("Using webkit instead of chromium for PDF generation...")
                        browser = p.webkit.launch(headless=True)

                    page = browser.new_page()

                    html_url = f'file:///{os.path.abspath(html_path).replace(os.sep, "/")}'
                    page.goto(html_url)

                    page.pdf(
                        path=pdf_path,
                        format='Letter',
                        print_background=True,
                        margin={
                            'top': '0.5in',
                            'right': '0.75in',
                            'bottom': '0.5in',
                            'left': '0.75in'
                        }
                    )

                    browser.close()
                success = True
            except Exception as pdf_error:
                st.error(f"PDF generation error: {str(pdf_error)}")
                st.error("Please contact administrator to verify Playwright browsers are installed correctly.")
                success = False

            if success:
                # Save to database
                import json
                db.save_generated_resume(
                    st.session_state.user_id,
                    job_id,
                    json.dumps(generated_bullets),
                    html_content,
                    output_filename
                )

                # Increment resume count
                db.increment_resume_count(st.session_state.user_id)

                st.success("Resume generated successfully!")

                # Offer download
                with open(pdf_path, 'rb') as f:
                    st.download_button(
                        label="📥 Download Resume PDF",
                        data=f.read(),
                        file_name=f"{output_filename}.pdf",
                        mime="application/pdf",
                        type="primary"
                    )
            else:
                st.error("Failed to generate PDF. Please check the logs.")

        except Exception as e:
            st.error(f"Error generating resume: {str(e)}")
            import traceback
            st.code(traceback.format_exc())


def build_resume_html(profile, experiences, generated_bullets):
    """Build complete HTML resume"""
    # This is a simplified version - you can customize the template
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
            h1 {{ text-align: center; margin-bottom: 5px; }}
            .contact {{ text-align: center; margin-bottom: 20px; font-size: 14px; }}
            h2 {{ border-bottom: 2px solid #333; padding-bottom: 5px; margin-top: 20px; }}
            .job {{ margin-bottom: 15px; }}
            .job-header {{ display: flex; justify-content: space-between; font-weight: bold; }}
            ul {{ margin: 5px 0; padding-left: 20px; }}
            li {{ margin: 3px 0; }}
        </style>
    </head>
    <body>
        <h1>{profile['full_name'] or 'Your Name'}</h1>
        <div class="contact">
            {profile['email'] or ''} | {profile['phone'] or ''} | {profile['linkedin_url'] or ''} | {profile['location'] or ''}
        </div>

        <h2>Education</h2>
    """

    # Add education
    for edu in profile.get('education', []):
        html += f"<p><strong>{edu['degree']}</strong> - {edu['school']} ({edu['year']})</p>"

    # Add experience
    html += "<h2>Professional Experience</h2>"

    for exp in experiences:
        bullets_html = ""
        if exp['id'] in generated_bullets:
            for bullet in generated_bullets[exp['id']]:
                bullets_html += f"<li>{bullet}</li>"

        html += f"""
        <div class="job">
            <div class="job-header">
                <span>{exp['job_title']} - {exp['company_name']}</span>
                <span>{exp['start_date']} - {exp['end_date'] if exp['end_date'] else 'Present'}</span>
            </div>
            <ul>
                {bullets_html}
            </ul>
        </div>
        """

    # Add skills
    html += "<h2>Skills</h2>"
    html += "<p>" + ", ".join(profile.get('skills', [])) + "</p>"

    html += "</body></html>"

    return html


def generated_resumes_page():
    """View generated resumes"""
    st.title("My Generated Resumes")

    resumes = db.get_user_resumes(st.session_state.user_id)

    if not resumes:
        st.info("No resumes generated yet. Go to 'Generate Resumes' to create your first one!")
    else:
        for resume in resumes:
            with st.expander(f"📄 {resume['company_name']} - {resume['job_title']} (Created: {resume['created_at']})", expanded=False):
                pdf_path = f"output/{resume['pdf_filename']}.pdf"

                if os.path.exists(pdf_path):
                    with open(pdf_path, 'rb') as f:
                        st.download_button(
                            label="📥 Download PDF",
                            data=f.read(),
                            file_name=f"{resume['pdf_filename']}.pdf",
                            mime="application/pdf",
                            key=f"download_{resume['id']}"
                        )
                else:
                    st.warning("PDF file not found")


# Main app logic
def main():
    if st.session_state.user_id is None:
        login_page()
    else:
        dashboard()


if __name__ == "__main__":
    main()
