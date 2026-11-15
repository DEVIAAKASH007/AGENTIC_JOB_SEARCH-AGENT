from skills.researcher import research_missing_skill


result = research_missing_skill.invoke({
    "skill": "AWS"
})


print("\n========================================")
print("       TAVILY RESEARCH")
print("========================================\n")

print(result)