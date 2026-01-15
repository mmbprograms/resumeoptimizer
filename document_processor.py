"""
Module for processing HTML documents and generating PDFs
"""
import os
import re
from typing import List
import config
from datetime import datetime


class DocumentProcessor:
    """Handles HTML document manipulation and PDF generation"""

    def __init__(self, template_path: str):
        self.template_path = template_path
        # Load template once
        with open(template_path, 'r', encoding='utf-8') as f:
            self.template_html = f.read()

    def create_resume(
        self,
        arya_bullets: List[str],
        deloitte_bullets: List[str],
        output_path: str
    ) -> bool:
        """
        Create a resume HTML document by replacing bullets in the template

        Args:
            arya_bullets: List of bullets for Arya Consulting Partners
            deloitte_bullets: List of bullets for Deloitte Consulting
            output_path: Path to save the output HTML document

        Returns:
            True if successful, False otherwise
        """
        try:
            # Start with template
            html_content = self.template_html

            # Generate Arya bullets HTML
            arya_html = self._generate_bullet_html(arya_bullets)
            # Replace Arya placeholder
            html_content = re.sub(
                config.ARYA_BULLETS_PLACEHOLDER,
                f"<!-- ARYA_BULLETS_START -->\n{arya_html}\n                <!-- ARYA_BULLETS_END -->",
                html_content,
                flags=re.DOTALL
            )

            # Generate Deloitte bullets HTML
            deloitte_html = self._generate_bullet_html(deloitte_bullets)
            # Replace Deloitte placeholder
            html_content = re.sub(
                config.DELOITTE_BULLETS_PLACEHOLDER,
                f"<!-- DELOITTE_BULLETS_START -->\n{deloitte_html}\n                <!-- DELOITTE_BULLETS_END -->",
                html_content,
                flags=re.DOTALL
            )

            # Save HTML file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)

            return True

        except Exception as e:
            print(f"Error creating resume: {str(e)}")
            return False

    def _generate_bullet_html(self, bullets: List[str]) -> str:
        """
        Generate HTML for bullet points

        Args:
            bullets: List of bullet point texts

        Returns:
            HTML string with <ul> and <li> elements
        """
        if not bullets:
            return "                <ul>\n                    <li>XX</li>\n                </ul>"

        html_lines = ["                <ul>"]
        for bullet in bullets:
            # Escape any HTML special characters
            escaped_bullet = bullet.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            html_lines.append(f"                    <li>{escaped_bullet}</li>")
        html_lines.append("                </ul>")

        return '\n'.join(html_lines)

    def convert_to_pdf(self, html_path: str, pdf_path: str) -> bool:
        """
        Convert HTML document to PDF using Playwright

        Args:
            html_path: Path to input HTML document
            pdf_path: Path to output PDF file

        Returns:
            True if successful, False otherwise
        """
        try:
            from playwright.sync_api import sync_playwright

            with sync_playwright() as p:
                # Launch browser in headless mode
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()

                # Load the HTML file
                html_url = f'file:///{os.path.abspath(html_path).replace(os.sep, "/")}'
                page.goto(html_url)

                # Generate PDF with proper settings
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
                return True

        except ImportError:
            print("  Error: Playwright not installed")
            print("  Install with: pip install playwright")
            print("  Then run: python -m playwright install chromium")
            return False
        except Exception as e:
            print(f"  Error converting to PDF: {str(e)}")
            return False


def generate_output_filename(company_name: str) -> str:
    """
    Generate output filename in format: Bianco_Resume_{COMPANY}_{YYMMDD}

    Args:
        company_name: Company name (may include _1, _2 suffix for duplicates)

    Returns:
        Filename without extension
    """
    date_str = datetime.now().strftime("%y%m%d")
    return f"Bianco_Resume_{company_name}_{date_str}"
