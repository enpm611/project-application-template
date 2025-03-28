import requests
import json
import time
import os
import sys
from datetime import datetime

"""
Script to fetch all issues from the python-poetry/poetry repository using GitHub API.
This script requires a GitHub personal access token with the 'repo' scope.
"""

# GitHub API configuration
REPO_OWNER = "python-poetry"
REPO_NAME = "poetry"
PER_PAGE = 100  # Maximum allowed by GitHub API
OUTPUT_FILE = "poetry_data.json"

# GitHub API endpoints
ISSUES_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues"
TIMELINE_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues/{{issue_number}}/timeline"

def get_github_token():
    """Get GitHub token from environment variable or prompt user"""
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        token = input("Enter your GitHub personal access token: ")
    return token

def check_rate_limit(headers, response=None):
    """Check GitHub API rate limit and wait if necessary
    
    Returns True if we had to wait, False otherwise
    """
    # If we have a response, use its headers
    if response and 'X-RateLimit-Remaining' in response.headers:
        remaining = int(response.headers['X-RateLimit-Remaining'])
        reset_time = int(response.headers['X-RateLimit-Reset'])
        print(f"Rate limit status: {remaining} requests remaining")
    else:
        # Otherwise make a request to check rate limit
        rate_limit_url = "https://api.github.com/rate_limit"
        rate_response = requests.get(rate_limit_url, headers=headers)
        if rate_response.status_code != 200:
            print(f"Error checking rate limit: {rate_response.status_code}")
            return False
            
        rate_data = rate_response.json()
        remaining = rate_data['resources']['core']['remaining']
        reset_time = rate_data['resources']['core']['reset']
        print(f"Rate limit status: {remaining} requests remaining")
    
    # If we're close to the limit, wait until reset
    if remaining < 20:  # Buffer to prevent hitting the limit
        current_time = int(time.time())
        wait_time = reset_time - current_time + 5  # Add 5 seconds buffer
        if wait_time > 0:
            print(f"Rate limit nearly exceeded ({remaining} remaining). Waiting for {wait_time} seconds...")
            time.sleep(wait_time)
            return True
    
    return False

def fetch_all_issues(token, output_file=None):
    """Fetch all issues from the repository and optionally write directly to file"""
    all_issues = []
    issue_count = 0
    page = 1
    
    # If writing directly to file, initialize the file
    file_handle = None
    if output_file:
        file_handle = open(output_file, 'w', encoding='utf-8')
        file_handle.write('[\n')  # Start JSON array
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    print(f"Fetching issues from {REPO_OWNER}/{REPO_NAME}...")
    
    # Initial rate limit check
    check_rate_limit(headers)
    
    while True:
        # Fetch a page of issues
        params = {
            "state": "all",  # Get both open and closed issues
            "per_page": PER_PAGE,
            "page": page
        }
        
        # Check rate limit before making the request
        check_rate_limit(headers)
        
        response = requests.get(ISSUES_URL, headers=headers, params=params, stream=True)
        
        # Check for rate limiting
        if response.status_code == 403:
            if 'X-RateLimit-Remaining' in response.headers and int(response.headers['X-RateLimit-Remaining']) == 0:
                reset_time = int(response.headers['X-RateLimit-Reset'])
                wait_time = reset_time - int(time.time()) + 5  # Add 5 seconds buffer
                print(f"Rate limit exceeded. Waiting for {wait_time} seconds...")
                time.sleep(wait_time)
                continue
            else:
                print(f"Access forbidden (403). Headers: {dict(response.headers)}")
                print(f"Response body: {response.text}")
                sys.exit(1)
        
        # Check for other errors
        if response.status_code != 200:
            print(f"Error fetching issues: {response.status_code}")
            print(response.text)
            break
        
        # Process response in chunks to avoid memory issues
        response_text = ''
        for chunk in response.iter_content(chunk_size=8192, decode_unicode=True):
            if chunk:
                response_text += chunk
        
        issues = json.loads(response_text)
        
        # Break if no more issues
        if not issues:
            break
        
        print(f"Fetched page {page} with {len(issues)} issues")
        
        # Process each issue
        for issue in issues:
            # Skip pull requests (they're also returned by the issues endpoint)
            if "pull_request" in issue:
                continue
                
            # Extract relevant issue data
            issue_data = {
                "url": issue["html_url"],
                "creator": issue["user"]["login"],
                "labels": [label["name"] for label in issue["labels"]],
                "state": issue["state"],
                "assignees": [assignee["login"] for assignee in issue["assignees"]],
                "title": issue["title"],
                "text": issue["body"],
                "number": issue["number"],
                "created_date": issue["created_at"],
                "updated_date": issue["updated_at"],
                "timeline_url": issue["timeline_url"],
                "events": []
            }
            
            # Fetch timeline events for this issue
            issue_data["events"] = fetch_issue_timeline(token, issue["number"])
            
            # If writing directly to file
            if file_handle:
                # Add comma if not the first issue
                if issue_count > 0:
                    file_handle.write(',\n')
                
                # Convert to JSON and write in chunks
                issue_json = json.dumps(issue_data, indent=2)
                for j in range(0, len(issue_json), 8192):
                    chunk = issue_json[j:j+8192]
                    file_handle.write(chunk)
                
                issue_count += 1
            else:
                # Otherwise add to in-memory list
                all_issues.append(issue_data)
            
            # Small delay to avoid hitting rate limits
            time.sleep(0.5)  # Increased from 0.1 to be more conservative
        
        # Move to next page
        page += 1
        
        # Small delay between pages
        time.sleep(2)  # Increased from 1 to be more conservative
    
    # Close file handle if it was opened
    if file_handle:
        file_handle.write('\n]')  # End JSON array
        file_handle.close()
        return issue_count
    else:
        return all_issues

