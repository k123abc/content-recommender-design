#%%
 
#   Written by "Kais Suleiman" (ksuleiman.weebly.com)
#
#   Notes:
#
#   - The contents of this script represent a tool used to generate 
#   different recommender category results given different experiment 
#   setups as explained in details in Chapter 5 of the thesis:
#    
#       Kais Suleiman, "Popular Content Distribution in Public 
#       Transportation Using Artificial Intelligence Techniques.", 
#       Ph.D. thesis, University of Waterloo, Ontario, Canada, 2019.
#
#   - Any experiment setup encoding can be used to differentiate between
#   the different results generated using this tool. For example, we can
#   use the encoding xyz such that x represents different group interest 
#   distribution standard deviations, y represents different unknown 
#   consumer interest ratios and z represents different network capacities. 
#   We can then specify that each of x, y and z would have a value of 1 
#   to represent a high value and a value of 0 to represent a low value. 
#   Therefore and using such encoding setup, 111 would represent 
#   an experiment setup with a high group interest distribution standard 
#   deviation, a high unknown consumer interests ratio and a high
#   network capacity. Refer to Table 5.1. of the thesis for further
#   clarification.
#   - Simpler but still similar variable names have been used throughout 
#   this script instead of the mathematical notations used in the thesis.
#   - The assumptions used in the script are the same as those used in the thesis.
#   - Figures are created throughout this script to aid 
#   in thesis visualizations and other forms of results sharing.

#%%

# To clear memory

for name in dir():
    if not name.startswith('_'):
        del globals()[name]
        
import random
import numpy as np
import matplotlib.pyplot as plt
import sys

random.seed(1)

#%%

#  Scenario assumptions:

number_of_consumers = 100
number_of_services = 20
number_of_groups = 2
group_interests_distribution_std = number_of_services / 10
unknown_interests_ratio = 0.1
xmin = 0
xmax = 1000
ymin = 0
ymax = 500
group_x_location_std = (xmax - xmin) / number_of_groups / 10
group_y_location_std = (ymax - ymin) / 10
duration = 100
network_capacity = number_of_services // 10

setup = 111 # Used to name result files 

#%%

#   Consumer interest distributions:

true_interests = \
    np.zeros((number_of_consumers, number_of_services))

