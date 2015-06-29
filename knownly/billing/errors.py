

class PaymentProviderError(Exception):

    def __init__(self, message, cause):
        super(PaymentProviderError, self).__init__(message + u'. Caused by ' + repr(cause))
        self.cause = cause
