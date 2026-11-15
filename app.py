import os
import re
import gradio as gr
from dotenv import load_dotenv

from langchain.chat_models import init_chat_model
from langchain.agents import create_agent

from candidate.loader import load_candidate_profile
from jobs.analyzer import create_job_matching_tool, analyze_jobs
from skills.researcher import research_missing_skill
from matcher.normalizer import normalize_skill, normalize_skills
from matcher.semantic_matcher import semantic_skill_match
from matcher.matcher import calculate_weighted_match, _semantic_match

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

model = init_chat_model(
    "google_genai:gemini-3.5-flash-lite",
    api_key=GEMINI_API_KEY
)

# Global candidate and session state (Initialized EMPTY - NO hardcoded skills)
current_candidate_data = {
    "profile": None,
    "skills": [],
    "profile_loaded": False,
    "current_location": None,
    "current_role": "software engineer"
}


def reset_candidate():
    """
    Completely reset all candidate state.
    Guarantees User B never inherits User A's profile if extraction fails or new upload begins.
    """
    current_candidate_data["profile"] = None
    current_candidate_data["skills"] = []
    current_candidate_data["profile_loaded"] = False


def load_profile_action(pdf_file, github_url):
    """
    Reset previous candidate, extract new resume and GitHub data,
    and update candidate state.
    """
    reset_candidate()

    if pdf_file is None:
        return "⚠️ Please select a valid resume PDF file.", "", "❌ No profile loaded"

    resume_path = pdf_file.name if hasattr(pdf_file, "name") else pdf_file

    if not github_url or not github_url.strip():
        github_url = "https://github.com/DEVIAAKASH007"

    try:
        profile = load_candidate_profile(
            resume_path=resume_path,
            github_url=github_url
        )

        if not profile or not profile.get("skills"):
            reset_candidate()
            return "❌ Failed to extract skills from the provided profile.", "", "❌ Extraction Failed"

        current_candidate_data["profile"] = profile
        current_candidate_data["skills"] = profile.get("skills", [])
        current_candidate_data["profile_loaded"] = True

        skills_list = profile.get("skills", [])
        skills_str = ", ".join(skills_list)

        # Format GitHub evidence breakdown cleanly
        github_evidence = profile.get("github_evidence", [])
        evidence_md = ""
        if github_evidence:
            for item in github_evidence:
                evidence_md += f"- **{item['skill']}** (Confidence: `{item.get('confidence', 'medium')}` | Score: `{item.get('score', 0)}`)\n  - Evidence: {item['evidence']}\n"
        else:
            evidence_md = "No additional medium/low confidence skills kept as evidence."

        projects = "\n".join([f"- {p}" for p in profile.get("resume_projects", [])]) or "None"
        education = "\n".join([f"- {e}" for e in profile.get("education", [])]) or "None"

        summary_md = f"""### ✅ Unified Profile Loaded Successfully!

**Primary Candidate Skills ({len(skills_list)}):**
`{skills_str}`

---

#### 📁 Resume Projects:
{projects}

#### 🎓 Education:
{education}

#### 🔍 GitHub Supporting Evidence:
{evidence_md}
"""
        status_msg = f"✅ Profile Active ({len(skills_list)} skills loaded)"
        return summary_md, skills_str, status_msg

    except Exception as e:
        reset_candidate()
        return f"❌ Error extracting profile: {str(e)}", "", "❌ Error loading profile"


