from llm_string.constraint_generator.constraints import Constraints


def parse_constraints(constraint: Constraints, default=None) -> list[str]:
    if constraint is None:
        return default

    variables = constraint.variables

    constraints = []

    for c in constraint.constraint:
        if c is None:
            constraints.append(None)
            continue

        constraint_expression = c

        for variable in variables:
            constraint_expression = constraint_expression.replace(variable, 's')

        constraints.append(constraint_expression)

    return constraints
