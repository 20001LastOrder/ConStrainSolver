import keyword

from z3 import *

from llm_string.models import Constraint, Constraints

from llm_string.logging.logging_overrides import getLogger

logger = getLogger()

class ConstraintEvaluator:
    def __init__(self, constraint_type: str, constraint: Constraint | Constraints, skip_validation=False):
        logger.debug("Creating a new constraint evaluator with type '{0}' and constraint '{1}'.", constraint_type, constraint)

        self.solver = Solver()

        self.constraint_type = constraint_type
        self.constraint = constraint

        if skip_validation:
            return

        for variable in constraint.variables:
            if constraint_type == "smt-lib2":
                expression = f"(declare-const {variable} String)"
                try:
                    logger.info("Declaring variable \"{0}\" with expression \"{1}\".", variable, expression)
                    self.solver.from_string(expression)
                except Z3Exception as ex:
                    logger.error("Variable declaration failed: \"{0}\": {1}", expression, str(ex))
                    raise ValueError("variable declaration failed", expression, ex)

                logger.info("Variable declared successfully: \"{0}\".", expression)

            elif constraint_type == "z3py":
                expression = f"{variable} = String('{variable}')"
                logger.info("Declaring variable {0} with expression \"{1}\".", variable, expression)

                if not variable.isidentifier():
                    logger.error("Variable declaration failed: the variable name {0} is not a valid Python identifier.", variable)
                    raise ValueError("variable declaration failed", f"'{variable}'",
                                     f"The variable name '{variable}' is not a valid Python identifier.")

                if keyword.iskeyword(variable):
                    logger.error("Variable declaration failed: the variable name {0} is a Python keyword.", variable)
                    raise ValueError("variable declaration failed", f"'{variable}'",
                                     f"The variable name '{variable}' is a Python keyword.")

                if variable in globals():
                    logger.error("Variable declaration failed: the variable name {0} is already defined in the global scope.", variable)
                    raise ValueError("variable declaration failed", f"'{variable}'",
                                     f"The variable name '{variable}' is already defined in the global scope. You are allowed to come up with a different name for the variable.")

                try:
                    exec(expression)
                except Exception as ex:
                    logger.error("Variable declaration failed: \"{0}\": {1}", expression, str(ex))
                    raise ValueError("variable declaration failed", expression, ex)

                logger.info("Variable declared successfully: \"{0}\".", expression)


        if isinstance(constraint, Constraint):
            if constraint_type == "smt-lib2":
                expression = f"(assert {constraint.constraint})"
                logger.info("Asserting constraint \"{0}\".", expression)
                try:
                    self.solver.from_string(expression)
                except Z3Exception as ex:
                    logger.error("Constraint assertion failed: \"{0}\": {1}", expression, str(ex))
                    raise ValueError("constraint assertion failed", expression, ex)

                logger.info("Constraint asserted successfully: \"{0}\".", expression)
            elif constraint_type == "z3py":
                expression = f"self.solver.add({constraint.constraint})"
                logger.info("Asserting constraint \"{0}\".", expression)
                try:
                    exec(expression)
                except SyntaxError as err:
                    if "was never closed" in err.msg:
                        exec(expression + ")")
                    else:
                        raise ValueError("constraint assertion failed", expression, err)
                except Exception as ex:
                    logger.error("Constraint assertion failed: \"{0}\": {1}", expression, str(ex))
                    raise ValueError("constraint assertion failed", expression, ex)

                logger.info("Constraint asserted successfully: \"{0}\".", expression)
        elif isinstance(constraint, Constraints):
            for c in constraint.constraint:
                if constraint_type == "smt-lib2":
                    expression = f"(assert {c})"
                    logger.info("Asserting constraint \"{0}\".", expression)
                    try:
                        self.solver.from_string(expression)
                    except Z3Exception as ex:
                        logger.error("Constraint assertion failed: \"{0}\": {1}", expression, str(ex))
                        raise ValueError("constraint assertion failed", expression, ex)

                    logger.info("Constraint asserted successfully: \"{0}\".", expression)
                elif constraint_type == "z3py":
                    expression = f"self.solver.add({c})"
                    logger.info("Asserting constraint \"{0}\".", expression)
                    try:
                        exec(expression)
                    except SyntaxError as err:
                        if "was never closed" in err.msg:
                            exec(expression + ")")
                        else:
                            raise ValueError("constraint assertion failed", expression, err)
                    except Exception as ex:
                        logger.error("Constraint assertion failed: \"{0}\": {1}", expression, str(ex))
                        raise ValueError("constraint assertion failed", expression, ex)

                    logger.info("Constraint asserted successfully: \"{0}\".", expression)

        if isinstance(constraint, Constraint):
            logger.info(f"Checking if the constraint is satisfiable.")
            if self.solver.check() == "unsat":
                logger.error("Constraint is unsatisfiable: \"{0}\".", self.solver.sexpr())
                raise ValueError("constraint is unsatisfiable", self.solver.sexpr())

            logger.info("Constraint is satisfiable: \"{0}\".", self.solver.sexpr())


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
            logger.error("Expected {0} arguments, but got {1}.", len(self.constraint.variables), len(args))
            raise IndexError(f"Expected {len(self.constraint.variables)} arguments, but got {len(args)}.")

        base_expression = self.solver.sexpr()

        if self.constraint_type == "smt-lib2":
            for variable, value in zip(self.constraint.variables, args):
                expression = f'(assert (= {variable} "{value}"))'
                logger.info("Assigning value \"{0}\" to variable \"{1}\" with expression \"{2}\".", value, variable, expression)
                try:
                    self.solver.from_string(expression)
                except Z3Exception as ex:
                    logger.error("Variable assignment failed: \"{0}\": {1}", expression, str(ex))
                    raise ValueError("variable assignment failed", expression, ex)

                logger.info("Variable assigned successfully: \"{0}\".", expression)

        if self.constraint_type == "z3py":
            for variable, value in zip(self.constraint.variables, args):
                expression = f"{variable} = String('{variable}')"
                logger.info("Declaring variable \"{0}\" with expression \"{1}\".", variable, expression)
                try:
                    exec(expression)
                except Exception as ex:
                    logger.error("Variable declaration failed: \"{0}\": {1}", expression, str(ex))
                    raise ValueError("variable declaration failed", expression, ex)

                logger.info("Variable declared successfully: \"{0}\".", expression)

                expression = f"self.solver.add({variable} == '{value}')"
                logger.info("Assigning value \"{0}\" to variable \"{1}\" with expression \"{2}\".", value, variable, expression)
                try:
                    exec(expression)
                except Exception as ex:
                    logger.error("Variable assignment failed: \"{0}\": {1}", expression, str(ex))
                    raise ValueError("variable assignment failed", expression, ex)

                logger.info("Variable assigned successfully: \"{0}\".", expression)


        logger.info("Checking if the constraint is satisfied.")
        is_sat = str(self.solver.check()) == "sat"
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