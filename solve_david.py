#!/usr/bin/env python

from parse_sg  import mine_concepts
from json      import dumps as jsons
from itertools import product
from itertools import starmap
from itertools import combinations
from itertools import permutations
from concepts  import *

def main():
	file = "examples/david_cell.sg"
	sg, cause_concepts, or_cause_concepts = mine_concepts(file, False)
	concepts = cause_concepts + or_cause_concepts
	graph = dict()
	all_signals = sg.encoding
	literals = starmap(Literal, product(all_signals, "+-"))
	# for cause in cause_concepts:
	for cond, tran in permutations(literals, 2):
		if cond == ~tran:
			continue
		signals = set(sg.encoding)
		signals.discard(cond.signal)
		signals.discard(tran.signal)
		other_literals = starmap(Literal, product(signals, "+-"))
		mk_or_conc = lambda cond2 : OrCause(cond, cond2, tran)
		cause = Cause(cond, tran)
		graph[cause] = map(mk_or_conc, other_literals)
	# "orGate a b c = or_cause_rrr a b c . cause a- c- . cause b- c-"
	# "norGate a b c = or_cause_rrf a b c . cause a- c+ . cause b- c+",
	or_causes = set().union(*map(set, graph.values()))
	for y in all_signals:
		remaining = set(all_signals) - set([y])
		for a, b in combinations(remaining, 2):
			or_cause = OrCause(
				Literal(a, "+"),
				Literal(b, "+"),
				Literal(y, "-")
			)
			nor_gate = NorGate(a, b, y)
			cause1 = Cause(Literal(a, "-"), Literal(y, "+"))
			cause2 = Cause(Literal(b, "-"), Literal(y, "+"))
			if (or_cause in or_cause_concepts) and (cause1 in cause_concepts) \
				and (cause2 in cause_concepts):
				graph[nor_gate] = [or_cause, cause1, cause2]
				# print "%-16s = %s . %s . %s" % (nor_gate, or_cause, cause1, cause2)
	for key, val in graph.iteritems():
		if (type(key) == Cause) and key in cause_concepts:
			print "%-16s %s" % (key, map(str, val))

if __name__ == "__main__":
	main()