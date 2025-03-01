from func_timeout import func_timeout
from z3 import Solver, Z3Exception

from llm_string.logging.logging_overrides import getLogger
from llm_string.models import Constraint, Constraints

logger = getLogger()


def create_solver_with_smt_lib2_constraint(constraint: Constraint) -> Solver:
    solver = _create_solver_with_variables(constraint.variables)

    constraint_expression = f"(assert {constraint.constraint})"

    try:
        solver.from_string(constraint_expression)
    except Z3Exception as ex:
        raise ValueError("Constraint assertion failed", constraint_expression, ex)

    logger.info(f"Checking if the constraint is satisfiable.")

    check = func_timeout(5, solver.check)
    if check.r == -1:
        raise ValueError("Constraint is unsatisfiable", solver.sexpr().replace("\n", " "))

    logger.info("Constraint is satisfiable: \"{0}\".", solver.sexpr().replace("\n", " "))

    return solver


def create_solver_with_smt_lib2_constraints(constraints: Constraints) -> tuple[Solver, list[tuple[int, Exception]]]:
    solver = _create_solver_with_variables(constraints.variables)

    return _update_solver_with_smt_lib2_constraints(solver, constraints)


def create_solver_with_z3py_constraint(constraint: Constraint) -> Solver:
    solver = _create_solver_with_variables(constraint.variables)

    try:
        solver.add(constraint.constraint)
    except Z3Exception as ex:
        raise ValueError("Constraint assertion failed", constraint.constraint, ex)

    logger.info(f"Checking if the constraint is satisfiable.")

    check = func_timeout(5, solver.check)
    if check.r == -1:
        raise ValueError("Constraint is unsatisfiable", solver.sexpr().replace("\n", " "))

    logger.info("Constraint is satisfiable: \"{0}\".", solver.sexpr().replace("\n", " "))

    return solver


def create_solver_with_z3py_constraints(constraints: Constraints) -> tuple[Solver, list[tuple[int, Exception]]]:
    solver = _create_solver_with_variables(constraints.variables)

    return _update_solver_with_z3py_constraints(solver, constraints.constraint)


def _create_solver_with_variables(variables: list[str]) -> Solver:
    solver = Solver()

    for variable in list(dict.fromkeys(variables)):
        variable_declare_expression = f"(declare-const {variable} String)"
        try:
            solver.from_string(variable_declare_expression)
        except Z3Exception as ex:
            raise ValueError("variable declaration failed", variable_declare_expression, ex)

    return solver


def _update_solver_with_smt_lib2_constraints(solver: Solver, constraints: Constraints) -> tuple[Solver, list[tuple[int, Exception]]]:
    error_list = []

    for i, constraint in enumerate(constraints.constraint):
        # a common issue is that the LLM would append a punctuation mark to the end of the constraint
        # which is an easy fix, so we can fix it here.
        if not constraint.endswith(")"):
            constraint = constraint[:-1]

        # another common issue is to already wrap the answer in an assert statement
        if not constraint.startswith("(assert"):
            constraint_expression = f"(assert {constraint})"
        else:
            constraint_expression = constraint

        current_solver_state = solver.sexpr()

        try:
            solver.from_string(constraint_expression)
        except Z3Exception as ex:
            error_list.append((i, ex))
            if current_solver_state == "":
                solver = _create_solver_with_variables(constraints.variables)
            else:
                solver = Solver()
                solver.from_string(current_solver_state)

    logger.info(f"Checking if the constraints are satisfiable.")

    try:
        check = func_timeout(5, solver.check)
        if check.r == -1:
            error_list.insert(0, (-1, ValueError("Constraints are unsatisfiable", solver.sexpr().replace("\n", " "))))
    except Exception as ex:
        error_list.insert(0, (-1, ex))

    return solver, error_list


def _update_solver_with_z3py_constraints(solver: Solver, constraints_list: list[str]) -> (Solver, list[tuple[int, Exception]]):
    error_list = []

    for i, constraint in enumerate(constraints_list):
        constraint_expression = f"solver.add({constraint})"

        try:
            exec(constraint_expression)
        except SyntaxError as err:
            # a common issue is that the LLM would miss a closing parenthesis,
            # which is an easy fix, so we can fix it here.
            if "was never closed" in err.msg:
                exec(constraint_expression + ")")
            else:
                raise err
        except Exception as ex:
            error_list.append((i, ex))

    logger.info(f"Checking if the constraints are satisfiable.")

    try:
        check = func_timeout(5, solver.check)
        if check.r == -1:
            error_list.insert(0, (-1, ValueError("Constraints are unsatisfiable", solver.sexpr().replace("\n", " "))))
    except Exception as ex:
        error_list.insert(0, (-1, ex))

    return solver, error_list
