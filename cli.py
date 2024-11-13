import os
import subprocess
import sys
import git
from anthropic import Anthropic
import argparse

def get_staged_diff():
    """
    Retrieves the diff of staged files in the current Git repository.
    """
    try:
        repo = git.Repo(".")
        diff = repo.git.diff("--cached")
        return diff
    except git.exc.InvalidGitRepositoryError:
        print("Error: Not a valid Git repository.")
        return None
    
def get_conventional_commit_prompt(diff):
    """Create a prompt for Claude to generate a conventional commit message."""
    with open('prompt.txt', 'r') as file:
        prompt = file.read()
    return f"""{prompt}
Here's the diff:
{diff}

Return only the commit message without any additional explanation."""


def generate_commit_message(diff, api_key=None):
    """Generate a commit message using Claude API."""
    if not api_key:
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            print("Error: ANTHROPIC_API_KEY not found in environment variables")
            sys.exit(1)
    
    client = Anthropic(api_key=api_key)
    
    try:
        message = client.messages.create(
            model="claude-2.1",
            max_tokens=300,
            temperature=0.7,
            system="You are a helpful assistant that generates clear and concise git commit messages.",
            messages=[{
                "role": "user",
                "content": get_conventional_commit_prompt(diff)
            }]
        )
        return message.content[0].text
    except Exception as e:
        print(f"Error generating commit message: {str(e)}")
        sys.exit(1)



def main():
    """Main function to handle command-line interface."""
    parser = argparse.ArgumentParser(description="Generate a conventional commit message for staged changes.")
    parser.add_argument("--api-key", help="Anthropic API key", default=os.getenv('ANTHROPIC_API_KEY'))
    parser.add_argument('--dry-run', action='store_true', help='Show the message without committing')
    args = parser.parse_args()

    try:
        # Check if there are staged changes
        status = subprocess.run(
            ['git', 'diff', '--cached', '--quiet'],
            capture_output=True
        )
        
        if status.returncode == 0:
            print("No changes staged for commit")
            sys.exit(1)
        
        # Get and analyze the diff
        diff = get_staged_diff()
        message = generate_commit_message(diff, args.api_key)

        # Print the generated message
        print("\nGenerated commit message:")
        print("-" * 50)
        print(message)
        print("-" * 50)
        
        if args.dry_run:
            print("\nDry run - not committing changes")
            sys.exit(0)

        # Ask if user wants to use this message
        response = input("\nUse this message for commit? [y/N]: ").lower()
        
        if response == 'y':
            try:
                subprocess.run(
                    ['git', 'commit', '-m', message],
                    check=True
                )
                print("Changes committed successfully!")
            except subprocess.CalledProcessError:
                print("Error: Failed to commit changes")
                sys.exit(1)
        else:
            print("Commit canceled.")
            sys.exit(0)
            
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
        
if __name__ == "__main__":
    main()