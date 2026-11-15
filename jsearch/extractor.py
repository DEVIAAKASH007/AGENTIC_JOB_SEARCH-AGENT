from models.schemas import JobSkills


def extract_job_skills(model, job_description):
    """
    Extract clean technical skills from a job description.

    Skills are divided into:
    - required_skills
    - preferred_skills
    """

    structured_model = model.with_structured_output(
        JobSkills
    )

    prompt = f"""
You are an expert technical recruiter analyzing a job description.

Your task is to extract ONLY concrete technical skills.

Separate the skills into:

1. required_skills
2. preferred_skills

============================================================
WHAT COUNTS AS A TECHNICAL SKILL
============================================================

Include things such as:

- Programming languages
  Python, Java, C++, JavaScript, TypeScript, Go

- Frameworks
  React, Django, Spring Boot, Angular

- Libraries
  TensorFlow, PyTorch, Pandas, NumPy

- Databases
  MySQL, PostgreSQL, MongoDB, Redis

- Cloud technologies
  AWS, Azure, Google Cloud

- AWS services
  EC2, S3, Lambda, ECS, EKS

- DevOps
  Docker, Kubernetes, Terraform, CI/CD

- AI / ML
  Machine Learning, Deep Learning, Generative AI,
  LLMs, NLP, Computer Vision

- Networking
  TCP/IP, HTTP, DNS, BGP

- Software technologies
  REST APIs, Microservices, Distributed Systems

============================================================
DO NOT EXTRACT
============================================================

Do NOT create vague or generic skills such as:

- software
- technology
- programming
- cloud
- coding
- development
- software systems
- software systems design tools and languages
- technical knowledge
- engineering
- computer science

If the job says something broad like:

"experience with software systems design tools and languages"

DO NOT create that entire sentence as a skill.

Instead, extract the specific technologies mentioned elsewhere
in the description.

For example:

"Strong knowledge of C++, Linux and networking"

should produce:

C++
Linux
Networking

NOT:

software systems design tools and languages

============================================================
REQUIRED VS PREFERRED
============================================================

Put a skill in required_skills when the job indicates:

- required
- must have
- mandatory
- minimum qualification
- strong experience required
- should have
- experience with

Put a skill in preferred_skills when the job indicates:

- preferred
- nice to have
- desirable
- bonus
- plus
- advantage
- good to have

If the job does not clearly distinguish them,
put concrete technical skills in required_skills.

============================================================
DUPLICATES
============================================================

Do not return duplicate skills.

For example, if the description contains:

Kubernetes
K8s

return only:

Kubernetes

If it contains:

MUI
Material UI

return only:

Material UI

If it contains:

LLM
LLMs
Large Language Models

return only:

Large Language Model

============================================================
IMPORTANT
============================================================

- Extract only skills explicitly supported by the job description.
- Do not infer technologies that are not mentioned.
- Do not turn broad phrases into skills.
- Do not invent skills.
- Do not include company names.
- Do not include job titles.
- Do not include soft skills.
- Do not include responsibilities as skills.
- Use standard technical skill names.
- Keep each skill short and specific.

============================================================
JOB DESCRIPTION
============================================================

{job_description}
"""

    result = structured_model.invoke(prompt)

    return result