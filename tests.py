#!/usr/bin/python2.7
import gambit
import random
import matplotlib, matplotlib.pyplot
import numpy
import types

solver = gambit.nash.ExternalEnumMixedSolver()
game_size = 5
vals_jmps = 1
max_payoff = 100

def show_plot(arg1, arg2=None):

    def real_decorator(f):
        def wrapper(*args, **kwargs):
            matplotlib.pyplot.figure(figsize=(arg1, arg2))
            result = f(*args, **kwargs)
            matplotlib.pyplot.show()
            return result
        return wrapper

    if type(arg1) == types.FunctionType:
        f = arg1
        arg1, arg2 = 10, 5
        return real_decorator(f)
    return real_decorator


def randomize_game(size=game_size, max_payoff=max_payoff):
	m = size
	g = gambit.Game.new_table([m,m])
	for i in xrange(m):
		for j in xrange(m):
			g[i, j][0] = int(random.random() * max_payoff)
			g[i, j][1] = -g[i, j][0]
	return g

def compute_nash_eq(g):
	return solver.solve(g)

def dist_diff(p1, p2, g):
	return max([abs(p1[0][i]-p2[0][i]) for i in xrange(game_size)])

def worst_payoff(p1_resp_both, best_resp_both, g):
	p2_resp = best_resp_both[0][g.players[1]]
	p1_resp = p1_resp_both[0][g.players[0]]

	return sum([p1_resp[i] * p2_resp[j] * g[i, j][0] for i in xrange(game_size) for j in xrange(game_size)])

def get_counter_example():
	for i in xrange(10000):
		#print "trying"
		cond = False
		g = None
		rsol = None
		ind = None
		while not cond:
			g = randomize_game()
			rsol = compute_nash_eq(g)		
			p2 = list(rsol[0][g.players[1]])
			ind = 0
			break
	#			if p2.count(0.0) >= 1:
	#			ind = p2.index(0.0)
	#			break
		best_payoff = rsol[0][g.players[0]].profile.payoff(0)
		hidden_indx = (0, ind)
		g[hidden_indx][0] = max_payoff
		g[hidden_indx][1] = -max_payoff
		rsol_new = compute_nash_eq(g)
		best_payoff_new = rsol_new[0][g.players[0]].profile.payoff(0)
		if best_payoff_new < best_payoff:
			print 'sol-new:', rsol_new, 'payoff:', best_payoff_new
			print 'sol-original:', rsol, 'payoff:', best_payoff 
			print "game-after change:"
			print g.__repr__()
			print "	found"
			break


def gen_vals(jmps=vals_jmps):
	vals = []
	# first gen the game.
	g = randomize_game()
	# compute its real mixed winner.
	rsol = compute_nash_eq(g)
	# remove one tile, try over all completions to it.
	rem_ind = int(random.random() * (game_size - 1)), int(random.random() * (game_size - 1))
	backup_vals = g[rem_ind[0], rem_ind[1]][0], g[rem_ind[0], rem_ind[1]][1]
	print "real value for k is", backup_vals[0]
	for val in xrange(-max_payoff, +max_payoff, jmps):
		g[rem_ind[0], rem_ind[1]][0] = val
		g[rem_ind[0], rem_ind[1]][1] = -val
		cur_ne = compute_nash_eq(g)
		g[rem_ind[0], rem_ind[1]][0] = backup_vals[0]
		g[rem_ind[0], rem_ind[1]][1] = backup_vals[1]
		vals.append((val, worst_payoff(cur_ne, rsol, g)))
	# return vals / plot graph of: completion -> statistical diff.
	plot_it(vals)
	return vals

@show_plot
def plot_it(vals):
	for (x, y) in vals:
		matplotlib.pyplot.scatter(x, y)
	axes = matplotlib.pyplot.gca()
	axes.set_xlabel('x')
	axes.set_ylabel('y')

if __name__ == "__main__":
	for i in xrange(1):
		get_counter_example()