def find_jobs_action(skill_query, location_query, custom_skills_str):
    """
    Search and rank jobs. Enforces profile-required check and respects requested location.
    """
    if not current_candidate_data["profile_loaded"] and not (custom_skills_str and custom_skills_str.strip()):
        return (
            "⚠️ **Profile Required**: Please upload your resume and provide your GitHub profile in the "
            "**'📄 Candidate Profile & GitHub'** tab so I can analyze your skills and match jobs accurately.",
            ""
        )

    if custom_skills_str and custom_skills_str.strip():
        candidate_skills = [s.strip() for s in custom_skills_str.split(",") if s.strip()]
    else:
        candidate_skills = current_candidate_data["skills"]

    # Respect user location
    if location_query and location_query.strip():
        loc = location_query.strip()
        current_candidate_data["current_location"] = loc
    elif current_candidate_data["current_location"]:
        loc = current_candidate_data["current_location"]
    else:
        loc = "Bangalore"

    if skill_query and skill_query.strip():
        role = skill_query.strip()
        current_candidate_data["current_role"] = role
    else:
        role = current_candidate_data["current_role"]

    try:
        results = analyze_jobs(
            model=model,
            candidate_skills=candidate_skills,
            skill=role,
            location=loc
        )

        if not results:
            return f"No jobs found for **{role}** in **{loc}**.", ""

        if isinstance(results[0], dict) and "error" in results[0]:
            return f"❌ JSearch Error: {results[0]}", ""

        cards_md = f"## 💼 Ranked Job Matches for '{role}' in {loc}\n\n"
        missing_skills_counter = {}

        for idx, job in enumerate(results, start=1):
            status = job.get("status", "OK")
            score = job.get("match_percentage", 0)

            if status == "INSUFFICIENT_JOB_SKILL_DATA":
                score_badge = "⚠️ **Insufficient Job Skill Data**"
            elif score >= 50:
                score_badge = f"🟢 **Skill Match Score: {score}%**"
            elif score >= 20:
                score_badge = f"🟡 **Skill Match Score: {score}%**"
            else:
                score_badge = f"🔴 **Skill Match Score: {score}%**"

            matched_req = ", ".join(job.get("matched_required_skills", [])) or "_None_"
            missing_req = ", ".join(job.get("missing_required_skills", [])) or "_None_"
            matched_pref = ", ".join(job.get("matched_preferred_skills", [])) or "_None_"
            missing_pref = ", ".join(job.get("missing_preferred_skills", [])) or "_None_"

            # Missing required skills tracking
            for s in job.get("missing_required_skills", []):
                missing_skills_counter[s] = missing_skills_counter.get(s, 0) + 1

            explanation = job.get("score_explanation", {})
            req_ratio = explanation.get("required_ratio", "N/A")
            pref_ratio = explanation.get("preferred_ratio", "N/A")

            cards_md += f"""### {idx}. {job.get('job_title')} — {job.get('company_name')}
- **Location:** 📍 {job.get('location')}
- **Score:** {score_badge}
- **Score Breakdown:** Required Matched: `{req_ratio}` (80% weight) | Preferred Matched: `{pref_ratio}` (20% weight)
- **Required Skills:**
  - ✅ Matched: `{matched_req}`
  - ❌ Missing: `{missing_req}`
- **Preferred Skills:**
  - ✅ Matched: `{matched_pref}`
  - ❌ Missing: `{missing_pref}`
- 🔗 **[Apply / View Posting]({job.get('job_link', '#')})**

---
"""

        sorted_missing = sorted(missing_skills_counter.items(), key=lambda x: x[1], reverse=True)[:5]
        gap_md = "### 📈 High-Frequency Skill Gaps Across Jobs\n"
        for sk, count in sorted_missing:
            gap_md += f"- **{sk.title()}**: Required in {count} job(s)\n"

        return cards_md, gap_md

    except Exception as e:
        return f"❌ Error searching/matching jobs: {str(e)}", ""


def build_career_agent():
    """Build Career Agent tool pipeline."""
    candidate_skills = current_candidate_data["skills"]

    find_and_match_jobs = create_job_matching_tool(
        model=model,
        candidate_skills=candidate_skills
    )

    system_prompt = """
You are an intelligent, professional Career Agent.

RULES:
1. PROFILE CHECK: If the user asks for suitable jobs, matching positions, or recommendations and no profile has been loaded yet, inform them politely:
   "Please upload your resume and provide your GitHub profile so I can analyze your skills and find suitable jobs."
2. LOCATION RESPECT: Strictly preserve the location requested by the user (e.g. Bangalore, Hyderabad, Chennai). Never force Bangalore if another location was asked.
3. CLEAR FORMATTING: Present job scores as "Skill Match Score: XX%" (never call it hiring probability or chance of getting hired). Show exact matched and missing required/preferred skills cleanly.
4. LEARNING RESOURCES: When asked for tutorials or learning resources, call research_missing_skill to get official links and documentation via Tavily.
"""

    return create_agent(
        model=model,
        tools=[find_and_match_jobs, research_missing_skill],
        system_prompt=system_prompt
    )