for i in range(number_of_groups):
    
    first_group_consumer = \
        number_of_consumers // number_of_groups * i
    
    last_group_consumer = \
        number_of_consumers // number_of_groups * (i + 1)
    
    first_group_service = \
        number_of_services // number_of_groups * i
    
    last_group_service = \
        number_of_services // number_of_groups * (i + 1)
    
    for j in range(first_group_consumer, last_group_consumer):
        
        true_interests_indices = \
            np.floor(np.random.normal( \
                                        round((first_group_service + \
                                               last_group_service) / 2), \
                                            group_interests_distribution_std, \
                                                size = \
                                                    (1, number_of_services // number_of_groups)))
        
        true_interests_indices = \
            true_interests_indices[np.logical_and((true_interests_indices >= 0), \
                                   (true_interests_indices <= number_of_services - 1))]
        
        for index in true_interests_indices.astype(int):
            true_interests[j, index] = 1

#   Confirming that at least one service is truely liked per consumer:

for i in range(number_of_consumers):   
    
    if np.all(true_interests[i, :] == 0):    
        
        true_interests \
            [i, np.random.randint( \
                                  np.floor(i / (number_of_consumers // number_of_groups)) * \
                                      (number_of_services // number_of_groups) + 1, \
                                          (np.floor(i / (number_of_consumers // number_of_groups)) + 1) * \
                                              (number_of_services // number_of_groups), 1)] = 1 

available_interests = np.copy(true_interests)

for i in range(number_of_consumers):
    
    for j in range(number_of_services):
        
        if np.random.uniform(0, 1) < unknown_interests_ratio:
            
            available_interests[i, j] = np.NaN

#   Confirming that at least one service is known to be liked 
#   per consumer:

for i in range(number_of_consumers):
    
    for j in range(number_of_services):
        
        if np.sum(available_interests[i, np.where(~ np.isnan(available_interests[i, :]))]) == 0 \
            and np.isnan(available_interests[i, j]) \
                and true_interests[i, j]:
            
            available_interests[i, j] = true_interests[i, j]
            break

#%%

#   Interest distributions plotting:

group_popularities = \
    np.zeros((number_of_groups, number_of_services))

for i in range(number_of_groups):
    
    for j in range(number_of_services):
    
        group_popularities[i, j] = \
            np.nansum(true_interests[list(range(number_of_consumers // number_of_groups * i, \
            number_of_consumers // number_of_groups * (i + 1) - 1)), j])
    
figure, ax = plt.subplots(nrows = 1, ncols = 1)

cumulative_bottom = np.arange(number_of_services) * 0
cumulative_bottom = cumulative_bottom.astype(float)

for i in range(number_of_groups):
    chosen_color = np.random.randint(10, size = (1, 3)) / 10
    ax.bar(np.arange(number_of_services) + 1, \
           group_popularities[i, :], \
               bottom = cumulative_bottom, color = chosen_color)
    cumulative_bottom += group_popularities[i, :]

ax.set_title('Group interests')

max_service_popularity = 0

for i in range(number_of_services):
    
    max_service_popularity = \
        max(max_service_popularity, \
            np.sum(group_popularities[:, i]))

ax.set_xlim([0, number_of_services + 1])
ax.set_ylim([0, max_service_popularity + 1])
ax.set_xlabel('Services')
ax.set_ylabel('Number of consumers interested')
ax.grid(color = 'k', linestyle = '--', linewidth = 1)

figure.tight_layout()
figure.savefig('Group interest distributions with ' + \
               str(group_interests_distribution_std) + ' std.png', \
                   dpi = 500)

figure, ax = plt.subplots(nrows = 1, ncols = 1)

temp = ax.imshow(true_interests, interpolation = 'nearest', aspect='auto')
figure.colorbar(temp, ax = ax)

ax.set_title('True service interests matrix')
ax.set_xlabel('Services')
ax.set_ylabel('Consumers')

figure.tight_layout()
figure.savefig('True interest distributions with ' + \
                     str(group_interests_distribution_std) + ' std & ' + \
                         str(unknown_interests_ratio) + ' unknown ratio.png', \
               dpi = 500)

figure, ax = plt.subplots(nrows = 1, ncols = 1)

temp = ax.imshow(available_interests, interpolation = 'nearest', \
                 aspect='auto')
figure.colorbar(temp, ax = ax)

ax.set_title('Available service interests matrix')
ax.set_xlabel('Services')
ax.set_ylabel('Consumers')

figure.tight_layout()
figure.savefig('Available interest distributions with ' + \
                     str(group_interests_distribution_std) + ' std & ' + \
                         str(unknown_interests_ratio) + ' unknown ratio.png', \
               dpi = 500)
 
#%%

#   Consumer location distributions:

x_locations = np.zeros((1, number_of_consumers))
y_locations = np.zeros((1, number_of_consumers))

for i in range(number_of_groups):
    
    first_group_consumer = \
        number_of_consumers // number_of_groups * i
    
    last_group_consumer = \
        number_of_consumers // number_of_groups * (i + 1)
    
    group_x_location_mean = \
        (i * (xmax - xmin) / number_of_groups) + \
        (((i + 1) * (xmax - xmin) / number_of_groups) - \
        (i * (xmax - xmin) / number_of_groups)) / 2
    
    group_y_location_mean = (ymax - ymin) / 2
    
    x_locations[0, list(range(first_group_consumer, last_group_consumer))] = \
        np.random.normal(group_x_location_mean, group_x_location_std, \
                         (number_of_consumers // number_of_groups))
    
    y_locations[0, list(range(first_group_consumer, last_group_consumer))] = \
        np.random.normal(group_y_location_mean, group_y_location_std, \
                         (number_of_consumers // number_of_groups))

#%%

#   Location distributions plotting:

figure, ax = plt.subplots(nrows = 1, ncols = 1)
ax.scatter(x_locations, y_locations, color = 'yellow', \
           marker = 'o', edgecolors = 'black')
ax.set_xlim([xmin, xmax])
ax.set_ylim([ymin, ymax])
ax.set_title('Consumer locations')
ax.set_xlabel('X - axis (m)')
ax.set_ylabel('Y - axis (m)')
ax.grid(color = 'k', linestyle = '--', linewidth = 1)

figure.tight_layout()
figure.savefig('Location distributions.png', dpi = 500)

#%%

#   Category 1 with the non-interactive non-collaborative 
#   non-group-based recommender system:

c1_available_interests = np.copy(available_interests);

c1_available_interests_ratio = np.zeros((1, duration))

c1_true_popularities = \
    np.zeros((number_of_groups, number_of_services))
c1_true_most_popular_services = \
    np.zeros((number_of_groups, number_of_services))
c1_should_be_distributed_services = \
    np.zeros((number_of_groups, network_capacity))

number_of_group_consumers = \
    number_of_consumers // number_of_groups

for g in range(number_of_groups):
    
    first_group_consumer = number_of_group_consumers * g
    last_group_consumer = number_of_group_consumers * (g + 1)
    
    c1_true_popularities[g, :] = \
        np.sum(true_interests[list(range(first_group_consumer, \
                                         last_group_consumer)), :], \
               axis = 0)
    
    c1_true_most_popular_services[g, :] = \
        c1_true_popularities[g, :].argsort()[::-1]
    
    c1_should_be_distributed_services[g, :] = \
        c1_true_most_popular_services[g, list(range(network_capacity))]

c1_truely_popular_distributed_services_ratio = \
    np.zeros((number_of_groups, duration))
c1_total_truely_popular_distributed_services_ratio = \
    np.zeros((1, duration))

for t in range(duration):
    
    c1_available_interests_ratio[0, t] = \
        np.count_nonzero(~ np.isnan(c1_available_interests)) / \
            (number_of_consumers * number_of_services)

    c1_available_popularities = np.zeros((1, number_of_services))
    
    for i in range(number_of_services):

        c1_available_popularities[0, i] = \
            np.nansum(c1_available_interests[:, i])
    
    c1_available_most_popular_services = \
        (- c1_available_popularities).argsort()
        
    c1_distributed_services = \
        c1_available_most_popular_services[0, list(range(network_capacity))]
    
    for g in range(number_of_groups):
        
        c1_truely_popular_distributed_services_ratio[g, t] = \
            len(set(c1_distributed_services).intersection( \
                                                          c1_should_be_distributed_services[g, :])) \
                / np.shape(c1_distributed_services)[0]
    
    c1_total_truely_popular_distributed_services_ratio[0, t] = \
        np.sum(c1_truely_popular_distributed_services_ratio[:, t] * \
        network_capacity) / \
            (number_of_groups * network_capacity)
    
    sys.stdout.write('\r' + \
                     str("Please wait ... {:.2f}%".\
                         format(t / duration \
                                * 100)))
    sys.stdout.flush()

#%%

#   Category 1 summary results:

figure, ax = plt.subplots(nrows = 1, ncols = 1)
ax.plot(list(range(duration)), c1_available_interests_ratio[0],'--k', \
        label = 'Cat 1')
ax.legend(loc = 'best')
ax.set_title('Interests ratio vs. time')
ax.set_xlim([1, duration])
ax.set_ylim([0, 1.1])
ax.set_xlabel('Time interval')
ax.set_ylabel('Interests ratio')
ax.grid(color = 'k', linestyle = '--', linewidth = 1)

figure.tight_layout()
figure.savefig('c1-interests ratio-setup ' + str(setup) + '.png', \
               dpi = 500)

figure, ax = plt.subplots(nrows = 1, ncols = 1)
ax.plot(list(range(duration)), \
        c1_total_truely_popular_distributed_services_ratio[0],'--k', \
            label = 'Cat 1')
ax.legend(loc = 'best')
ax.set_title('Popular distributed services ratio vs. time')
ax.set_xlim([1, duration])
ax.set_ylim([0, 1.1])
ax.set_xlabel('Time interval')
ax.set_ylabel('Popular distributed services ratio')
ax.grid(color = 'k', linestyle = '--', linewidth = 1)

figure.tight_layout()
figure.savefig('c1-popular distributed services ratio-setup ' + \
                     str(setup) + '.png', dpi = 500)

#%%

#   Category 2.a with the greedy non-collaborative 
#   non-group-based recommender system:

c2a_available_interests = np.copy(available_interests);

c2a_available_interests_ratio = np.zeros((1, duration))

c2a_true_popularities = \
    np.zeros((number_of_groups, number_of_services))
c2a_true_most_popular_services = \
    np.zeros((number_of_groups, number_of_services))
c2a_should_be_distributed_services = \
    np.zeros((number_of_groups, network_capacity))

number_of_group_consumers = \
    number_of_consumers // number_of_groups

for g in range(number_of_groups):
    
    first_group_consumer = number_of_group_consumers * g
    last_group_consumer = number_of_group_consumers * (g + 1)
    
    c2a_true_popularities[g, :] = \
        np.sum(true_interests[list(range(first_group_consumer, \
                                         last_group_consumer)), :], \
               axis = 0)
    
    c2a_true_most_popular_services[g, :] = \
        (- c2a_true_popularities[g, :]).argsort()
    
    c2a_should_be_distributed_services[g, :] = \
        c2a_true_most_popular_services[g, list(range(network_capacity))]

c2a_truely_popular_distributed_services_ratio = \
    np.zeros((number_of_groups, duration))
c2a_total_truely_popular_distributed_services_ratio = \
    np.zeros((1, duration))

for t in range(duration):
    
    c2a_available_interests_ratio[0, t] = \
        np.count_nonzero(~ np.isnan(c2a_available_interests)) / \
            (number_of_consumers * number_of_services)
    
    c2a_available_popularities = np.zeros((1, number_of_services))
    
    for i in range(number_of_services):

        c2a_available_popularities[0, i] = \
            np.nansum(c2a_available_interests[:, i])
    
    c2a_available_most_popular_services = \
        (- c2a_available_popularities).argsort()
        
    c2a_distributed_services = \
        c2a_available_most_popular_services[0, list(range(network_capacity))]
    
    for g in range(number_of_groups):
        
        c2a_truely_popular_distributed_services_ratio[g, t] = \
            len(set(c2a_distributed_services).intersection( \
                                                           c2a_should_be_distributed_services[g, :])) \
                / np.shape(c2a_distributed_services)[0]
    
    c2a_total_truely_popular_distributed_services_ratio[0, t] = \
        np.sum(c2a_truely_popular_distributed_services_ratio[:, t] * \
        network_capacity) / \
            (number_of_groups * network_capacity)
    
    for i in range(number_of_consumers):
        
        c2a_available_interests[i, c2a_distributed_services] = \
            true_interests[i, c2a_distributed_services]
    
    sys.stdout.write('\r' + \
                     str("Please wait ... {:.2f}%".\
                         format(t / duration \
                                * 100)))
    sys.stdout.flush()

#%%

#   Category 2.b with the epsilon-greedy non-collaborative 
#   non-group-based recommender system:

c2b_available_interests = np.copy(available_interests)

c2b_available_interests_ratio = np.zeros((1, duration))

c2b_true_popularities = \
    np.zeros((number_of_groups, number_of_services))
c2b_true_most_popular_services = \
    np.zeros((number_of_groups, number_of_services))
c2b_should_be_distributed_services = \
    np.zeros((number_of_groups, network_capacity))

number_of_group_consumers = \
    number_of_consumers // number_of_groups

for g in range(number_of_groups):
    
    first_group_consumer = number_of_group_consumers * g
    last_group_consumer = number_of_group_consumers * (g + 1)
    
    c2b_true_popularities[g, :] = \
        np.sum(true_interests[list(range(first_group_consumer, \
                                         last_group_consumer)), :], \
               axis = 0)
    
    c2b_true_most_popular_services[g, :] = \
        (- c2b_true_popularities[g, :]).argsort()
    
    c2b_should_be_distributed_services[g, :] = \
        c2b_true_most_popular_services[g, list(range(network_capacity))]

c2b_truely_popular_distributed_services_ratio = \
    np.zeros((number_of_groups, duration))
c2b_total_truely_popular_distributed_services_ratio = \
    np.zeros((1, duration))

for t in range(duration):
    
    c2b_available_interests_ratio[0, t] = \
        np.count_nonzero(~ np.isnan(c2b_available_interests)) / \
        (number_of_consumers * number_of_services)

    c2b_available_popularities = np.zeros((1, number_of_services))

    for i in range(number_of_services):
        
        c2b_available_popularities[0, i] = \
            np.nansum(c2b_available_interests[:, i])
    
    c2b_available_most_popular_services = \
        (- c2b_available_popularities).argsort()
    
    epsilon = unknown_interests_ratio
    
    c2b_distributed_services = \
        c2b_available_most_popular_services[0, \
                                            list(range(np.floor(network_capacity * (1 - epsilon)).astype(int)))]
    
    c2b_distributed_services = np.concatenate((c2b_distributed_services, \
        c2b_available_most_popular_services \
        [0, np.random.randint(np.floor(network_capacity * (1 - epsilon)).astype(int) + 1, number_of_services, \
        size = (1, network_capacity - np.floor(network_capacity * (1 - epsilon)).astype(int)))[0]]), axis = 0)

    for g in range(number_of_groups):
        
        c2b_truely_popular_distributed_services_ratio[g, t] = \
            len(set(c2b_distributed_services).intersection( \
                                                           c2b_should_be_distributed_services[g, :])) \
                / np.shape(c2b_distributed_services)[0]
    
    c2b_total_truely_popular_distributed_services_ratio[0, t] = \
        np.sum(c2b_truely_popular_distributed_services_ratio[:, t] * \
               network_capacity) / \
            (number_of_groups * network_capacity)
    
    for i in range(number_of_consumers):
        
        c2b_available_interests[i, c2b_distributed_services] = \
            true_interests[i, c2b_distributed_services]
    
    sys.stdout.write('\r' + \
                     str("Please wait ... {:.2f}%".\
                         format(t / duration \
                                * 100)))
    sys.stdout.flush()

#%%

#   Category 2.c with the decaying epsilon-greedy non-collaborative 
#   non-group-based recommender system:

c2c_available_interests = np.copy(available_interests)

c2c_available_interests_ratio = np.zeros((1, duration))

c2c_true_popularities = \
    np.zeros((number_of_groups, number_of_services))
c2c_true_most_popular_services = \
    np.zeros((number_of_groups, number_of_services))
c2c_should_be_distributed_services = \
    np.zeros((number_of_groups, network_capacity))

number_of_group_consumers = \
    number_of_consumers // number_of_groups

for g in range(number_of_groups):
    
    first_group_consumer = number_of_group_consumers * g
    last_group_consumer = number_of_group_consumers * (g + 1)
    
    c2c_true_popularities[g, :] = \
        np.sum(true_interests[list(range(first_group_consumer, \
                                         last_group_consumer)), :], \
               axis = 0)
    
    c2c_true_most_popular_services[g, :] = \
        (- c2c_true_popularities[g, :]).argsort()
    
    c2c_should_be_distributed_services[g, :] = \
        c2c_true_most_popular_services[g, list(range(network_capacity))]

c2c_truely_popular_distributed_services_ratio = \
    np.zeros((number_of_groups, duration))
c2c_total_truely_popular_distributed_services_ratio = \
    np.zeros((1, duration))

for t in range(duration):
    
    c2c_available_interests_ratio[0, t] = \
        np.count_nonzero(~ np.isnan(c2c_available_interests)) / \
            (number_of_consumers * number_of_services)
    
    c2c_available_popularities = np.zeros((1, number_of_services))
    
    for i in range(number_of_services):
        
        c2c_available_popularities[0, i] = \
            np.nansum(c2c_available_interests[:, i])
    
    c2c_available_most_popular_services = \
        (- c2c_available_popularities).argsort()
    
    epsilon = 1 - c2c_available_interests_ratio[0, t]
    
    c2c_distributed_services = \
        c2c_available_most_popular_services[0, list(range(np.floor(network_capacity * (1 - epsilon)).astype(int)))]
    
    c2c_distributed_services = np.concatenate((c2c_distributed_services, \
        c2c_available_most_popular_services \
        [0, np.random.randint(np.floor(network_capacity * (1 - epsilon)).astype(int) + 1, number_of_services, \
        size = (1, network_capacity - np.floor(network_capacity * (1 - epsilon)).astype(int)))[0]]), axis = 0)

    for g in range(number_of_groups):
        
        c2c_truely_popular_distributed_services_ratio[g, t] = \
            len(set(c2c_distributed_services).intersection( \
                                                           c2c_should_be_distributed_services[g, :])) \
                / np.shape(c2c_distributed_services)[0]
    
    c2c_total_truely_popular_distributed_services_ratio[0, t] = \
        np.sum(c2c_truely_popular_distributed_services_ratio[:, t] * \
               network_capacity) / \
            (number_of_groups * network_capacity)
    
    for i in range(number_of_consumers):
        
        c2c_available_interests[i, c2c_distributed_services] = \
            true_interests[i, c2c_distributed_services]
    
    sys.stdout.write('\r' + \
                     str("Please wait ... {:.2f}%".\
                         format(t / duration \
                                * 100)))
    sys.stdout.flush()

#%%

#   Category 2.d with the Upper-Popularity-Bound non-collaborative
#   non-group-based recommender system:

c2d_available_interests = np.copy(available_interests)

c2d_available_interests_ratio = np.zeros((1, duration))

c2d_true_popularities = \
    np.zeros((number_of_groups, number_of_services))
c2d_true_most_popular_services = \
    np.zeros((number_of_groups, number_of_services))
c2d_should_be_distributed_services = \
    np.zeros((number_of_groups, network_capacity))

number_of_group_consumers = \
    number_of_consumers // number_of_groups

for g in range(number_of_groups):
    
    first_group_consumer = number_of_group_consumers * g
    last_group_consumer = number_of_group_consumers * (g + 1)
    
    c2d_true_popularities[g, :] = \
        np.sum(true_interests[list(range(first_group_consumer, \
                                         last_group_consumer)), :], \
               axis = 0)
    
    c2d_true_most_popular_services[g, :] = \
        (- c2d_true_popularities[g, :]).argsort()
    
    c2d_should_be_distributed_services[g, :] = \
        c2d_true_most_popular_services[g, list(range(network_capacity))]

c2d_truely_popular_distributed_services_ratio = \
    np.zeros((number_of_groups, duration))
c2d_total_truely_popular_distributed_services_ratio = \
    np.zeros((1, duration))

for t in range(duration):
    
    c2d_available_interests_ratio[0, t] = \
        np.count_nonzero(~ np.isnan(c2d_available_interests)) / \
            (number_of_consumers * number_of_services)
        
    c2d_available_popularities = \
        np.zeros((1, number_of_services))
    c2d_upper_available_popularity_bounds = \
        np.zeros((1, number_of_services))
    
    for i in range(number_of_services):
        
        c2d_available_popularities[0, i] = \
            np.nansum(c2d_available_interests[:, i])
        
        c2d_upper_available_popularity_bounds[0, i] = \
            c2d_available_popularities[0, i] + \
                np.count_nonzero(np.isnan(c2d_available_interests[:, i]))
    
    c2d_available_most_popular_services = \
        (- c2d_upper_available_popularity_bounds).argsort()
        
    c2d_distributed_services = \
        c2d_available_most_popular_services[0, list(range(network_capacity))]
    
    for g in range(number_of_groups):
        
        c2d_truely_popular_distributed_services_ratio[g, t] = \
            len(set(c2d_distributed_services).intersection( \
                                                           c2d_should_be_distributed_services[g, :])) \
                / np.shape(c2d_distributed_services)[0]
    
    c2d_total_truely_popular_distributed_services_ratio[0, t] = \
        np.sum(c2d_truely_popular_distributed_services_ratio[:, t] * \
               network_capacity) / \
            (number_of_groups * network_capacity)
    
    for i in range(number_of_consumers):
        
        c2d_available_interests[i, c2d_distributed_services] = \
            true_interests[i, c2d_distributed_services]
    
    sys.stdout.write('\r' + \
                     str("Please wait ... {:.2f}%".\
                         format(t / duration \
                                * 100)))
    sys.stdout.flush()

#%%

#   Category 2 summary results:

figure, ax = plt.subplots(nrows = 1, ncols = 1)
ax.plot(list(range(duration)), c2a_available_interests_ratio[0], '-+b', \
        label = 'Cat 2 - Greedy')
ax.plot(list(range(duration)), c2b_available_interests_ratio[0], '-*g', \
        label = 'Cat 2 - e-greedy')
ax.plot(list(range(duration)), c2c_available_interests_ratio[0], '-xr', \
        label = 'Cat 2 - Decaying e-greedy')
ax.plot(list(range(duration)), c2d_available_interests_ratio[0], '-ok', \
        label = 'Cat 2 - UPB')
ax.legend(loc = 'best')
ax.set_title('Interests ratio vs. time')
ax.set_xlim([1, duration])
ax.set_ylim([0, 1.1])
ax.set_xlabel('Time interval')
ax.set_ylabel('Interests ratio')
ax.grid(color = 'k', linestyle = '--', linewidth = 1)

figure.tight_layout()
figure.savefig('c2-interests ratio-setup ' + str(setup) + '.png', \
               dpi = 500)

figure, ax = plt.subplots(nrows = 1, ncols = 1)
ax.plot(list(range(duration)), c2a_total_truely_popular_distributed_services_ratio[0], \
        '-+b', label = 'Cat 2 - Greedy')
ax.plot(list(range(duration)), c2b_total_truely_popular_distributed_services_ratio[0], \
        '-*g', label = 'Cat 2 - e-greedy')
ax.plot(list(range(duration)), c2c_total_truely_popular_distributed_services_ratio[0], \
        '-xr', label = 'Cat 2 - Decaying e-greedy')
ax.plot(list(range(duration)), c2d_total_truely_popular_distributed_services_ratio[0], \
        '-ok', label = 'Cat 2 - UPB')
ax.legend(loc = 'best')
ax.set_title('Popular distributed services ratio vs. time')
ax.set_xlim([1, duration])
ax.set_ylim([0, 1.1])
ax.set_xlabel('Time interval')
ax.set_ylabel('Popular distributed services ratio')
ax.grid(color = 'k', linestyle = '--', linewidth = 1)

figure.tight_layout()
figure.savefig('c2-popular distributed services ratio-setup ' + \
               str(setup) + '.png', \
               dpi = 500)

#%%

#   The generateNGBRecommendations function:

def generateNGBRecommendations(number_of_consumers, \
                               number_of_services, \
                                   available_interests):
    
    jaccard_similarities = \
        np.zeros((number_of_consumers,number_of_consumers))
    
    for i in range(number_of_consumers):
        
        for j in range(number_of_consumers):
            
            if i == j:
                
                continue
                
            else:
                
                jaccard_similarities[i, j] = \
                    np.shape(np.where(available_interests[i, :] == \
                           available_interests[j, :]))[0] \
                        / number_of_services
    
    recommended_interests = np.copy(available_interests)
    
    for i in range(number_of_consumers):
        
        for j in range(number_of_services):
            
            if np.isnan(recommended_interests[i, j]):
                
                most_similar_consumers = \
                    np.where(jaccard_similarities[i, :] == \
                             np.amax(jaccard_similarities[i, :]))
                
                recommended_interests[i, j] = \
                    recommended_interests[most_similar_consumers[0][0], j]

    return recommended_interests

#%%

#   Category 3.a with the greedy collaborative
#   non-group-based recommender system:

c3a_available_interests = np.copy(available_interests)

c3a_available_interests_ratio = np.zeros((1, duration))
c3a_recommended_interests_ratio = np.zeros((1, duration))

c3a_true_popularities = \
    np.zeros((number_of_groups, number_of_services))
c3a_true_most_popular_services = \
    np.zeros((number_of_groups, number_of_services))
c3a_should_be_distributed_services = \
    np.zeros((number_of_groups, network_capacity))

number_of_group_consumers = \
    number_of_consumers // number_of_groups

for g in range(number_of_groups):
    
    first_group_consumer = \
        number_of_group_consumers * g
    last_group_consumer = \
        number_of_group_consumers * (g + 1)
    
    c3a_true_popularities[g, :] = \
        np.sum(true_interests[list(range(first_group_consumer, \
                                         last_group_consumer)), :], \
               axis = 0)
    
    c3a_true_most_popular_services[g, :] = \
        (- c3a_true_popularities[g, :]).argsort()
    
    c3a_should_be_distributed_services[g, :] = \
        c3a_true_most_popular_services[g, list(range(network_capacity))]

c3a_truely_popular_distributed_services_ratio = \
    np.zeros((number_of_groups, duration))
c3a_total_truely_popular_distributed_services_ratio = \
    np.zeros((1, duration))

for t in range(duration):
    
    c3a_available_interests_ratio[0, t] = \
        np.count_nonzero(~ np.isnan(c3a_available_interests)) / \
            (number_of_consumers * number_of_services)
    
    c3a_recommended_interests = \
        generateNGBRecommendations( \
                                   number_of_consumers, \
                                       number_of_services, \
                                           c3a_available_interests)
    
    c3a_recommended_interests_ratio[0, t] = \
        np.shape(np.where(c3a_recommended_interests == true_interests))[1] / \
        (number_of_consumers * number_of_services)

    c3a_recommended_popularities = np.zeros((1, number_of_services))
    
    for i in range(number_of_services):
        
        c3a_recommended_popularities[0, i] = \
            np.nansum(c3a_recommended_interests[:, i])

    c3a_recommended_most_popular_services = \
        (- c3a_recommended_popularities).argsort()
    
    c3a_distributed_services = \
        c3a_recommended_most_popular_services[0, list(range(network_capacity))]
    
    for g in range(number_of_groups):
        
        c3a_truely_popular_distributed_services_ratio[g, t] = \
            len(set(c3a_distributed_services).intersection( \
                                                           c3a_should_be_distributed_services[g, :])) \
                / np.shape(c3a_distributed_services)[0]
    
    c3a_total_truely_popular_distributed_services_ratio[0, t] = \
        np.sum(c3a_truely_popular_distributed_services_ratio[:, t] * \
               network_capacity) / \
            (number_of_groups * network_capacity)
    
    for i in range(number_of_consumers):
        
        c3a_available_interests[i, c3a_distributed_services] = \
            true_interests[i, c3a_distributed_services]
    
    sys.stdout.write('\r' + \
                     str("Please wait ... {:.2f}%".\
                         format(t / duration \
                                * 100)))
    sys.stdout.flush()

#%%

#   Category 3.b with the epsilon-greedy collaborative
#   non-group-based recommender system:

c3b_available_interests = np.copy(available_interests)

c3b_available_interests_ratio = np.zeros((1, duration))
c3b_recommended_interests_ratio = np.zeros((1, duration))

c3b_true_popularities = \
    np.zeros((number_of_groups, number_of_services))
c3b_true_most_popular_services = \
    np.zeros((number_of_groups, number_of_services))
c3b_should_be_distributed_services = \
    np.zeros((number_of_groups, network_capacity))

number_of_group_consumers = \
    number_of_consumers // number_of_groups

for g in range(number_of_groups):
    
    first_group_consumer = number_of_group_consumers * g
    last_group_consumer = number_of_group_consumers * (g + 1)
    
    c3b_true_popularities[g, :] = \
        np.sum(true_interests[list(range(first_group_consumer, \
                                         last_group_consumer)), :], \
               axis = 0)
    
    c3b_true_most_popular_services[g, :] = \
        (- c3b_true_popularities[g, :]).argsort()
    
    c3b_should_be_distributed_services[g, :] = \
        c3b_true_most_popular_services[g, list(range(network_capacity))]

c3b_truely_popular_distributed_services_ratio = \
    np.zeros((number_of_groups, duration))
c3b_total_truely_popular_distributed_services_ratio = \
    np.zeros((1, duration))

for t in range(duration):
    
    c3b_available_interests_ratio[0, t] = \
        np.count_nonzero(~ np.isnan(c3b_available_interests)) / \
            (number_of_consumers * number_of_services)
        
    c3b_recommended_interests = \
        generateNGBRecommendations( \
                                   number_of_consumers, \
                                       number_of_services, \
                                           c3b_available_interests)

    c3b_recommended_interests_ratio[0, t] = \
        np.shape(np.where(c3b_recommended_interests == true_interests))[1] / \
            (number_of_consumers * number_of_services)

    c3b_recommended_popularities = np.zeros((1, number_of_services))
    
    for i in range(number_of_services):
        
        c3b_recommended_popularities[0, i] = \
            np.nansum(c3b_recommended_interests[:, i])
    
    c3b_recommended_most_popular_services = \
        (- c3b_recommended_popularities).argsort()
    
    epsilon = unknown_interests_ratio
    
    c3b_distributed_services = \
        c3b_recommended_most_popular_services[0, list(range(np.floor(network_capacity * (1 - epsilon)).astype(int)))]
        
    c3b_distributed_services = np.concatenate((c3b_distributed_services, \
        c3b_recommended_most_popular_services \
        [0, np.random.randint(np.floor(network_capacity * (1 - epsilon)).astype(int) + 1, number_of_services, \
        size = (1, network_capacity - np.floor(network_capacity * (1 - epsilon)).astype(int)))[0]]), axis = 0)

    for g in range(number_of_groups):
        
        c3b_truely_popular_distributed_services_ratio[g, t] = \
            len(set(c3b_distributed_services).intersection( \
                                                           c3b_should_be_distributed_services[g, :])) \
                / np.shape(c3b_distributed_services)[0]
    
    c3b_total_truely_popular_distributed_services_ratio[0, t] = \
        np.sum(c3b_truely_popular_distributed_services_ratio[:, t] * \
               network_capacity) / \
            (number_of_groups * network_capacity)
    
    for i in range(number_of_consumers):
        
        c3b_available_interests[i, c3b_distributed_services] = \
            true_interests[i, c3b_distributed_services]
    
    sys.stdout.write('\r' + \
                     str("Please wait ... {:.2f}%".\
                         format(t / duration \
                                * 100)))
    sys.stdout.flush()

#%%

#   Category 3.c with the decaying epsilon-greedy collaborative
#   non-group-based recommender system:

c3c_available_interests = np.copy(available_interests)

c3c_available_interests_ratio = np.zeros((1, duration))
c3c_recommended_interests_ratio = np.zeros((1, duration))

c3c_true_popularities = \
    np.zeros((number_of_groups, number_of_services))
c3c_true_most_popular_services = \
    np.zeros((number_of_groups, number_of_services))
c3c_should_be_distributed_services = \
    np.zeros((number_of_groups, network_capacity))

number_of_group_consumers = \
    number_of_consumers // number_of_groups

for g in range(number_of_groups):
    
    first_group_consumer = number_of_group_consumers * g
    last_group_consumer = number_of_group_consumers * (g + 1)
    
    c3c_true_popularities[g, :] = \
        np.sum(true_interests[list(range(first_group_consumer, \
                                         last_group_consumer)), :], \
               axis = 0)
    
    c3c_true_most_popular_services[g, :] = \
        (- c3c_true_popularities[g, :]).argsort()
    
    c3c_should_be_distributed_services[g, :] = \
        c3c_true_most_popular_services[g, \
                                       list(range(network_capacity))]

c3c_truely_popular_distributed_services_ratio = \
    np.zeros((number_of_groups, duration))
c3c_total_truely_popular_distributed_services_ratio = \
    np.zeros((1, duration))

for t in range(duration):
    
    c3c_available_interests_ratio[0, t] = \
        np.count_nonzero(~ np.isnan(c3c_available_interests)) / \
            (number_of_consumers * number_of_services)
    
    c3c_recommended_interests = \
        generateNGBRecommendations( \
                                   number_of_consumers, \
                                       number_of_services, \
                                           c3c_available_interests)

    c3c_recommended_interests_ratio[0, t] = \
        np.shape(np.where(c3c_recommended_interests == \
                               true_interests))[1] / \
        (number_of_consumers * number_of_services)

    c3c_recommended_popularities = \
        np.zeros((1, number_of_services))
    
    for i in range(number_of_services):
        
        c3c_recommended_popularities[0, i] = \
            np.nansum(c3c_recommended_interests[:, i])
    
    c3c_recommended_most_popular_services = \
        (- c3c_recommended_popularities).argsort()
    
    epsilon = 1 - c3c_available_interests_ratio[0, t]
    
    c3c_distributed_services = \
        c3c_recommended_most_popular_services[0, list(range(np.floor(network_capacity * (1 - epsilon)).astype(int)))]
            
    c3c_distributed_services = np.concatenate((c3c_distributed_services, \
        c3c_recommended_most_popular_services \
        [0, np.random.randint(np.floor(network_capacity * (1 - epsilon)).astype(int) + 1, number_of_services, \
        size = (1, network_capacity - np.floor(network_capacity * (1 - epsilon)).astype(int)))[0]]), axis = 0)

    for g in range(number_of_groups):
        
        c3c_truely_popular_distributed_services_ratio[g, t] = \
            len(set(c3c_distributed_services).intersection( \
                                                           c3c_should_be_distributed_services[g, :])) \
                / np.shape(c3c_distributed_services)[0]
    
    c3c_total_truely_popular_distributed_services_ratio[0, t] = \
        np.sum(c3c_truely_popular_distributed_services_ratio[:, t] * \
               network_capacity) / \
            (number_of_groups * network_capacity)
    
    for i in range(number_of_consumers):
        
        c3c_available_interests[i, c3c_distributed_services] = \
            true_interests[i, c3c_distributed_services]
    
    sys.stdout.write('\r' + \
                     str("Please wait ... {:.2f}%".\
                         format(t / duration \
                                * 100)))
    sys.stdout.flush()

#%%

#   Category 3.d with the Upper-Popularity-Bound collaborative
#   non-group-based recommender system:

c3d_available_interests = np.copy(available_interests)

c3d_available_interests_ratio = np.zeros((1, duration))
c3d_recommended_interests_ratio = np.zeros((1, duration))

c3d_true_popularities = \
    np.zeros((number_of_groups, number_of_services))
c3d_true_most_popular_services = \
    np.zeros((number_of_groups, number_of_services))
c3d_should_be_distributed_services = \
    np.zeros((number_of_groups, network_capacity))

number_of_group_consumers = \
    number_of_consumers // number_of_groups

for g in range(number_of_groups):
    
    first_group_consumer = number_of_group_consumers * g
    last_group_consumer = number_of_group_consumers * (g + 1)
    
    c3d_true_popularities[g, :] = \
        np.sum(true_interests[list(range(first_group_consumer, \
                                         last_group_consumer)), :], \
               axis = 0)
    
    c3d_true_most_popular_services[g, :] = \
        (- c3d_true_popularities[g, :]).argsort()
    
    c3d_should_be_distributed_services[g, :] = \
        c3d_true_most_popular_services[g, list(range(network_capacity))]

c3d_truely_popular_distributed_services_ratio = \
    np.zeros((number_of_groups, duration))
c3d_total_truely_popular_distributed_services_ratio = \
    np.zeros((1, duration))

for t in range(duration):
    
    c3d_available_interests_ratio[0, t] = \
        np.count_nonzero(~ np.isnan(c3d_available_interests)) / \
            (number_of_consumers * number_of_services)
        
    c3d_recommended_interests = \
        generateNGBRecommendations( \
                                   number_of_consumers, \
                                       number_of_services, \
                                           c3d_available_interests);
    
    c3d_recommended_interests_ratio[0, t] = \
        np.shape(np.where(c3d_recommended_interests == true_interests))[1] / \
            (number_of_consumers * number_of_services)

    c3d_recommended_popularities = \
        np.zeros((1, number_of_services))
    c3d_upper_recommended_popularity_bounds = \
        np.zeros((1, number_of_services))
    
    for i in range(number_of_services):
        
        c3d_recommended_popularities[0, i] = \
            np.nansum(c3d_recommended_interests[:, i])
                        
        c3d_upper_recommended_popularity_bounds[0, i] = \
            c3d_recommended_popularities[0, i] + \
                np.count_nonzero(np.isnan(c3d_recommended_interests[:, i]))

    c3d_recommended_most_popular_services = \
        (- c3d_upper_recommended_popularity_bounds).argsort()
    
    c3d_distributed_services = \
        c3d_recommended_most_popular_services[0, list(range(network_capacity))]
    
    for g in range(number_of_groups):
        
        c3d_truely_popular_distributed_services_ratio[g, t] = \
            len(set(c3d_distributed_services).intersection( \
                                                           c3d_should_be_distributed_services[g, :])) / \
                np.shape(c3d_distributed_services)[0]
    
    c3d_total_truely_popular_distributed_services_ratio[0, t] = \
        np.sum(c3d_truely_popular_distributed_services_ratio[:, t] * \
               network_capacity) / \
            (number_of_groups * network_capacity)
    
    for i in range(number_of_consumers):
        
        c3d_available_interests[i, c3d_distributed_services] = \
            true_interests[i, c3d_distributed_services]
    
    sys.stdout.write('\r' + \
                     str("Please wait ... {:.2f}%".\
                         format(t / duration \
                                * 100)))
    sys.stdout.flush()

#%%

#%   Category 3 summary results:

figure, ax = plt.subplots(nrows = 1, ncols = 1)
ax.plot(list(range(duration)), c3a_recommended_interests_ratio[0], \
        '-+b', label = 'Cat 3 - Greedy');
ax.plot(list(range(duration)), c3b_recommended_interests_ratio[0], \
        '-*g', label = 'Cat 3 - e-greedy');
ax.plot(list(range(duration)), c3c_recommended_interests_ratio[0], \
        '-xr', label = 'Cat 3 - Decaying e-greedy');
ax.plot(list(range(duration)), c3d_recommended_interests_ratio[0], \
        '-ok', label = 'Cat 3 - UPB');
ax.legend(loc = 'best')
ax.set_title('Interests ratio vs. time')
ax.set_xlim([1, duration])
ax.set_ylim([0, 1.1])
ax.set_xlabel('Time interval')
ax.set_ylabel('Interests ratio')
ax.grid(color = 'k', linestyle = '--', linewidth = 1)

figure.tight_layout()
figure.savefig('c3-interests ratio-setup ' + str(setup) + '.png', \
               dpi = 500)

figure, ax = plt.subplots(nrows = 1, ncols = 1)
ax.plot(list(range(duration)), c3a_total_truely_popular_distributed_services_ratio[0], \
        '-+b', label = 'Cat 3 - Greedy')
ax.plot(list(range(duration)), c3b_total_truely_popular_distributed_services_ratio[0], \
        '-*g', label = 'Cat 3 - e-greedy')
ax.plot(list(range(duration)), c3c_total_truely_popular_distributed_services_ratio[0], \
        '-xr', label = 'Cat 3 - Decaying e-greedy')
ax.plot(list(range(duration)), c3d_total_truely_popular_distributed_services_ratio[0], \
        '-ok', label = 'Cat 3 - UPB')
ax.legend(loc = 'best')
ax.set_title('Popular distributed services ratio vs. time')
ax.set_xlim([1, duration])
ax.set_ylim([0, 1.1])
ax.set_xlabel('Time interval')
ax.set_ylabel('Popular distributed services ratio')
ax.grid(color = 'k', linestyle = '--', linewidth = 1)

figure.tight_layout()
figure.savefig('c3-popular distributed services ratio-setup ' + \
               str(setup) + '.png', \
               dpi = 500)

#%%

#   The generateGBRecommendations function:

def generateGBRecommendations(number_of_group_consumers, \
                              group_index, number_of_services, \
                                  available_interests, \
                                      recommended_interests):

    jaccard_similarities = \
        np.zeros((number_of_group_consumers, number_of_group_consumers))
        
    for i in range(number_of_group_consumers):
            
        for j in range(number_of_group_consumers):
                
            if i == j:
                    
                continue
                    
            else:
                    
                jaccard_similarities[i, j] = \
                    np.shape(np.where(available_interests[group_index, i, :] == \
                                      available_interests[group_index, j, :]))[0] / \
                        number_of_services

    recommended_interests[group_index, :, :] = \
        available_interests[group_index, :, :]
        
    for i in range(number_of_group_consumers):
            
        for j in range(number_of_services):
                
            if np.isnan(recommended_interests[group_index, i, j]):
                    
                most_similar_consumers = \
                    np.where(jaccard_similarities[i, :] == \
                             np.amax(jaccard_similarities[i, :]))
                    
                recommended_interests[group_index, i, j] = \
                    recommended_interests[group_index, most_similar_consumers[0][0],j]

    return recommended_interests

#%%

#   Category 4.a with the greedy collaborative 
#   group-based recommender system:

number_of_group_consumers = \
    number_of_consumers // number_of_groups

c4a_available_interests = \
    np.zeros((number_of_groups, \
              number_of_group_consumers, \
                 number_of_services))
c4a_true_interests = \
    np.zeros((number_of_groups, \
          number_of_group_consumers, \
              number_of_services))

for g in range(number_of_groups):
    
    first_group_consumer = number_of_group_consumers * g
    last_group_consumer = number_of_group_consumers * (g + 1)
    
    c4a_available_interests[g, :, :] = \
        available_interests[list(range(first_group_consumer, \
                                       last_group_consumer)), :]
            
    c4a_true_interests[g, :, :] = \
        true_interests[list(range(first_group_consumer, \
                                  last_group_consumer)), :]

c4a_available_interests_ratio = \
    np.zeros((number_of_groups, duration))
c4a_recommended_interests = \
    np.zeros((number_of_groups, \
              number_of_group_consumers, \
                  number_of_services))
c4a_recommended_interests_ratio = \
    np.zeros((number_of_groups, duration))

c4a_recommended_popularities = \
    np.zeros((number_of_groups, number_of_services))
c4a_recommended_most_popular_services = \
    np.zeros((number_of_groups, number_of_services))
c4a_distributed_services = \
    np.zeros((number_of_groups, network_capacity))

c4a_true_popularities = \
    np.zeros((number_of_groups, number_of_services))
c4a_true_most_popular_services = \
    np.zeros((number_of_groups, number_of_services))
c4a_should_be_distributed_services = \
    np.zeros((number_of_groups, network_capacity))

for g in range(number_of_groups):

    c4a_true_popularities[g, :] = \
        np.sum(c4a_true_interests[g, :, :], axis = 0)
    
    c4a_true_most_popular_services[g, :] = \
        (- c4a_true_popularities[g, :]).argsort()
    
    c4a_should_be_distributed_services[g, :] = \
        c4a_true_most_popular_services[g, list(range(network_capacity))]

c4a_truely_popular_distributed_services_ratio = \
    np.zeros((number_of_groups, duration))

for g in range(number_of_groups):
    
    for t in range(duration):
        
        c4a_available_interests_ratio[g, t] = \
            np.count_nonzero(~ np.isnan(c4a_available_interests[g, :, :])) / \
                (number_of_group_consumers * number_of_services)
        
        c4a_recommended_interests = generateGBRecommendations(number_of_group_consumers, \
                                                              g, \
                                                                  number_of_services, \
                                                                      c4a_available_interests, \
                                                                          c4a_recommended_interests)
                   
        c4a_recommended_interests_ratio[g, t] = \
            np.shape(np.where(c4a_recommended_interests[g, :, :] == \
                              c4a_true_interests[g, :, :]))[1] / \
                (number_of_group_consumers * number_of_services)
        
        for i in range(number_of_services):
            
            c4a_recommended_popularities[g, i] = \
                np.nansum(c4a_recommended_interests[g, :, i])
        
        c4a_recommended_most_popular_services[g, :] = \
            (- c4a_recommended_popularities[g, :]).argsort()
        
        c4a_distributed_services[g, :] = \
            c4a_recommended_most_popular_services[g, \
                                                  list(range(network_capacity))]
        
        c4a_truely_popular_distributed_services_ratio[g, t] = \
            len(set(c4a_distributed_services[g, :]).intersection( \
                                                                 c4a_should_be_distributed_services[g, :])) / \
                np.shape(c4a_distributed_services[g, :])[0]
        
        for i in range(number_of_group_consumers):
            
            c4a_available_interests[g, i, c4a_distributed_services[g, :].astype(int)] = \
                c4a_true_interests[g, i, c4a_distributed_services[g, :].astype(int)]
        
        sys.stdout.write('\r' + \
                         str("Please wait ... {:.2f}%".\
                             format((g * duration + t) / \
                                    (number_of_groups * duration) \
                                    * 100)))
        sys.stdout.flush()
    
c4a_total_recommended_interests_ratio = \
    np.sum(c4a_recommended_interests_ratio * \
           (number_of_group_consumers * number_of_services), axis = 0) \
        / (number_of_consumers * number_of_services)

c4a_total_truely_popular_distributed_services_ratio = \
    np.sum(c4a_truely_popular_distributed_services_ratio * \
           network_capacity, axis = 0) / (number_of_groups * network_capacity)

#%%

#   Category 4.b with the epsilon-greedy collaborative
#   group-based recommender system:

number_of_group_consumers = \
    number_of_consumers // number_of_groups

c4b_available_interests = \
    np.zeros((number_of_groups, \
              number_of_group_consumers, \
                  number_of_services))
c4b_true_interests = \
    np.zeros((number_of_groups, \
              number_of_group_consumers, \
                  number_of_services))

for g in range(number_of_groups):
    
    first_group_consumer = number_of_group_consumers * g
    last_group_consumer = number_of_group_consumers * (g + 1)
    
    c4b_available_interests[g, :, :] = \
        available_interests[list(range(first_group_consumer, \
                                       last_group_consumer)), :]
            
    c4b_true_interests[g, :, :] = \
        true_interests[list(range(first_group_consumer, \
                                  last_group_consumer)), :]

c4b_available_interests_ratio = \
    np.zeros((number_of_groups, duration))
c4b_recommended_interests = \
    np.zeros((number_of_groups, \
              number_of_group_consumers, \
                  number_of_services))
c4b_recommended_interests_ratio = \
    np.zeros((number_of_groups, duration))

c4b_recommended_popularities = \
    np.zeros((number_of_groups, number_of_services))
c4b_recommended_most_popular_services = \
    np.zeros((number_of_groups, number_of_services))
c4b_distributed_services = \
    np.zeros((number_of_groups, network_capacity))

c4b_true_popularities = \
    np.zeros((number_of_groups, number_of_services))
c4b_true_most_popular_services = \
    np.zeros((number_of_groups, number_of_services))
c4b_should_be_distributed_services = \
    np.zeros((number_of_groups, network_capacity))

for g in range(number_of_groups):
    
    c4b_true_popularities[g, :] = \
        np.sum(c4b_true_interests[g, :, :], axis = 0)
    
    c4b_true_most_popular_services[g, :] = \
        (- c4b_true_popularities[g, :]).argsort()
    
    c4b_should_be_distributed_services[g, :] = \
        c4b_true_most_popular_services[g, list(range(network_capacity))]

c4b_truely_popular_distributed_services_ratio = \
    np.zeros((number_of_groups, duration))
    
for g in range(number_of_groups):
    
    for t in range(duration):
        
        c4b_available_interests_ratio[g, t] = \
            np.count_nonzero(~ np.isnan(c4b_available_interests[g, :, :])) / \
                (number_of_group_consumers * number_of_services)
        
        c4b_recommended_interests = \
            generateGBRecommendations( \
                                      number_of_group_consumers, \
                                          g, number_of_services, \
                                              c4b_available_interests, \
                                                  c4a_recommended_interests)       
                
        c4b_recommended_interests_ratio[g, t] = \
            np.shape(np.where(c4b_recommended_interests[g, :, :] == \
                              c4b_true_interests[g, :, :]))[1] / \
                (number_of_group_consumers * number_of_services)
        
        for i in range(number_of_services):
            
            c4b_recommended_popularities[g, i] = \
                np.nansum(c4b_recommended_interests[g, :, i])
        
        c4b_recommended_most_popular_services[g, :] = \
            (- c4b_recommended_popularities[g, :]).argsort()
        
        epsilon = unknown_interests_ratio
        
        c4b_distributed_services[g, list(range(np.floor(network_capacity * (1 - epsilon)).astype(int)))] = \
            c4b_recommended_most_popular_services[g, list(range(np.floor(network_capacity * (1 - epsilon)).astype(int)))]
        
        c4b_distributed_services \
            [g, list(range(np.floor(network_capacity * (1 - epsilon)).astype(int) + 1, network_capacity))] = \
                c4b_recommended_most_popular_services \
                    [g, np.random.randint(np.floor(network_capacity * (1 - epsilon)).astype(int) + 1, number_of_services, \
                                          size = (1, network_capacity - np.floor(network_capacity * (1 - epsilon)).astype(int)))[0]]
        
        c4b_truely_popular_distributed_services_ratio[g, t] = \
            len(set(c4b_distributed_services[g, :]).intersection( \
                                                                 c4b_should_be_distributed_services[g, :])) \
                / np.shape(c4b_distributed_services[g, :])[0]
        
        for i in range(number_of_group_consumers):
            
            c4b_available_interests[g, i, c4b_distributed_services[g, :].astype(int)] = \
                c4b_true_interests[g, i, c4b_distributed_services[g, :].astype(int)]    
        
        sys.stdout.write('\r' + \
                         str("Please wait ... {:.2f}%".\
                             format((g * duration + t) / \
                                    (number_of_groups * duration) \
                                    * 100)))
        sys.stdout.flush()        
    
c4b_total_recommended_interests_ratio = \
    np.sum(c4b_recommended_interests_ratio * \
           (number_of_group_consumers * number_of_services), axis = 0) \
        / (number_of_consumers * number_of_services)

c4b_total_truely_popular_distributed_services_ratio = \
    np.sum(c4b_truely_popular_distributed_services_ratio * \
           network_capacity, axis = 0) / (number_of_groups * network_capacity)

#%%

#   Category 4.c with the decaying epsilon-greedy collaborative 
#   group-based recommender system:

number_of_group_consumers = \
    number_of_consumers // number_of_groups

c4c_available_interests = \
    np.zeros((number_of_groups, \
              number_of_group_consumers, \
                  number_of_services))
c4c_true_interests = \
    np.zeros((number_of_groups, \
              number_of_group_consumers, \
                  number_of_services))

for g in range(number_of_groups):
    
    first_group_consumer = number_of_group_consumers * g
    last_group_consumer = number_of_group_consumers * (g + 1)
    
    c4c_available_interests[g, :, :] = \
        available_interests[list(range(first_group_consumer, \
                                       last_group_consumer)), :]
    
    c4c_true_interests[g, :, :] = \
        true_interests[list(range(first_group_consumer, \
                                  last_group_consumer)), :]

c4c_available_interests_ratio = \
    np.zeros((number_of_groups, duration))
c4c_recommended_interests = \
    np.zeros((number_of_groups, \
              number_of_group_consumers, \
                  number_of_services))
c4c_recommended_interests_ratio = \
    np.zeros((number_of_groups, duration))

c4c_recommended_popularities = \
    np.zeros((number_of_groups, number_of_services))
c4c_recommended_most_popular_services = \
    np.zeros((number_of_groups, number_of_services))
c4c_distributed_services = \
    np.zeros((number_of_groups, network_capacity))

c4c_true_popularities = \
    np.zeros((number_of_groups, number_of_services))
c4c_true_most_popular_services = \
    np.zeros((number_of_groups, number_of_services))
c4c_should_be_distributed_services = \
    np.zeros((number_of_groups, network_capacity))

for g in range(number_of_groups):
    
    c4c_true_popularities[g, :] = \
        np.sum(c4c_true_interests[g, :, :], axis = 0)
    
    c4c_true_most_popular_services[g, :] = \
        (- c4c_true_popularities[g, :]).argsort()
    
    c4c_should_be_distributed_services[g, :] = \
        c4c_true_most_popular_services[g, list(range(network_capacity))]

c4c_truely_popular_distributed_services_ratio = \
    np.zeros((number_of_groups, duration))
    
for g in range(number_of_groups):
    
    for t in range(duration):
        
        c4c_available_interests_ratio[g, t] = \
            np.count_nonzero(~ np.isnan(c4c_available_interests[g, :, :])) / \
                (number_of_group_consumers * number_of_services)
        
        c4c_recommended_interests = \
            generateGBRecommendations( \
                                      number_of_group_consumers, g, \
                                          number_of_services, \
                                              c4c_available_interests, \
                                                  c4a_recommended_interests)
        
        c4c_recommended_interests_ratio[g, t] = \
            np.shape(np.where(c4c_recommended_interests[g, :, :] == \
                              c4c_true_interests[g, :, :]))[1] / \
                (number_of_group_consumers * number_of_services)
        
        for i in range(number_of_services):
            
            c4c_recommended_popularities[g, i] = \
                np.nansum(c4c_recommended_interests[g, :, i])
        
        c4c_recommended_most_popular_services[g, :] = \
            (- c4c_recommended_popularities[g, :]).argsort()
        
        epsilon = 1 - c4c_available_interests_ratio[g, t]
        
        c4c_distributed_services[g, list(range(np.floor(network_capacity * (1 - epsilon)).astype(int)))] = \
            c4c_recommended_most_popular_services[g, list(range(np.floor(network_capacity * (1 - epsilon)).astype(int)))]
        
        c4c_distributed_services \
            [g, list(range(np.floor(network_capacity * (1 - epsilon)).astype(int) + 1, network_capacity))] = \
                c4c_recommended_most_popular_services \
                    [g, np.random.randint(np.floor(network_capacity * (1 - epsilon)).astype(int) + 1, number_of_services, \
                                          size = (1, network_capacity - np.floor(network_capacity * (1 - epsilon)).astype(int)))[0]]
        
        c4c_truely_popular_distributed_services_ratio[g, t] = \
            len(set(c4c_distributed_services[g, :]).intersection( \
                                                                 c4c_should_be_distributed_services[g, :])) \
                / np.shape(c4c_distributed_services[g, :])[0]
        
        for i in range(number_of_group_consumers):
            
            c4c_available_interests[g, i, c4c_distributed_services[g, :].astype(int)] = \
                c4c_true_interests[g, i, c4c_distributed_services[g, :].astype(int)]

        sys.stdout.write('\r' + \
                         str("Please wait ... {:.2f}%".\
                             format((g * duration + t) / \
                                    (number_of_groups * duration) \
                                    * 100)))
        sys.stdout.flush()
            
c4c_total_recommended_interests_ratio = \
    np.sum(c4c_recommended_interests_ratio * \
           (number_of_group_consumers * number_of_services), axis = 0) \
        / (number_of_consumers * number_of_services)

c4c_total_truely_popular_distributed_services_ratio = \
    np.sum(c4c_truely_popular_distributed_services_ratio * \
           network_capacity, axis = 0) / (number_of_groups * network_capacity)

#%%

#   Category 4.d with the Upper-Popularity-Bound collaborative
#   group-based recommender system:

number_of_group_consumers = \
    number_of_consumers // number_of_groups

c4d_available_interests = \
    np.zeros((number_of_groups, \
              number_of_group_consumers, \
                  number_of_services))
c4d_true_interests = \
    np.zeros((number_of_groups, \
              number_of_group_consumers, \
                  number_of_services))

for g in range(number_of_groups):
    
    first_group_consumer = number_of_group_consumers * g
    last_group_consumer = number_of_group_consumers * (g + 1)
    
    c4d_available_interests[g, :, :] = \
        available_interests[list(range(first_group_consumer, \
                                       last_group_consumer)), :]
    
    c4d_true_interests[g, :, :] = \
        true_interests[list(range(first_group_consumer, \
                                  last_group_consumer)), :]

c4d_available_interests_ratio = \
    np.zeros((number_of_groups, duration))
c4d_recommended_interests = \
    np.zeros((number_of_groups, \
              number_of_group_consumers, \
                  number_of_services))
c4d_recommended_interests_ratio = \
    np.zeros((number_of_groups, duration))

c4d_recommended_popularities = \
    np.zeros((number_of_groups, number_of_services))
c4d_upper_recommended_popularity_bounds = \
    np.zeros((number_of_groups, number_of_services))
c4d_recommended_most_popular_services = \
    np.zeros((number_of_groups, number_of_services))
c4d_distributed_services = \
    np.zeros((number_of_groups, network_capacity))

c4d_true_popularities = \
    np.zeros((number_of_groups, number_of_services))
c4d_true_most_popular_services = \
    np.zeros((number_of_groups, number_of_services))
c4d_should_be_distributed_services = \
    np.zeros((number_of_groups, network_capacity))

for g in range(number_of_groups):
    
    c4d_true_popularities[g, :] = \
        np.sum(c4d_true_interests[g, :, :], axis = 0)
    
    c4d_true_most_popular_services[g, :] = \
        (- c4d_true_popularities[g, :]).argsort()
    
    c4d_should_be_distributed_services[g, :] = \
        c4d_true_most_popular_services[g, list(range(network_capacity))]

c4d_truely_popular_distributed_services_ratio = \
    np.zeros((number_of_groups, duration))
    
for g in range(number_of_groups):
    
    for t in range(duration):
        
        c4d_available_interests_ratio[g, t] = \
            np.count_nonzero(~ np.isnan(c4d_available_interests[g, :, :])) / \
                (number_of_group_consumers * number_of_services)
        
        c4d_recommended_interests = \
            generateGBRecommendations( \
                                      number_of_group_consumers, g, \
                                          number_of_services, \
                                              c4d_available_interests, \
                                                  c4a_recommended_interests)
        
        c4d_recommended_interests_ratio[g, t] = \
            np.shape(np.where(c4d_recommended_interests[g, :, :] == \
                              c4d_true_interests[g, :, :]))[1] / \
                (number_of_group_consumers * number_of_services)
        
        for i in range(number_of_services):
            
            c4d_recommended_popularities[g, i] = \
                np.nansum(c4d_recommended_interests[g, :, i])

            c4d_upper_recommended_popularity_bounds[g, i] = \
                c4d_recommended_popularities[g, i] + \
                    np.count_nonzero(np.isnan(c4d_recommended_interests[g, :, i]))
        
        c4d_recommended_most_popular_services[g, :] = \
            (- c4d_upper_recommended_popularity_bounds[g, :]).argsort()
        
        c4d_distributed_services[g, :] = \
            c4d_recommended_most_popular_services[g, \
                                                  list(range(network_capacity))]
        
        c4d_truely_popular_distributed_services_ratio[g, t] = \
            len(set(c4d_distributed_services[g, :]).intersection( \
                                                                 c4d_should_be_distributed_services[g, :])) \
                / np.shape(c4d_distributed_services[g, :])[0]
        
        for i in range(number_of_group_consumers):
            
            c4d_available_interests[g, i, c4d_distributed_services[g, :].astype(int)] = \
                c4d_true_interests[g, i, c4d_distributed_services[g, :].astype(int)]
            
        sys.stdout.write('\r' + \
                         str("Please wait ... {:.2f}%".\
                             format((g * duration + t) / \
                                    (number_of_groups * duration) \
                                    * 100)))
        sys.stdout.flush()
            
c4d_total_recommended_interests_ratio = \
    np.sum(c4d_recommended_interests_ratio * \
           (number_of_group_consumers * number_of_services), axis = 0) \
        / (number_of_consumers * number_of_services)

c4d_total_truely_popular_distributed_services_ratio = \
    np.sum(c4d_truely_popular_distributed_services_ratio * \
           network_capacity, axis = 0) / (number_of_groups * network_capacity)

#%%

#   Category 4 summary results:
    
figure, ax = plt.subplots(nrows = 1, ncols = 1)
ax.plot(list(range(duration)), c4a_total_recommended_interests_ratio, \
        '-+b', label = 'Cat 4 - Greedy')
ax.plot(list(range(duration)), c4b_total_recommended_interests_ratio, \
        '-*g', label = 'Cat 4 - e-greedy')
ax.plot(list(range(duration)), c4c_total_recommended_interests_ratio, \
        '-xr', label = 'Cat 4 - Decaying e-greedy')
ax.plot(list(range(duration)), c4d_total_recommended_interests_ratio, \
        '-ok', label = 'Cat 4 - UPB')
ax.legend(loc = 'best')
ax.set_title('Interests ratio vs. time')
ax.set_xlim([1, duration])
ax.set_ylim([0, 1.1])
ax.set_xlabel('Time interval')
ax.set_ylabel('Interests ratio')
ax.grid(color = 'k', linestyle = '--', linewidth = 1)

figure.tight_layout()
figure.savefig('c4-interests ratio-setup ' + str(setup) + '.png', \
               dpi = 500)

figure, ax = plt.subplots(nrows = 1, ncols = 1)
ax.plot(list(range(duration)), c4a_total_truely_popular_distributed_services_ratio, \
        '-+b', label = 'Cat 4 - Greedy')
ax.plot(list(range(duration)), c4b_total_truely_popular_distributed_services_ratio, \
        '-*g', label = 'Cat 4 - e-greedy')
ax.plot(list(range(duration)), c4c_total_truely_popular_distributed_services_ratio, \
        '-xr', label = 'Cat 4 - Decaying e-greedy')
ax.plot(list(range(duration)), c4d_total_truely_popular_distributed_services_ratio, \
        '-ok', label = 'Cat 4 - UPB')
ax.legend(loc = 'best')
ax.set_title('Popular distributed services ratio vs. time')
ax.set_xlim([1, duration])
ax.set_ylim([0, 1.1])
ax.set_xlabel('Time interval')
ax.set_ylabel('Popular distributed services ratio')
ax.grid(color = 'k', linestyle = '--', linewidth = 1)

figure.tight_layout()
figure.savefig('c4-popular distributed services ratio-setup ' + str(setup) + '.png', \
               dpi = 500)

#%%

#   Saving all results:

import shelve
 
results = \
    shelve.open('setup' + str(setup) + 'results.out','n')

for key in dir():
    try:
        results[key] = globals()[key]
    except TypeError:
        print('ERROR shelving: {0}'.format(key))
results.close()

#%%

#   Written by "Kais Suleiman" (ksuleiman.weebly.com) 
