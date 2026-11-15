from jsearch.search import search_jobs


jobs = search_jobs.invoke({
    "skill": "software engineer",
    "location": "Bangalore"
})


print("\n===== JOB RESULTS =====")

print("Number of jobs:", len(jobs))


for job in jobs:

    if "error" in job:

        print("\nERROR:")
        print(job)

        continue

    print("\n" + "=" * 60)

    print("Title:")
    print(job.get("job_title"))

    print("\nCompany:")
    print(job.get("company_name"))

    print("\nLocation:")
    print(job.get("location"))

    print("\nDescription:")

    description = job.get("job_description")

    if description:
        print(description[:1000])
    else:
        print("No description available")

    print("\nApply Link:")
    print(job.get("job_link"))