def agent_chat_fn(user_message, chat_history):
    """Handle conversational turn with Career Agent."""
    if not user_message or not user_message.strip():
        return "", chat_history

    if chat_history is None:
        chat_history = []

    # Check if profile is loaded when user asks for matching/jobs
    lower_msg = user_message.lower()
    if not current_candidate_data["profile_loaded"] and any(kw in lower_msg for kw in ["my profile", "suitable for me", "match my resume", "jobs for me", "can i apply"]):
        prompt_msg = "Please upload your resume and provide your GitHub profile in the **'📄 Candidate Profile & GitHub'** tab so I can analyze your skills and find suitable jobs for you."
        chat_history.append({"role": "user", "content": user_message})
        chat_history.append({"role": "assistant", "content": prompt_msg})
        return "", chat_history

    # Parse and update location memory from query
    for city in ["hyderabad", "bangalore", "bengaluru", "chennai", "mumbai", "pune", "delhi", "gurgaon", "noida", "remote"]:
        if city in lower_msg:
            current_candidate_data["current_location"] = city.capitalize()
            break

    agent = build_career_agent()

    try:
        messages = []
        for item in chat_history:
            if isinstance(item, dict):
                messages.append({
                    "role": item.get("role", "user"),
                    "content": item.get("content", "")
                })

        messages.append({"role": "user", "content": user_message})

        response = agent.invoke({"messages": messages})
        last_msg = response["messages"][-1].content

        if isinstance(last_msg, list):
            agent_text = "".join([part.get("text", "") for part in last_msg if isinstance(part, dict)])
        else:
            agent_text = str(last_msg)

        chat_history.append({"role": "user", "content": user_message})
        chat_history.append({"role": "assistant", "content": agent_text})
        return "", chat_history

    except Exception as e:
        chat_history.append({"role": "user", "content": user_message})
        chat_history.append({"role": "assistant", "content": f"❌ Error: {str(e)}"})
        return "", chat_history


def test_normalizer_fn(skill_input):
    if not skill_input:
        return "Please enter a skill name."
    norm = normalize_skill(skill_input)
    return f"Input: **{skill_input}**  ➔  Normalized: **`{norm}`**"


def test_semantic_fn(skill_a, skill_b, threshold):
    if not skill_a or not skill_b:
        return "Please enter both skills."
    match = _semantic_match(skill_a, skill_b, threshold=float(threshold))
    status = "✅ MATCH (Equivalent/Compatible)" if match else "❌ NO MATCH (Distinct / Incompatible)"
    return f"**{skill_a}** ↔ **{skill_b}**\n\nResult: {status}"


# ============================================================
# GRADIO UI DEFINITION
# ============================================================

custom_css = """
.gradio-container {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    max-width: 1200px !important;
    margin: 0 auto;
}
.header-box {
    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
    color: white;
    padding: 24px;
    border-radius: 12px;
    margin-bottom: 20px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}
"""

