# utilities
import buildGraph
import infectionModels
import random
from scipy import stats
import exportGraph

def nCk(n, k):
    """
    A fast way to calculate binomial coefficients by Andrew Dalke (contrib).
    """
    if 0 <= k <= n:
        ntok = 1
        ktok = 1
        for t in range(1, min(k, n - k) + 1):
            ntok *= n
            ktok *= t
            n -= 1
        return ntok // ktok
    else:
        return 0
        
        
'''Runs a spreading algorithm over a real dataset. Either pramod's algo (deterministic) or message passing (ours)'''    
def runDataset(filename, min_degree, trials, max_time=100, max_infection = -1):
    # Run dataset runs a spreading algorithm over a dataset. 
    # Inputs:
    #
    #       filename:               name of the file containing the data
    #       min_degree:             remove all nodes with degree lower than min_degree
    #       trials:                 number of trials to run
    #       max_time(opt):          the maximum number of timesteps to use
    #       max_infection(opt):     the maximum number of nodes a node can infect in any given timestep
    #
    # Outputs:
    #
    #       p:                      average proportion of nodes reached by the algorithm 
    #       num_infected:           total number of nodes infected by the algorithm
    #
    # NB: If max_infection is not set, then we'll run the deterministic algorihtm. Otherwise, it's the message passing one.
    
    adjacency = buildGraph.buildDatasetGraph(filename, min_degree)
    # print(adjacency)
    num_nodes = len(adjacency)
    num_true_nodes = sum([len(item)>0 for item in adjacency])
    print('nonzero nodes:',num_true_nodes)
    num_infected = 0
    p = 0
    pd_jordan = [0 for i in range(max_time)]
    pd_rumor = [0 for i in range(max_time)]
    pd_ml = [0 for i in range(max_time)]
    
    stepsize = 5;
    # max_infection+1 is the degree of the tree
    max_nodes = int(infectionModels.N_nodes(max_time,max_infection+1))
    bins = [i for i in range(1,max_nodes+stepsize+1,stepsize)]
    jordan_found = [0 for i in range(len(bins))]
    jordan_count = [0 for i in range(len(bins))]
    rumor_found = [0 for i in range(len(bins))]
    rumor_count = [0 for i in range(len(bins))]
    
    for trial in range(trials):
        # if trial % 20 == 0:
        print('Trial ',trial, ' / ',trials)
        while True:
            source = random.randint(0,num_nodes-1)
            if len(adjacency[source]) > 0:
                break
        if max_infection == -1:      # i.e. we're running the deterministic version
            num_infected, infection_pattern = infectionModels.infect_nodes_deterministic(source,adjacency)
        else:
            num_infected, infection_pattern, who_infected, results = infectionModels.infect_nodes_adaptive_diff(source,adjacency,max_time,max_infection,stepsize)
            # unpack the results
            jordan_results, rumor_results, ml_correct = results
            jordan_bins, jordan_instances, jordan_detected, jordan_correct = jordan_results
            rumor_bins, rumor_instances, rumor_detected, rumor_correct = rumor_results
            
            pd_jordan = [i+j/(1.0) for (i,j) in zip(pd_jordan, jordan_correct)]
            jordan_found = [i+j for (i,j) in zip(jordan_found,jordan_detected)]
            jordan_count = [i+j for (i,j) in zip(jordan_count,jordan_instances)]
            pd_rumor = [i+j/(1.0) for (i,j) in zip(pd_rumor, rumor_correct)]
            rumor_found = [i+j for (i,j) in zip(rumor_found,rumor_detected)]
            rumor_count = [i+j for (i,j) in zip(rumor_count,rumor_instances)]
            
            pd_ml = [i+j for (i,j) in zip(pd_ml, ml_correct)]
            
            # write the infected subgraph to file
            filename = 'infected_subgraph_'+str(trial)
            exportGraph.export_gexf(filename,who_infected,source,infection_pattern,adjacency)
            
        p += num_infected / (1.0 * num_true_nodes)
    p = p / trials
    # pd_jordan = [i / (1.0 * trials) for i in pd_jordan]
    pd_jordan = [i/j for (i,j) in zip(jordan_found, jordan_count) if j>0]
    pd_rumor = [i/j for (i,j) in zip(rumor_found, rumor_count) if j>0]
    pd_ml = [i / trials for i in pd_ml]
    # pd_rumor = [i / (1.0 * trials) for i in pd_rumor]
    # pd_rumor = pd_rumor/(1.0*num_true_nodes)
    return p, num_infected, pd_jordan, pd_rumor, pd_ml
    
'''Run a random tree'''    
def run_randtree(trials, max_time, max_infection, degree_rv):
    # Run dataset runs a spreading algorithm over a dataset. 
    # Inputs:
    #
    #       trials:                 number of trials to run
    #       max_time:               the maximum number of timesteps to use
    #       degree_rv:              remove all nodes with degree lower than min_degree
    #
    # Outputs:
    #
    #       p:                      average proportion of nodes reached by the algorithm 
    #       num_infected:           total number of nodes infected by the algorithm
    #
    # NB: If max_infection is not set, then we'll run the deterministic algorihtm. Otherwise, it's the message passing one.
    
    pd_ml = [0 for i in range(max_time)]
    
    for trial in range(trials):
        if trial % 10 == 0:
            print('Trial ',trial, ' / ',trials-1)
        source = 0
        num_infected, infection_pattern, who_infected, ml_correct = infectionModels.infect_nodes_adaptive_diff_irregular_tree(source, max_time, max_infection, degree_rv)
        # unpack the results
        
        pd_ml = [i+j for (i,j) in zip(pd_ml, ml_correct)]
        
    pd_ml = [i / trials for i in pd_ml]
    return num_infected, pd_ml