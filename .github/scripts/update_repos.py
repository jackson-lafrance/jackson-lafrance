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
            "type": "all",  # Get all repos (we'll filter public ones)
            "sort": "updated",
            "direction": "desc",
            "per_page": per_page,
            "page": page
        }
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            # Check rate limit headers
            remaining = response.headers.get('X-RateLimit-Remaining', 'unknown')
            limit = response.headers.get('X-RateLimit-Limit', 'unknown')
            print(f"Rate limit: {remaining}/{limit} remaining")
            
            response.raise_for_status()
            
            page_repos = response.json()
            print(f"Page {page}: Received {len(page_repos)} repositories")
            
            if not page_repos:
                break
            
            # Only add public repos and filter out the profile repo
            for repo in page_repos:
                repo_name = repo["name"]
                is_private = repo.get("private", False)
                is_archived = repo.get("archived", False)
                
                if repo_name != GITHUB_USERNAME and not is_private and not is_archived:
                    repos.append(repo)
                    print(f"  Added: {repo_name} (public, not archived)")
                else:
                    reason = []
                    if repo_name == GITHUB_USERNAME:
                        reason.append("profile repo")
                    if is_private:
                        reason.append("private")
                    if is_archived:
                        reason.append("archived")
                    print(f"  Skipped: {repo_name} ({', '.join(reason)})")
            
            page += 1
            
            if len(page_repos) < per_page:
                break
        except Exception as e:
            print(f"Error fetching repos: {e}")
            if hasattr(e, 'response'):
                print(f"Response status: {e.response.status_code}")
                print(f"Response: {e.response.text[:200]}")
            break
    
    # Sort by updated date
    repos.sort(key=lambda x: x["updated_at"], reverse=True)
    
    print(f"\nTotal repositories found: {len(repos)}")
    for repo in repos:
        print(f"  - {repo['name']}")
    
    return repos

def generate_repos_section(repos):
    """Generate markdown for repositories section"""
    if not repos:
        return "## 💻 My Repositories\n\n_No public repositories found._\n"
    
    # Group repos into pairs for grid layout using table
    markdown = "## 💻 My Repositories\n\n"
    
    # Create grid layout with 2 columns using table
    for i in range(0, len(repos), 2):
        markdown += "<table>\n<tr>\n"
        
        # Left repo
        repo1 = repos[i]
        repo_name1 = repo1["name"]
        repo_url1 = repo1["html_url"]
        markdown += f"  <td width=\"50%\">\n"
        markdown += f"    <a href=\"{repo_url1}\">\n"
        markdown += f"      <img width=\"100%\" src=\"https://github-readme-stats.vercel.app/api/pin/?username={GITHUB_USERNAME}&repo={repo_name1}&theme=radical&bg_color=0D1117&title_color=FF6B9D&icon_color=FF6B9D&border_color=FF6B9D&hide_border=false\" />\n"
        markdown += "    </a>\n"
        markdown += "  </td>\n"
        
        # Right repo (if exists)
        if i + 1 < len(repos):
            repo2 = repos[i + 1]
            repo_name2 = repo2["name"]
            repo_url2 = repo2["html_url"]
            markdown += f"  <td width=\"50%\">\n"
            markdown += f"    <a href=\"{repo_url2}\">\n"
            markdown += f"      <img width=\"100%\" src=\"https://github-readme-stats.vercel.app/api/pin/?username={GITHUB_USERNAME}&repo={repo_name2}&theme=radical&bg_color=0D1117&title_color=FF6B9D&icon_color=FF6B9D&border_color=FF6B9D&hide_border=false\" />\n"
            markdown += "    </a>\n"
            markdown += "  </td>\n"
        else:
            markdown += "  <td width=\"50%\"></td>\n"
        
        markdown += "</tr>\n</table>\n\n"
    
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

