from github.analyzer import (
    extract_username,
    get_github_repositories,
    get_readme,
    get_languages,
    get_repository_topics
)


github_url = "https://github.com/DEVIAAKASH007"


# -----------------------------------------
# 1. Extract username
# -----------------------------------------

username = extract_username(github_url)

print("Username:", username)


# -----------------------------------------
# 2. Get repositories
# -----------------------------------------

repos = get_github_repositories(username)


if isinstance(repos, dict) and "error" in repos:

    print("Error:", repos)

else:

    print("Repositories found:", len(repos))

    github_profile = []


    # -----------------------------------------
    # 3. Collect information from repositories
    # -----------------------------------------

    for repo in repos:

        repo_name = repo["name"]


        # README
        readme = get_readme(
            username,
            repo_name
        )


        # Languages
        languages = get_languages(
            username,
            repo_name
        )


        # Topics
        topics = get_repository_topics(
            username,
            repo_name
        )


        # -----------------------------------------
        # Create clean repository object
        # -----------------------------------------

        repository_data = {

            "name": repo_name,

            "description": repo["description"],

            "url": repo["html_url"],

            "languages": languages,

            "topics": topics,

            "readme": readme

        }


        github_profile.append(repository_data)


    # -----------------------------------------
    # 4. Display collected data
    # -----------------------------------------

    for repo in github_profile:

        print("\n" + "=" * 60)

        print("Repository:", repo["name"])

        print("Description:", repo["description"])

        print("URL:", repo["url"])

        print("Languages:", repo["languages"])

        print("Topics:", repo["topics"])

        print("\nREADME:")

        print(repo["readme"][:500])