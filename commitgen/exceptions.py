class CommitGenError(Exception):
    """Base exception for CommitGen"""
    pass

class GitError(CommitGenError):
    """Git operation related errors"""
    pass

class OllamaError(CommitGenError):
    """Ollama API related errors"""
    pass