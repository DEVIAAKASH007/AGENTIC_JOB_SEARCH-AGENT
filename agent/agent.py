import os

from dotenv import load_dotenv

from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain_tavily import TavilySearch
from langgraph.checkpoint.memory import InMemorySaver

from jsearch.search import search_jobs
from matcher.matcher import match_job


load_dotenv()


# ============================================================
# API KEYS
# ============================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")


# ============================================================
# CHECK API KEYS
# ============================================================

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is missing from .env")

if not TAVILY_API_KEY:
    raise ValueError("TAVILY_API_KEY is missing from .env")


# ============================================================
# LLM
# ============================================================

model = init_chat_model(
    "google_genai:gemini-2.5-flash",
    api_key=GEMINI_API_KEY
)


# ============================================================
# TAVILY
# ============================================================

# TavilySearch is already a LangChain tool.
# Therefore, we do NOT use @tool here.

tavily_search = TavilySearch(
    max_results=5,
    search_depth="advanced",
    tavily_api_key=TAVILY_API_KEY
)


# ============================================================
# MEMORY
# ============================================================

checkpointer = InMemorySaver()


# ============================================================
# SYSTEM PROMPT
# ============================================================

system_prompt = """
You are a Career Agent.

Your job is to help users:

1. Find relevant job openings.
2. Analyze job requirements.
3. Compare jobs with the candidate's skills.
4. Calculate job match percentage.
5. Identify matched skills.
6. Identify missing skills.
7. Find learning resources for missing skills.

You have access to these tools:

------------------------------------------------------------
search_jobs
------------------------------------------------------------

Use this tool when the user asks for current job openings.

It searches JSearch for jobs based on skill and location.

------------------------------------------------------------
match_job
------------------------------------------------------------

Use this tool when comparing candidate skills
against required job skills.

The tool returns:

- match_percentage
- matched_skills
- missing_skills

IMPORTANT:
Do NOT calculate the match percentage yourself.

Always use match_job for job matching.

------------------------------------------------------------
TavilySearch
------------------------------------------------------------

Use this tool when the user needs current web
information or learning resources.

For example:

- tutorials
- documentation
- courses
- learning resources
- current technology information

------------------------------------------------------------
CANDIDATE PROFILE
------------------------------------------------------------

When a candidate profile is provided, use it when
evaluating jobs.

Do not invent candidate skills.

Do not invent job requirements.

If required job skills are available, use match_job.

If job requirements are not explicitly available,
explain that the match cannot be calculated reliably.

------------------------------------------------------------
RESPONSE STYLE
------------------------------------------------------------

Give clear and concise answers.

When presenting a job match, use:

Job:
Company:
Location:

Match Percentage:

Matched Skills:
- skill

Missing Skills:
- skill

If the user asks about missing skills,
use TavilySearch to find useful resources.
"""


# ============================================================
# CREATE CAREER AGENT
# ============================================================

agent = create_agent(
    model=model,

    tools=[
        search_jobs,
        match_job,
        tavily_search
    ],

    system_prompt=system_prompt,

    checkpointer=checkpointer
)