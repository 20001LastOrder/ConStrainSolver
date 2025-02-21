import keyword

from z3 import *

from llm_string.models import Constraint

import llm_string.logging.logging_overrides as logging

logger = logging.getLogger('constraint_evaluator')

class ConstraintEvaluator:
    def __init__(self, constraint_type: str, constraint: Constraint):
        logger.debug(f"Creating a new constraint evaluator with type '{constraint_type}' and constraint '{constraint}'.")

        self.solver = Solver()

        for variable in constraint.variables:
            if constraint_type == "smt-lib2":
                expression = f"(declare-const {variable} String)"
                try:
                    logger.info("Declaring variable \"%s\" with expression \"%s\".", variable, expression)
                    self.solver.from_string(expression)
                except Z3Exception as ex:
                    logger.error("Variable declaration failed: \"%s\": %s", expression, str(ex))
                    raise ValueError("variable declaration failed", expression, ex)

                logger.info("Variable declared successfully: \"%s\".", expression)

            elif constraint_type == "z3py":
                expression = f"{variable} = String('{variable}')"
                logger.info("Declaring variable %s with expression \"%s\".", variable, expression)

                if not variable.isidentifier():
                    logger.error("Variable declaration failed: the variable name %s is not a valid Python identifier.", variable)
                    raise ValueError("variable declaration failed", f"'{variable}'",
                                     f"The variable name '{variable}' is not a valid Python identifier.")

                if keyword.iskeyword(variable):
                    logger.error("Variable declaration failed: the variable name %s is a Python keyword.", variable)
                    raise ValueError("variable declaration failed", f"'{variable}'",
                                     f"The variable name '{variable}' is a Python keyword.")

                if variable in globals():
                    logger.error("Variable declaration failed: the variable name %s is already defined in the global scope.", variable)
                    raise ValueError("variable declaration failed", f"'{variable}'",
                                     f"The variable name '{variable}' is already defined in the global scope. You are allowed to come up with a different name for the variable.")

                try:
                    exec(expression)
                except Exception as ex:
                    logger.error("Variable declaration failed: \"%s\": %s", expression, str(ex))
                    raise ValueError("variable declaration failed", expression, ex)

                logger.info("Variable declared successfully: \"%s\".", expression)


        if constraint_type == "smt-lib2":
            expression = f"(assert {constraint.constraint})"
            logger.info(f"Asserting constraint \"%s\".", expression)
            try:
                self.solver.from_string(expression)
            except Z3Exception as ex:
                logger.error("Constraint assertion failed: \"%s\": %s", expression, str(ex))
                raise ValueError("constraint assertion failed", expression, ex)

            logger.info("Constraint asserted successfully: \"%s\".", expression)
        elif constraint_type == "z3py":
            expression = f"self.solver.add({constraint.constraint})"
            logger.info("Asserting constraint \"%s\".", expression)
            try:
                exec(expression)
            except SyntaxError as err:
                if "was never closed" in err.msg:
                    exec(expression + ")")
                else:
                    raise ValueError("constraint assertion failed", expression, err)
            except Exception as ex:
                logger.error("Constraint assertion failed: \"%s\": %s", expression, str(ex))
                raise ValueError("constraint assertion failed", expression, ex)

            logger.info("Constraint asserted successfully: \"%s\".", expression)

        logger.info(f"Checking if the constraint is satisfiable.")
        if self.solver.check() == "unsat":
            logger.error("Constraint is unsatisfiable: \"%s\".", self.solver.sexpr())
            raise ValueError("constraint is unsatisfiable", self.solver.sexpr())

        logger.info("Constraint is satisfiable: \"%s\".", self.solver.sexpr())

        self.constraint_type = constraint_type
        self.constraint = constraint


    def evaluate(self, *args) -> bool:
        """
        Evaluate whether the arguments satisfy the constraint. If there is an error with variables or the constraint, an exception is raised.
        :param args: list of values for each variable in the constraint, where the order is defined by the Constraint object.
        :return: True if the constraint is satisfied, False if it is not.
        :raises IndexError: if the number of arguments does not match the number of variables in the constraint.
        :raises ValueError: if there is an error with the variables or the constraint.
        """
        logger.debug("Evaluating [%s] with constraint \"%s\".", str(args), self.constraint)

        if len(args) != len(self.constraint.variables):
            logger.error("Expected %d arguments, but got %d.", len(self.constraint.variables), len(args))
            raise IndexError(f"Expected {len(self.constraint.variables)} arguments, but got {len(args)}.")

        base_expression = self.solver.sexpr()

        if self.constraint_type == "smt-lib2":
            for variable, value in zip(self.constraint.variables, args):
                expression = f'(assert (= {variable} "{value}"))'
                logger.info("Assigning value \"%s\" to variable \"%s\" with expression \"%s\".", value, variable, expression)
                try:
                    self.solver.from_string(expression)
                except Z3Exception as ex:
                    logger.error("Variable assignment failed: \"%s\": %s", expression, str(ex))
                    raise ValueError("variable assignment failed", expression, ex)

                logger.info("Variable assigned successfully: \"%s\".", expression)

        if self.constraint_type == "z3py":
            for variable, value in zip(self.constraint.variables, args):
                expression = f"{variable} = String('{variable}')"
                logger.info("Declaring variable \"%s\" with expression \"%s\".", variable, expression)
                try:
                    exec(expression)
                except Exception as ex:
                    logger.error("Variable declaration failed: \"%s\": %s", expression, str(ex))
                    raise ValueError("variable declaration failed", expression, ex)

                logger.info("Variable declared successfully: \"%s\".", expression)

                expression = f"self.solver.add({variable} == '{value}')"
                logger.info("Assigning value \"%s\" to variable \"%s\" with expression \"%s\".", value, variable, expression)
                try:
                    exec(expression)
                except Exception as ex:
                    logger.error("Variable assignment failed: \"%s\": %s", expression, str(ex))
                    raise ValueError("variable assignment failed", expression, ex)

                logger.info("Variable assigned successfully: \"%s\".", expression)


        logger.info("Checking if the constraint is satisfied.")
        is_sat = str(self.solver.check()) == "sat"
        logger.info("Constraint is satisfied: %s.", is_sat)

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
            logger.error("Error evaluating constraint: %s", str(ex))
            return False