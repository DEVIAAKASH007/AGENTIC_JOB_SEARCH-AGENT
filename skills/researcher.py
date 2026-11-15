import os

from dotenv import load_dotenv
from langchain.tools import tool
from langchain_tavily import TavilySearch


load_dotenv()


# ============================================================
# TAVILY
# ============================================================

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")


tavily = TavilySearch(
    max_results=5,
    topic="general",
    tavily_api_key=TAVILY_API_KEY
)


# ============================================================
# RESEARCH MISSING SKILL
# ============================================================

@tool
def research_missing_skill(skill: str) -> str:
    """
    Search the web for reliable learning resources
    for a missing technical skill.
    """

    query = f"""
    Best resources to learn {skill} for software engineers.
    Prefer official documentation, official tutorials,
    hands-on labs, and reliable learning resources.
    """

    result = tavily.invoke({
        "query": query
    })


    # ========================================================
    # FORMAT RESULTS
    # ========================================================

    results = result.get(
        "results",
        []
    )


    if not results:

        return (
            f"No useful learning resources found "
            f"for {skill}."
        )


    output = []

    output.append(
        f"Learning resources for {skill}:"
    )


    for index, item in enumerate(
        results,
        start=1
    ):

        title = item.get(
            "title",
            "Untitled"
        )

        url = item.get(
            "url",
            ""
        )

        content = item.get(
            "content",
            ""
        )


        # Keep description short
        if len(content) > 300:

            content = (
                content[:300]
                + "..."
            )


        output.append(
            f"""
{index}. {title}

URL: {url}

Description:
{content}
"""
        )


    return "\n".join(output)