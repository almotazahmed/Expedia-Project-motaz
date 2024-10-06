
class CustomBaseException(Exception):
    """Base class for all custom exceptions."""
    def __init__(self, message="An error occurred"):
        super().__init__(message)


class PaymentProcessingError(CustomBaseException):
    """Exception raised for payment processing errors."""
    def __init__(self, message="Payment processing failed"):
        super().__init__(message)


class BookingError(CustomBaseException):
    """Exception raised for booking-related errors."""
    def __init__(self, message="Booking failed"):
        super().__init__(message)


class NetworkError(CustomBaseException):
    """Exception raised for network-related errors."""
    def __init__(self, message="Network issue encountered"):
        super().__init__(message)


class InvalidInputError(Exception):
    """Exception raised for invalid input when a number is expected."""
    def __init__(self, message="Invalid input, please enter a valid number"):
        super().__init__(message)

