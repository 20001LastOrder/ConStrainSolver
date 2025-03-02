from z3 import Solver, Z3Exception

from llm_string.constraint_generator.core.helpers.solver_helpers import \
    create_solver_with_smt_lib2_constraint, \
    create_solver_with_smt_lib2_constraints, \
    create_solver_with_z3py_constraint, \
    create_solver_with_z3py_constraints

from llm_string.models import Constraint, Constraints

from llm_string.logging.logging_overrides import getLogger

logger = getLogger()


class ConstraintEvaluator:
    constraint: Constraint | Constraints = None
    solver: Solver = None

    def evaluate(self, *args) -> bool:
        """
        Evaluate whether the arguments satisfy the constraint. If there is an error with variables or the constraint, an exception is raised.
        :param args: list of values for each variable in the constraint, where the order is defined by the Constraint object.
        :return: True if the constraint is satisfied, False if it is not.
        :raises IndexError: if the number of arguments does not match the number of variables in the constraint.
        :raises ValueError: if there is an error with the variables or the constraint.
        """
        logger.debug("Evaluating [{0}] with constraint \"{1}\".", str(args), self.constraint)

        if len(args) != len(self.constraint.variables):
            raise IndexError(f"Expected {len(self.constraint.variables)} arguments, but got {len(args)}.")

        base_expression = self.solver.sexpr()

        for variable, value in zip(self.constraint.variables, args):
            expression = f'(assert (= {variable} "{value}"))'
            logger.info("Assigning value \"{0}\" to variable \"{1}\" with expression \"{2}\".", value, variable, expression)

            try:
                self.solver.from_string(expression)
            except Z3Exception as ex:
                logger.error("Variable assignment failed: \"{0}\": {1}", expression, str(ex))
                raise ValueError("variable assignment failed", expression, ex)

            logger.info("Variable assigned successfully: \"{0}\".", expression)


        logger.info("Checking if the constraint is satisfied.")
        is_sat = self.solver.check().r == 1
        logger.info("Constraint is satisfied: {0}.", is_sat)

        self.solver.reset()
        self.solver.from_string(base_expression)

        return is_sat


    def safe_evaluate(self, *args) -> bool:
        """
        Safely evaluate whether the arguments satisfy the constraint. See also evaluate().
        :param args: list of values for each variable in the constraint, where the order is defined by the Constraint object.
        :return: True if the constraint is satisfied, False if it is not or if an error occurred.
        """
        try:
            return self.evaluate(*args)
        except Exception as ex:
            logger.error("Error evaluating constraint: {0}", str(ex))
            return False


    @staticmethod
    def create_evaluator_with_single_constraint(constraint_type: str, constraint: Constraint) -> "ConstraintEvaluator":
        logger.debug("Creating a new constraint evaluator with type '{0}' and constraint '{1}'.", constraint_type, constraint)

        constraint_evaluator = ConstraintEvaluator()
        constraint_evaluator.constraint = constraint

        if constraint_type == "smt-lib2":
            constraint_evaluator.solver = create_solver_with_smt_lib2_constraint(constraint)

        elif constraint_type == "z3py":
            constraint_evaluator.solver = create_solver_with_z3py_constraint(constraint)

        else:
            raise ValueError(f"Unknown constraint type: {constraint_type}")

        return constraint_evaluator


    @staticmethod
    def create_evaluator_with_multiple_constraints(constraint_type: str, constraints: Constraints) -> tuple["ConstraintEvaluator", list[tuple[int, Exception]]]:
        logger.debug("Creating a new constraint evaluator with type '{0}' and constraint '{1}'.", constraint_type, constraints)

        constraint_evaluator = ConstraintEvaluator()
        constraint_evaluator.constraint = constraints

        if constraint_type == "smt-lib2":
            solver, error_list = create_solver_with_smt_lib2_constraints(constraints)

        elif constraint_type == "z3py":
            solver, error_list = create_solver_with_z3py_constraints(constraints)

        else:
            raise ValueError(f"Unknown constraint type: {constraint_type}")

        constraint_evaluator.solver = solver

        return constraint_evaluator, error_list