with gr.Blocks(title="Career Agent AI") as demo:
    with gr.Row():
        gr.HTML("""
        <div class="header-box">
            <h1 style="margin:0; font-size: 28px;">🚀 Career Agent AI</h1>
            <p style="margin:5px 0 0 0; opacity: 0.9; font-size: 15px;">
                Intelligent Career Assistant • Resume & GitHub Skills Extraction • JSearch Real-Time Job Matching • Semantic Gap Analysis
            </p>
        </div>
        """)

    with gr.Tabs():
        # TAB 1: Chat Assistant
        with gr.Tab("💬 Career Agent Chat"):
            chatbot = gr.Chatbot(
                height=520,
                label="Conversation"
            )
            with gr.Row():
                chat_input = gr.Textbox(
                    placeholder="E.g., 'Find Python jobs in Hyderabad and research the most important missing skills for me'",
                    label="Ask Career Agent",
                    scale=8
                )
                send_btn = gr.Button("Send 🚀", variant="primary", scale=1)

            gr.Examples(
                examples=[
                    "Find software engineer jobs in Hyderabad and research missing skills for me.",
                    "Show Python jobs in Bangalore.",
                    "What official documentation and tutorials exist for Docker and Kubernetes?",
                    "Give me learning resources for AWS."
                ],
                inputs=chat_input
            )

            send_btn.click(agent_chat_fn, inputs=[chat_input, chatbot], outputs=[chat_input, chatbot])
            chat_input.submit(agent_chat_fn, inputs=[chat_input, chatbot], outputs=[chat_input, chatbot])

        # TAB 2: Job Search & Weighted Matching
        with gr.Tab("🔍 Job Search & Matcher"):
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("### ⚙️ Search Criteria")
                    job_query = gr.Textbox(label="Skill / Role", value="software engineer")
                    location_query = gr.Textbox(label="Location", value="Bangalore")
                    candidate_skills_box = gr.Textbox(
                        label="Active Candidate Skills",
                        value="",
                        placeholder="Upload resume in Tab 3 or type custom skills here...",
                        lines=3
                    )
                    search_jobs_btn = gr.Button("Find & Rank Jobs 🎯", variant="primary")
                    skill_gap_output = gr.Markdown(label="Skill Gap Analysis")

                with gr.Column(scale=2):
                    gr.Markdown("### 📊 Ranked Match Results")
                    jobs_output = gr.Markdown("Upload your resume in Tab 3 or enter skills to search live positions.")

            search_jobs_btn.click(
                find_jobs_action,
                inputs=[job_query, location_query, candidate_skills_box],
                outputs=[jobs_output, skill_gap_output]
            )

        # TAB 3: Candidate Profile Loader
        with gr.Tab("📄 Candidate Profile & GitHub"):
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("### 📥 Profile Input")
                    pdf_input = gr.File(label="Upload Resume (PDF)", file_types=[".pdf"])
                    github_input = gr.Textbox(
                        label="GitHub Profile URL",
                        value="https://github.com/DEVIAAKASH007"
                    )
                    load_btn = gr.Button("Extract & Build Unified Profile ⚡", variant="primary")
                    profile_status_box = gr.Markdown("❌ No Profile Loaded")

                with gr.Column(scale=2):
                    gr.Markdown("### 📋 Unified Profile Details")
                    profile_output = gr.Markdown("Upload a resume and click extract to load candidate skills dynamically.")

            load_btn.click(
                load_profile_action,
                inputs=[pdf_input, github_input],
                outputs=[profile_output, candidate_skills_box, profile_status_box]
            )

        # TAB 4: Normalizer & Semantic Matching Playground
        with gr.Tab("🧪 Skill Normalizer & Semantic Lab"):
            gr.Markdown("### 🔄 Skill Normalization Playground")
            with gr.Row():
                norm_input = gr.Textbox(label="Skill Name / Alias", placeholder="e.g. JavaScript (Basic), K8s, React.js, sklearn")
                norm_btn = gr.Button("Normalize", scale=0)
                norm_output = gr.Markdown()

            norm_btn.click(test_normalizer_fn, inputs=norm_input, outputs=norm_output)

            gr.Markdown("---")
            gr.Markdown("### 🧠 Semantic Matcher & Guard Rules Playground")
            with gr.Row():
                skill1 = gr.Textbox(label="Candidate Skill", value="AWS EC2")
                skill2 = gr.Textbox(label="Job Skill", value="Amazon EC2")
                sim_threshold = gr.Slider(minimum=0.5, maximum=1.0, value=0.8, step=0.05, label="Cosine Similarity Threshold")
                sem_btn = gr.Button("Test Match", scale=0)

            sem_output = gr.Markdown()
            sem_btn.click(test_semantic_fn, inputs=[skill1, skill2, sim_threshold], outputs=sem_output)

if __name__ == "__main__":
    demo.launch(
        server_name="127.0.0.1",
        server_port=7861,
        theme=gr.themes.Soft(),
        css=custom_css,
        share=False
    )
