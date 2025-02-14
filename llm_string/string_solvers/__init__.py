from llm_string.string_solvers.formal_solvers import CVC5Solver, Z3Solver
from llm_string.string_solvers.llm_solver import LLMSolver
from llm_string.utils import get_llm


def get_solver(args):
    if args.approach == "llm":
        llm = get_llm(args)
        return LLMSolver(llm=llm, use_variable_name=args.use_variable_name)
    elif args.approach == "smt":
        if args.smt_solver == "cvc5":
            return CVC5Solver()
        elif "z3" in args.smt_solver:
            return Z3Solver(solver_name=args.smt_solver)
        else:
            raise ValueError(f"Unknown SMT solver: {args.smt_solver}")
    else:
        raise ValueError(f"Unknown approach: {args.approach}")


__all__ = ["CVC5Solver", "Z3Solver", "LLMSolvers", "get_solver"]
