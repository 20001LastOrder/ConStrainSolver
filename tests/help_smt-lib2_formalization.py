
from llm_string.string_solvers.base import ConstraintProblem
from llm_string.string_solvers.formal_solvers import CVC5Solver, Z3Solver
from loguru import logger
import sys

# Logger, not required
logger.remove()
# logger.add(sys.stderr, level="INFO")

# Write your constraint here
constraint = '''
;(assert (>= (str.len s) 10))

(assert (str.in.re s (re.* (re.union (str.to.re "(") (str.to.re ")")))))

(assert (= (- (str.len s) (str.len (str.replace_all s "(" "")))
           (- (str.len s) (str.len (str.replace_all s ")" "")))))
'''

# Write your samples here, format: {'input': expected_output}
samples = {
    '()':  True,
    '(())':  True,
    ')()(':  False,
    '(()((((())':  False,
    ')))))(((((':  False,
    '(((((((())))':False,
    '(())()()((()))':  True,
    'awjwhdsbbjsdbca':  False,
}

# This is used to ask the solver to generate a consistentstring
# samples = {None: True}

for sample, expected in samples.items():
    init = "" if sample is None else f'(assert (= s "{sample}"))'
    con_str = f'''
    {init}
    {constraint}
    '''
    con_str
    p = ConstraintProblem(name='.', smt_constraints=con_str.split('\n'))
    s = CVC5Solver()
    # s = Z3Solver(solver_name='z3')
    out = s.solve(p)
    logger.info(out)

    correctness = (expected and out.status == 'sat') or (not expected and out.status == 'unsat')
    v = "PASS" if correctness else "FAIL"
    print(f"{v} --- In={sample}, Out={out.value}. Expected={expected}, Got={out.status}")
