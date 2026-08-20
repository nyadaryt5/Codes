class VeridianError(Exception):
    pass


class BudgetExhausted(VeridianError):
    pass


class DepthPolicyError(VeridianError):
    pass


class QueryError(VeridianError):
    pass


class IntegrityError(VeridianError):
    pass
