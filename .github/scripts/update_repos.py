import requests
import re
import os

GITHUB_USERNAME = "jackson-lafrance"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
README_FILE = "README.md"

def get_repositories():
    """Fetch all public repositories for the user"""
    repos = []
    page = 1
    per_page = 100
    
    while True:
        url = f"https://api.github.com/users/{GITHUB_USERNAME}/repos"
        headers = {"Accept": "application/vnd.github.v3+json"}
        if GITHUB_TOKEN:
            headers["Authorization"] = f"token {GITHUB_TOKEN}"
        
        params = {
            "type": "all",
            "sort": "updated",
            "direction": "desc",
            "per_page": per_page,
            "page": page
        }
        
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        page_repos = response.json()
        if not page_repos:
            break
        
        repos.extend(page_repos)
        page += 1
        
        if len(page_repos) < per_page:
            break
    
    # Filter out the profile repo itself and sort by updated date
    repos = [repo for repo in repos if repo["name"] != GITHUB_USERNAME]
    repos.sort(key=lambda x: x["updated_at"], reverse=True)
    
    return repos

def generate_repos_section(repos):
    """Generate markdown for repositories section"""
    if not repos:
        return """## 💻 My Repositories

<div align="center">
  
  <a href="https://github.com/jackson-lafrance?tab=repositories">
    <img src="https://img.shields.io/badge/View_All_Repositories-FF6B9D?style=for-the-badge&logo=github&logoColor=white" alt="View All Repositories" />
  </a>
  
</div>
"""
    
    # Group repos into pairs for grid layout
    markdown = "## 💻 My Repositories\n\n"
    
    # Create grid layout with 2 columns
    for i in range(0, len(repos), 2):
        markdown += "<div width=\"100%\">\n"
        
        # Left repo
        repo1 = repos[i]
        repo_name1 = repo1["name"]
        repo_url1 = repo1["html_url"]
        markdown += f"  <a href=\"{repo_url1}\">\n"
        markdown += f"    <img align=\"left\" width=\"45%\" src=\"https://github-readme-stats.vercel.app/api/pin/?username={GITHUB_USERNAME}&repo={repo_name1}&theme=radical&bg_color=0D1117&title_color=FF6B9D&icon_color=FF6B9D&border_color=FF6B9D&hide_border=false\" />\n"
        markdown += "  </a>\n"
        
        # Right repo (if exists)
        if i + 1 < len(repos):
            repo2 = repos[i + 1]
            repo_name2 = repo2["name"]
            repo_url2 = repo2["html_url"]
            markdown += f"  <a href=\"{repo_url2}\">\n"
            markdown += f"    <img align=\"right\" width=\"45%\" src=\"https://github-readme-stats.vercel.app/api/pin/?username={GITHUB_USERNAME}&repo={repo_name2}&theme=radical&bg_color=0D1117&title_color=FF6B9D&icon_color=FF6B9D&border_color=FF6B9D&hide_border=false\" />\n"
            markdown += "  </a>\n"
        
        markdown += "</div>\n\n<br/>\n\n"
    
    markdown += "<div align=\"center\">\n\n"
    markdown += "  <a href=\"https://github.com/jackson-lafrance?tab=repositories\">\n"
    markdown += "    <img src=\"https://img.shields.io/badge/View_All_Repositories-FF6B9D?style=for-the-badge&logo=github&logoColor=white\" alt=\"View All Repositories\" />\n"
    markdown += "  </a>\n\n"
    markdown += "</div>\n"
    
    return markdown

def update_readme():
    """Update the README file with new repositories section"""
    with open(README_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Find and replace the repositories section
    # Match from "## 💻 My Repositories" until the next "---" or end of file
    pattern = r"## 💻 My Repositories.*?(?=\n---|\Z)"
    repos = get_repositories()
    new_section = generate_repos_section(repos)
    
    if re.search(pattern, content, re.DOTALL):
        # Replace the existing section
        content = re.sub(pattern, new_section.rstrip(), content, flags=re.DOTALL)
    else:
        # If section doesn't exist, add it before the last section
        # Find the last --- before social links
        content = re.sub(r"(---\n\n<div align=\"center\">)", new_section + "\n\n---\n\n<div align=\"center\">", content, count=1)
    
    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"Updated README with {len(repos)} repositories")

if __name__ == "__main__":
    update_readme()

