"""
Test PDF generation locally before deploying
"""
import os

def test_xhtml2pdf():
    """Test if xhtml2pdf can generate PDFs"""
    try:
        from xhtml2pdf import pisa

        print("+ xhtml2pdf imported successfully")

        # Create simple HTML
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
                h1 { text-align: center; margin-bottom: 5px; }
                .contact { text-align: center; margin-bottom: 20px; font-size: 14px; }
                h2 { border-bottom: 2px solid #333; padding-bottom: 5px; margin-top: 20px; }
            </style>
        </head>
        <body>
            <h1>Test Resume</h1>
            <div class="contact">
                test@example.com | (555) 123-4567 | linkedin.com/in/test | New York, NY
            </div>

            <h2>Education</h2>
            <p><strong>MBA</strong> - Harvard Business School (2020)</p>

            <h2>Professional Experience</h2>
            <div>
                <p style="font-weight: bold;">Senior Consultant - McKinsey & Company | January 2020 - Present</p>
                <ul>
                    <li>Led cross-functional team of 12 to deliver $2M project ahead of schedule</li>
                    <li>Developed strategic framework that increased client satisfaction by 40%</li>
                    <li>Conducted market analysis resulting in $5M revenue opportunity</li>
                </ul>
            </div>

            <h2>Skills</h2>
            <p>Python, SQL, Project Management, Strategic Planning, Data Analysis</p>
        </body>
        </html>
        """

        # Create output directory
        os.makedirs("output", exist_ok=True)
        pdf_path = "output/test_resume.pdf"

        print("Generating PDF...")

        # Open PDF file and generate
        with open(pdf_path, "wb") as pdf_file:
            pisa_status = pisa.CreatePDF(html_content, dest=pdf_file)

        if not pisa_status.err:
            print(f"+ PDF generated successfully: {pdf_path}")
            print(f"+ File size: {os.path.getsize(pdf_path)} bytes")
            return True
        else:
            print("- PDF generation had errors")
            return False

    except ImportError as e:
        print(f"- Import error: {e}")
        print("\nTo fix, run: pip install xhtml2pdf reportlab")
        return False
    except Exception as e:
        print(f"- Error generating PDF: {e}")
        return False


if __name__ == "__main__":
    print("Testing PDF Generation with xhtml2pdf")
    print("=" * 50)

    success = test_xhtml2pdf()

    print("\n" + "=" * 50)
    if success:
        print("+ All tests passed!")
        print("\nYou can now deploy to Render with confidence.")
    else:
        print("- Tests failed!")
        print("\nPlease install dependencies:")
        print("  pip install -r requirements.txt")
