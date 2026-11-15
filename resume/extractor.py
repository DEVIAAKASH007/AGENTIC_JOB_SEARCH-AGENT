from models.schemas import CandidateProfile


def extract_candidate_profile(model, resume_text):
    """
    Extract structured candidate information from a resume.
    """

    structured_model = model.with_structured_output(
        CandidateProfile
    )

    prompt = f"""
You are a resume information extraction system.

Extract the candidate information from the resume.

Rules:

1. Extract only information explicitly supported
   by the resume.

2. Do not invent skills.

3. Do not infer skills.

4. Extract technical skills such as:
   programming languages,
   frameworks,
   libraries,
   databases,
   cloud technologies,
   AI/ML technologies,
   tools.

5. Extract projects.

6. Extract education.

7. Extract work experience.

8. Extract courses.

9. Extract certifications.

10. If a field is not present, return an empty list.

RESUME:

{resume_text}
"""

    result = structured_model.invoke(prompt)

    return result