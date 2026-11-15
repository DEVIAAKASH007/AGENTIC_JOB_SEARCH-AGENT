import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model

from candidate.loader import load_candidate_profile
from jobs.analyzer import create_job_matching_tool

from skills.researcher import research_missing_skill


# ============================================================
# LOAD ENVIRONMENT
# ============================================================

load_dotenv()


# ============================================================
# GEMINI
# ============================================================

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)

model = init_chat_model(
    "google_genai:gemini-3.5-flash-lite",
    api_key=GEMINI_API_KEY
)


# ============================================================
# LOAD CANDIDATE
# ============================================================

print("\n========================================")
print("      LOADING CANDIDATE PROFILE")
print("========================================")


candidate_profile = load_candidate_profile(
    resume_path="resume.pdf",
    github_url="https://github.com/DEVIAAKASH007"
)


candidate_skills = candidate_profile[
    "skills"
]


print("\nCandidate skills loaded:")

for skill in candidate_skills:

    print(
        "-",
        skill
    )


# ============================================================
# JOB MATCHING TOOL
# ============================================================

find_and_match_jobs = create_job_matching_tool(
    model=model,
    candidate_skills=candidate_skills
)


# ============================================================
# SYSTEM PROMPT
# ============================================================
system_prompt = """
You are an intelligent Career Agent.

The candidate's Resume and GitHub profile have already
been analyzed.

The candidate's skills are already available through
the job matching tool.

NEVER ask the candidate to manually provide their skills.


============================================================
AVAILABLE TOOLS
============================================================

You have exactly two tools.

1. find_and_match_jobs

Use this tool to:

- Search current jobs
- Compare jobs with the candidate profile
- Calculate match percentages
- Find matched skills
- Find missing skills

2. research_missing_skill

Use this tool to:

- Research a technical skill
- Find learning resources
- Find tutorials
- Find official documentation
- Find hands-on learning resources

IMPORTANT:

When the user explicitly asks for learning resources,
tutorials, documentation, or what to learn, you MUST
call research_missing_skill.

Do NOT generate learning resources from your own knowledge
when the research_missing_skill tool can provide them.


============================================================
JOB SEARCH
============================================================

If the user asks:

"Find software engineer jobs in Bangalore"

call:

find_and_match_jobs

Then present the jobs ranked by match percentage.


============================================================
JOB + LEARNING REQUEST
============================================================

If the user asks something like:

"Find jobs and tell me what skills I should learn."

First:

1. Call find_and_match_jobs.

Then:

2. Examine the missing skills from the returned jobs.

3. Identify the most important missing technical skills.

Prioritize skills that:

- Appear in multiple jobs
- Are important requirements
- Can significantly improve the candidate's match

Then:

4. Call research_missing_skill for the selected skills.

IMPORTANT:

You MUST actually call research_missing_skill.

Do not simply create a list of learning resources
from your own knowledge.


============================================================
LEARNING RESOURCE REQUEST
============================================================

If the user asks:

"What should I learn?"

"How can I improve my chances?"

"Give me resources for AWS."

"How do I learn Docker?"

"Give me tutorials for Kubernetes."

Then:

- Identify the relevant missing skill.
- Call research_missing_skill.
- Use the returned search results in the final answer.


============================================================
TAVILY RESULT HANDLING
============================================================

When research_missing_skill returns results:

Prefer:

1. Official documentation
2. Official training platforms
3. Official tutorials
4. Reliable technical resources
5. Community resources

Clearly distinguish official resources from community
resources when possible.

Do not invent URLs.


============================================================
IMPORTANT
============================================================

Do not call research_missing_skill unnecessarily.

For example, if the user only asks:

"Find software engineer jobs in Bangalore."

Only call:

find_and_match_jobs

If the user asks:

"Find jobs and tell me what I should learn."

Call BOTH tools.


============================================================
FINAL RESPONSE
============================================================

Keep responses concise and structured.

For job searches show:

- Job title
- Company
- Location
- Match percentage
- Matched skills
- Missing skills
- Job link

For learning requests show:

- Skill
- Why it matters
- Recommended resources
- Resource URLs
"""

# ============================================================
# CREATE AGENT
# ============================================================

agent = create_agent(
    model=model,
    tools=[
        find_and_match_jobs,
        research_missing_skill
    ],
    system_prompt=system_prompt
)

# ============================================================
# USER QUERY
# ============================================================

user_query = """
Find software engineer jobs in Bangalore and
research the most important missing skills for me.
Give me useful learning resources.
"""


# ============================================================
# RUN AGENT
# ============================================================

response = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": user_query
            }
        ]
    }
)


# ============================================================
# FINAL RESPONSE
# ============================================================

print("\n========================================")
print("       CAREER AGENT RESPONSE")
print("========================================\n")


print(
    response["messages"][-1].content
)