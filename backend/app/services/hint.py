"""
hint.py — LLM-powered hint engine.

The key design decision: hints are grounded in the specific failure.
We never send a generic "help me" prompt. Every hint request includes:
  - The exact failing test case (input + expected + actual output)
  - The user's actual code
  - Which hints they've already seen (so we never repeat)
  - The hint level (1=nudge, 2=specific, 3=near-solution)

This produces hints that say "your loop doesn't handle empty input"
instead of "think about edge cases".
"""

from groq import Groq
from app.config import settings

client = Groq(api_key=settings.groq_api_key)


HINT_LEVEL_INSTRUCTIONS = {
    1: (
        "Give a one-sentence nudge that points the user toward the right area "
        "of their code without mentioning the specific bug. It should make them "
        "think, not give it away."
    ),
    2: (
        "Give a one or two sentence hint that identifies the specific issue "
        "causing the failure. Name the relevant concept or edge case, but do "
        "not show any code or the fix."
    ),
    3: (
        "Give a two to three sentence hint that explains exactly what is wrong "
        "and what approach will fix it. You may describe the fix in plain English "
        "but do not write actual code."
    ),
}


async def generate_hint(
    problem_title: str,
    problem_description: str,
    user_code: str,
    failing_test: dict,
    passed_count: int,
    total_count: int,
    hint_level: int,
    prior_hints: list[str],
) -> str:
    """
    Calls the Groq API and returns a grounded, level-appropriate hint.
    """
    level_instruction = HINT_LEVEL_INSTRUCTIONS.get(hint_level, HINT_LEVEL_INSTRUCTIONS[2])

    prior_hints_text = ""
    if prior_hints:
        formatted = "\n".join(f"  - {h}" for h in prior_hints)
        prior_hints_text = f"""
Previously shown hints (do NOT repeat or paraphrase these):
{formatted}
"""

    failing_info = f"""
Failing test case:
  Input:    {failing_test.get('input', 'N/A')}
  Expected: {failing_test.get('expected', 'N/A')}
  Actual:   {failing_test.get('actual', 'N/A')}
  Error:    {failing_test.get('error', 'None')}
"""

    prompt = f"""You are a patient coding mentor helping a student debug their solution.

Problem: {problem_title}
Description: {problem_description}

The student's code:
```python
{user_code}
```

Progress: {passed_count} of {total_count} test cases passing.
{failing_info}
{prior_hints_text}
Hint level requested: {hint_level} of 3

Instructions: {level_instruction}

Important rules:
- Be specific to THIS failure, not generic advice
- Do not write any code
- Do not reveal the complete solution
- Keep it concise (1-3 sentences max)
- Speak directly to the student ("Your loop...", "Consider what happens when...")

Hint:"""

    message = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.choices[0].message.content.strip()