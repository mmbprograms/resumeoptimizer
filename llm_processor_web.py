"""
LLM Processor for Web App - Simplified for dynamic work experiences
"""
from anthropic import Anthropic
from typing import List
import json


class ResumeOptimizer:
    """Handle AI-powered resume optimization"""

    def __init__(self, api_key: str):
        self.client = Anthropic(api_key=api_key)

    def generate_bullets(
        self,
        job_description: str,
        experience_bullets: List[str],
        target_count: int = 5,
        context: str = ""
    ) -> List[str]:
        """
        Generate optimized bullets for a single work experience

        Args:
            job_description: The target job description
            experience_bullets: Available bullets for this experience
            target_count: Number of bullets to generate (default 5)
            context: Additional context (e.g., "Position: Consultant at McKinsey")

        Returns:
            List of optimized bullets
        """
        if not experience_bullets:
            return []

        # Build prompt
        prompt = f"""You are a professional resume writer helping to optimize resume bullets for a specific job application.

JOB DESCRIPTION:
{job_description}

AVAILABLE EXPERIENCE BULLETS{' (' + context + ')' if context else ''}:
{self._format_bullets(experience_bullets)}

TASK:
Select and tailor approximately {target_count} bullets from the available experience that are most relevant to this job.

GUIDELINES:
1. Choose bullets that best match the job requirements and keywords
2. Reword bullets to emphasize skills mentioned in the job description
3. Keep bullets concise and impactful (1-2 lines each)
4. Start each bullet with a strong action verb
5. Include metrics and quantifiable achievements when available
6. Ensure bullets are relevant to the target role

Return your response as a JSON object with this exact structure:
{{
    "bullets": [
        "First optimized bullet point",
        "Second optimized bullet point",
        ...
    ]
}}

IMPORTANT: Return ONLY the JSON object, no other text."""

        try:
            # Call Claude API
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            # Parse response
            response_text = message.content[0].text.strip()

            # Extract JSON if wrapped in markdown
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()

            result = json.loads(response_text)
            return result.get('bullets', [])

        except Exception as e:
            print(f"Error generating bullets: {str(e)}")
            # Fallback: return first N bullets
            return experience_bullets[:target_count]

    def _format_bullets(self, bullets: List[str]) -> str:
        """Format bullet list for prompt"""
        return "\n".join([f"- {bullet}" for bullet in bullets])