def fetch_issue_timeline(token, issue_number):
    """Fetch timeline events for a specific issue"""
    events = []
    page = 1
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.mockingbird-preview+json"  # Timeline API requires this preview header
    }
    
    # Check rate limit before starting
    check_rate_limit(headers)
    
    while True:
        # Fetch a page of timeline events
        params = {
            "per_page": PER_PAGE,
            "page": page
        }
        
        # Check rate limit before making the request
        check_rate_limit(headers)
        
        url = TIMELINE_URL.format(issue_number=issue_number)
        response = requests.get(url, headers=headers, params=params, stream=True)
        
        # Check for rate limiting
        if response.status_code == 403:
            if 'X-RateLimit-Remaining' in response.headers and int(response.headers['X-RateLimit-Remaining']) == 0:
                reset_time = int(response.headers['X-RateLimit-Reset'])
                wait_time = reset_time - int(time.time()) + 5  # Add 5 seconds buffer
                print(f"Rate limit exceeded. Waiting for {wait_time} seconds...")
                time.sleep(wait_time)
                continue
            else:
                print(f"Access forbidden (403) for issue #{issue_number}. Headers: {dict(response.headers)}")
                print(f"Response body: {response.text}")
                return events  # Return what we have so far
        
        # Check for other errors
        if response.status_code != 200:
            print(f"Error fetching timeline for issue #{issue_number}: {response.status_code}")
            break
        
        # Process response in chunks to avoid memory issues
        response_text = ''
        for chunk in response.iter_content(chunk_size=8192, decode_unicode=True):
            if chunk:
                response_text += chunk
        
        timeline_events = json.loads(response_text)
        
        # Break if no more events
        if not timeline_events:
            break
        
        # Process each event
        for event in timeline_events:
            event_data = {
                "event_type": event["event"],
                "author": event["actor"]["login"] if "actor" in event and event["actor"] is not None else None,
                "event_date": event["created_at"] if "created_at" in event else None,
            }
            
            # Add label for labeled/unlabeled events
            if event["event"] in ["labeled", "unlabeled"] and "label" in event:
                event_data["label"] = event["label"]["name"]
            
            # Add comment text for commented events
            if event["event"] == "commented" and "body" in event:
                event_data["comment"] = event["body"]
            
            events.append(event_data)
        
        # Move to next page
        page += 1
        
        # Small delay between pages
        time.sleep(1)  # Increased from 0.5 to be more conservative
    
    return events

def write_json_in_chunks(data, file_path, chunk_size=8192):
    """Write JSON data to a file in chunks to avoid memory issues"""
    with open(file_path, 'w', encoding='utf-8') as f:
        # Start the JSON array
        f.write('[\n')
        
        # Write each item in the array
        for i, item in enumerate(data):
            # Convert item to JSON string
            if i > 0:
                f.write(',\n')
            
            # Convert the item to a JSON string
            item_json = json.dumps(item, indent=2)
            
            # Write the item JSON in chunks
            for j in range(0, len(item_json), chunk_size):
                chunk = item_json[j:j+chunk_size]
                f.write(chunk)
        
        # End the JSON array
        f.write('\n]')

def main():
    # Get GitHub token
    token = get_github_token()
    
    # Fetch all issues and write directly to file
    start_time = time.time()
    issue_count = fetch_all_issues(token, OUTPUT_FILE)
    end_time = time.time()
    
    print(f"\nFetched {issue_count} issues in {end_time - start_time:.2f} seconds")
    print(f"Data saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
