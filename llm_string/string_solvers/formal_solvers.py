import os
import re
import subprocess
import tempfile

from loguru import logger
from z3 import Solver, sat, unknown, unsat

from llm_string.string_solvers.base import BaseStringSolver
from llm_string.structs import ConstraintProblem


class CVC5Solver(BaseStringSolver):
    name: str = "cvc5"
    solver_name: str = "csv5"

    def extract_unsat_core(self, output: str) -> list[str]:
        pattern = r"^(c\d+)$"
        logger.info(output)
        return re.findall(pattern, output, flags=re.MULTILINE)

    def solve(
        self, string_problem: ConstraintProblem, produce_unsat_core: bool = False
    ) -> ConstraintProblem:
        problem = ["(declare-const s String)"] + string_problem.smt_constraints

        problem = [
            "(set-logic QF_SLIA)",
            "(set-option :strings-exp true)",
            "(set-option :produce-unsat-cores true)",
            "(set-option :produce-models true)",
        ] + problem

        problem = problem + ["(check-sat)", "(get-model)"]
        if produce_unsat_core:
            problem = problem + ["(get-unsat-core)"]
        cons_str = "\n".join(problem)

        cons_str = cons_str.replace("str.to.re", "str.to_re")
        cons_str = cons_str.replace("str.in.re", "str.in_re")
        cons_str = cons_str.replace("str.to.int", "str.to_int")
        cons_str = cons_str.replace("re.complement", "re.comp")

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".smt2", delete=False, encoding="utf-8"
        ) as f:
            f.write(cons_str)
            temp_file_name = f.name

        result = subprocess.run(
            [
                "solvers/cvc5-Win64-x86_64-static/bin/cvc5.exe",
                temp_file_name,
                "--tlimit=5000",
            ],
            capture_output=True,
            text=True,
        )
        output = result.stdout.strip()
        os.remove(temp_file_name)

        # parse outcome
        sat_res = output.split("\n")[0]

        # parse the value of s
        unsat_core = []
        if sat_res == "sat":
            # Extract the value of s from the output
            string_val_line = output.split("\n")[2]
            assert string_val_line.startswith('(define-fun s () String "')

            str_val = string_val_line[len('(define-fun s () String "') : -2]

            start_index = output.find('(define-fun s () String "') + len(
                '(define-fun s () String "'
            )
            end_index = output.find('")', start_index)
            str_val = output[start_index:end_index]
        elif sat_res == "unsat":
            str_val = None
            if produce_unsat_core:
                unsat_core = self.extract_unsat_core(output)
        else:
            sat_res = "unknown"
            str_val = None

        string_problem.status = sat_res
        string_problem.value = str_val

        return (
            string_problem if not produce_unsat_core else (string_problem, unsat_core)
        )


class Z3Solver(BaseStringSolver):
    name: str = "z3_family"
    solver_name: str
    timeout: int = 30000

    status_map: dict = {str(sat): "sat", str(unsat): "unsat", str(unknown): "unknown"}

    def solve(self, string_problem: ConstraintProblem) -> ConstraintProblem:
        problem = ["(declare-const s String)"] + string_problem.smt_constraints
        cons_str = "\n".join(problem)

        solver = Solver()
        solver.set("timeout", self.timeout)
        if self.solver_name == "z3str3":
            solver.set("string_solver", "z3str3")

        solver.from_string(cons_str)

        # call the solver
        sat_res = solver.check()
        if sat_res == sat:
            model = solver.model()
            str_val = model[model.decls()[0]]
            # str_val = str_val.as_string() # NOTE this is taking long for some reason
            # str_val = str_val.strip('"')
        else:
            str_val = None

        string_problem.status = self.status_map[str(sat_res)]
        string_problem.value = str_val

        return string_problem
