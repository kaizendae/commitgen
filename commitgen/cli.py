#!/usr/bin/env python3
import subprocess
import sys
import argparse

from commitgen.git_operations import GitOperations
from commitgen.ollama_client import OllamaClient

def main():
    """Main function to handle command-line interface."""
    parser = argparse.ArgumentParser(
        description="Generate a conventional commit message for staged changes."
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Show the message without committing"
    )
    parser.add_argument(
        "--hint",
        type=str,
        nargs="+",
        help="Helpful keywords to base the commit message on",
    )
    args = parser.parse_args()

    ollama_client = OllamaClient()
    try:
        # Check if there are staged changes
        status = subprocess.run(
            ["git", "diff", "--cached", "--quiet"], capture_output=True
        )

        if status.returncode == 0:
            print("No changes staged for commit")
            sys.exit(1)

        hint = None
        if args.hint:
            hint = args.hint
        # Get and analyze the diff
        diff = GitOperations.get_staged_diff()

        response = "r"
        while response == "r":
            message = ollama_client.generate_commit_message(diff, hint)
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
