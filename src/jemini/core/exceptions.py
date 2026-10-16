"""Core exceptions for Jemini framework."""

class JeminiException(Exception):
    """Base exception for all Jemini errors."""
    pass

class QuotaExceededException(JeminiException):
    """Raised when all API keys in the rotator are exhausted or rate-limited."""
    pass

class ChannelBootstrapException(JeminiException):
    """Raised when channel onboarding or context profile fails."""
    pass

class PublicationException(JeminiException):
    """Raised when content publication fails."""
    pass
