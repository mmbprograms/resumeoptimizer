"""
Module for generating optimized resume bullets using Anthropic API
"""
import anthropic
from typing import List, Dict
import config


class ResumeOptimizer:
    """Handles LLM-based resume bullet optimization"""

    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)

    def generate_bullets(
        self,
        job_description: str,
        arya_experiences: List[str],
        deloitte_experiences: List[str]
    ) -> Dict[str, List[str]]:
        """
        Generate optimized resume bullets for both companies based on job description

        Args:
            job_description: The full job posting text
            arya_experiences: List of available Arya experience bullets
            deloitte_experiences: List of available Deloitte experience bullets

        Returns:
            Dict with keys 'Arya' and 'Deloitte', each containing list of optimized bullets
        """

        prompt = f"""You are an expert resume writer specializing in ATS-optimized resumes. Your task is to create compelling resume bullets for a job application.

JOB DESCRIPTION:
{job_description}

AVAILABLE ARYA CONSULTING PARTNERS EXPERIENCE (March 2024-Present):
{self._format_experience_list(arya_experiences)}

AVAILABLE DELOITTE CONSULTING EXPERIENCE (September 2022-December 2023):
{self._format_experience_list(deloitte_experiences)}

INSTRUCTIONS:
1. Create approximately {config.ARYA_TARGET_BULLETS} bullets for Arya Consulting Partners (more robust since it's more recent and varied)
2. Create approximately {config.DELOITTE_TARGET_BULLETS} bullets for Deloitte Consulting
3. Select and adapt experiences that are most relevant to the job description
4. Optimize bullets for ATS systems by incorporating relevant keywords from the job description
5. You may combine elements from multiple experience bullets to create new, more impactful bullets
6. Each bullet should start with a strong action verb
7. Include quantifiable results where available, and generate plausible impact metrics to be included where possible
8. Ensure the language and terminology align with what's in the job description
9. Keep bullets concise and impactful
10. The total resume must fit on ONE page, so be mindful of length

IMPORTANT: Your response must be ONLY a valid JSON object with this exact structure:
{{
    "arya": [
        "First Arya bullet point",
        "Second Arya bullet point",
        ...
    ],
    "deloitte": [
        "First Deloitte bullet point",
        "Second Deloitte bullet point",
        ...
    ]
}}

Do not include any other text, explanation, or markdown formatting. Only the JSON object."""

        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            response_text = message.content[0].text.strip()

            # Parse JSON response
            import json
            result = json.loads(response_text)

            # Normalize keys to proper case
            return {
                'Arya': result.get('arya', []),
                'Deloitte': result.get('deloitte', [])
            }

        except Exception as e:
            print(f"Error generating bullets: {str(e)}")
            # Return empty lists on error
            return {
                'Arya': [],
                'Deloitte': []
            }

    def _format_experience_list(self, experiences: List[str]) -> str:
        """Format experience list for prompt"""
        return '\n'.join([f"- {exp}" for exp in experiences])
