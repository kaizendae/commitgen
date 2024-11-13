#!/usr/bin/env python3
import os
import subprocess
import sys
import git
import argparse
import requests
from importlib import resources


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


def get_readme_content():
    """
    Reads the README.md file from the current directory.
    Returns None if the file doesn't exist.
    """
    try:
        with open("README.md", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return None


def get_conventional_commit_prompt(diff, keywords=None):
    """Create a prompt for Claude to generate a conventional commit message."""
    prompt = resources.read_text("commitgen", "prompt.txt")

    # Add README content to the prompt if available
    readme_content = get_readme_content()
    if readme_content:
        prompt += f"\n\nHere's the project's README.md content use it to generate a more accurate commit message:\n{readme_content} \n\n THIS IS ONLY FOR CONTEXT, DO NOT Generate a script or code ever if the readme mentions it. USE THE README CONTENT TO GENERATE A MORE ACCURATE COMMIT MESSAGE ONLY."

    if keywords:
        prompt += f"\nHere are some helpful keywords to base the commit message on: {keywords}"

    return f"""{prompt}
Here's the diff:
{diff}

Return only the commit message without any additional explanation."""


def generate_commit_message(diff, keywords=None):
    """Generate a commit message using Ollama API."""
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3.2",  # or whichever model you want to use
                "prompt": get_conventional_commit_prompt(diff, keywords),
                "system": "You are a helpful assistant that generates clear and concise git commit messages.",
                "stream": False,
            },
        )

        if response.status_code == 200:
            return response.json()["response"]
        else:
            print(f"Error: Ollama API returned status code {response.status_code}")
            sys.exit(1)

    except Exception as e:
        print(f"Error generating commit message: {str(e)}")
        sys.exit(1)


def main():
    """Main function to handle command-line interface."""
    parser = argparse.ArgumentParser(
        description="Generate a conventional commit message for staged changes."
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Show the message without committing"
    )
    parser.add_argument(
        "-k",
        "--keywords",
        type=str,
        nargs="+",
        help="Helpful keywords to base the commit message on",
    )
    args = parser.parse_args()

    try:
        # Check if there are staged changes
        status = subprocess.run(
            ["git", "diff", "--cached", "--quiet"], capture_output=True
        )

        if status.returncode == 0:
            print("No changes staged for commit")
            sys.exit(1)

        keywords = None
        if args.keywords:
            keywords = args.keywords
        # Get and analyze the diff
        diff = get_staged_diff()

        response = "r"
        while response == "r":
            message = generate_commit_message(diff, keywords)
            print("\nRegenerated commit message:")
            print("-" * 50)
            print(message)
            print("-" * 50)
            if args.dry_run:
                print("\nDry run - not committing changes")
                sys.exit(0)
            response = input("\nUse this message for commit? [y/N/r]: ").lower()

            if response == "y":
                try:
                    subprocess.run(["git", "commit", "-m", message], check=True)
                    print("Changes committed successfully!")
                except subprocess.CalledProcessError:
                    print("Error: Failed to commit changes")
                    sys.exit(1)
            elif response == "r":
                continue
            else:
                print("Commit canceled.")
                sys.exit(0)

    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
