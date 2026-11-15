from agent.agent import agent


# ============================================================
# CANDIDATE PROFILE
# ============================================================

candidate_profile = {
    "skills": [
        "C",
        "C++",
        "CNN",
        "CSS",
        "Deep Learning",
        "HTML",
        "JavaScript",
        "Neural Networks",
        "Python",
        "RNN",
        "SQL",
        "Scikit-learn",
        "TensorFlow",
        "Tkinter"
    ],

    "projects": [
        "EEG Freezing of Gait Detection",
        "Agentic RAG Document Intelligence Assistant",
        "Multi-Client Chat System",
        "Drone-based Hazard Detection System"
    ],

    "education": [
        "B.Tech in Artificial Intelligence"
    ]
}


# ============================================================
# MEMORY THREAD
# ============================================================

config = {
    "configurable": {
        "thread_id": "career_user_1"
    }
}


# ============================================================
# USER QUESTION
# ============================================================

question = """
Find software engineer jobs in Bangalore
and identify which jobs are suitable for me.
"""


# ============================================================
# MESSAGE TO AGENT
# ============================================================

message = f"""
Here is my candidate profile:

{candidate_profile}

My request:

{question}
"""


# ============================================================
# RUN AGENT
# ============================================================

response = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": message
            }
        ]
    },
    config=config
)


# ============================================================
# PRINT RESPONSE
# ============================================================

print("\n========================================")
print("       CAREER AGENT RESPONSE")
print("========================================\n")

print(response["messages"][-1].content)