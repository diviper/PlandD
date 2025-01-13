"""Custom exceptions for the PlanD application"""

class BasePlanDError(Exception):
    """Base exception for PlanD application"""
    pass

class InvalidTimeFormatError(BasePlanDError):
    """Raised when time format is invalid"""
    pass

class TimeConflictError(BasePlanDError):
    """Raised when there is a time conflict between plans"""
    pass

class PlanNotFoundError(BasePlanDError):
    """Raised when plan is not found"""
    pass

class InvalidPriorityError(BasePlanDError):
    """Raised when priority is invalid"""
    pass

class InvalidTimeBlockError(BasePlanDError):
    """Raised when time block is invalid"""
    pass

class EmptyPlanError(BasePlanDError):
    """Raised when plan text is empty"""
    pass

class PastTimeError(BasePlanDError):
    """Raised when time is in the past"""
    pass

class InvalidUserError(BasePlanDError):
    """Raised when user is invalid"""
    pass

class PlanTooLongError(BasePlanDError):
    """Raised when plan is too long"""
    pass

class InvalidStepOrderError(BasePlanDError):
    """Raised when step order is invalid"""
    pass

class DuplicateStepError(BasePlanDError):
    """Raised when there are duplicate steps"""
    pass

class ConcurrentModificationError(BasePlanDError):
    """Raised when there are concurrent modifications"""
    pass

class AIServiceError(BasePlanDError):
    """Raised when there is an error in AI service"""
    pass

class DatabaseError(BasePlanDError):
    """Raised when there is a database error"""
    pass

class ConfigurationError(BasePlanDError):
    """Raised when there is a configuration error"""
    pass

class ValidationError(BasePlanDError):
    """Raised when validation fails"""
    pass

class AuthenticationError(BasePlanDError):
    """Raised when authentication fails"""
    pass

class AuthorizationError(BasePlanDError):
    """Raised when authorization fails"""
    pass

class RateLimitError(BasePlanDError):
    """Raised when rate limit is exceeded"""
    pass

class ExternalServiceError(BasePlanDError):
    """Raised when external service fails"""
    pass

class MessageProcessingError(BasePlanDError):
    """Raised when message processing fails"""
    pass
