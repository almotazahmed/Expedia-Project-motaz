
class CustomBaseException(Exception):
    """Base class for all custom exceptions."""
    def __init__(self, message="An error occurred"):
        super().__init__(message)


class PaymentProcessingError(CustomBaseException):
    """Exception raised for payment processing errors."""
    def __init__(self, message="Payment processing failed"):
        super().__init__(message)


class RefundProcessingError(CustomBaseException):
    """Exception raised for payment processing errors."""
    def __init__(self, message="Refund processing failed"):
        super().__init__(message)


class BookingError(CustomBaseException):
    """Exception raised for booking-related errors."""
    def __init__(self, message="Booking failed"):
        super().__init__(message)


class CancellationError(CustomBaseException):
    """Exception raised for cancellation errors."""
    def __init__(self, message="cancellation failed"):
        super().__init__(message)


class NetworkError(CustomBaseException):
    """Exception raised for network-related errors."""
    def __init__(self, message="Network issue encountered"):
        super().__init__(message)


class InvalidInputError(CustomBaseException):
    """Exception raised for invalid input when a number is expected."""
    def __init__(self, message="Invalid input, please enter a valid number"):
        super().__init__(message)

class LoginError(CustomBaseException):
    """Exception raised for login error."""
    def __init__(self, message="Invalid Username or Password. Please try again."):
        super().__init__(message)



