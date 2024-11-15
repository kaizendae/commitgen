import git
from .logger import logger
from .exceptions import GitError
class GitOperations:
    @staticmethod
    def get_staged_diff():
        try:
            repo = git.Repo(".")
            return repo.git.diff("--cached")
        except git.exc.InvalidGitRepositoryError as e:
            logger.error("Not a valid Git repository")
            raise GitError("Invalid repository") from e

    @staticmethod
    def get_readme_content():
        try:
            with open("README.md", "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return None 