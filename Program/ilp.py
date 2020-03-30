# -*- coding: utf-8 -*-
import pulp as pulp

def solve_ilp(objective , constraints) :
    #print(objective)
    #print (constraints)
    prob = pulp.LpProblem('LP1' , pulp.LpMaximize)
    prob += objective
    for cons in constraints :
        prob += cons
    #print (prob)
    status = prob.solve()
    if status != 1 :
        #print 'status'
        #print status
        return None
    else :
        #return [v.varValue.real for v in prob.variables()]
        return [v.varValue.real for v in prob.variables()]



