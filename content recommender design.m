%%
 
%   Written by "Kais Suleiman" (ksuleiman.weebly.com)
%
%   Notes:
%
%   - The contents of this script represent a tool used to generate 
%   different recommender category results given different experiment 
%   setups as explained in details in Chapter 5 of the thesis:
%       Kais Suleiman, "Popular Content Distribution in Public 
%       Transportation Using Artificial Intelligence Techniques.", 
%       Ph.D. thesis, University of Waterloo, Ontario, Canada, 2019.
%   - Any experiment setup encoding can be used to differentiate between
%   the different results generated using this tool. For example, we can
%   use the encoding xyz such that x represents different group interest 
%   distribution standard deviations, y represents different unknown 
%   consumer interest ratios and z represents different network capacities. 
%   We can then specify that each of x, y and z would have a value of 1 
%   to represent a high value and a value of 0 to represent a low value. 
%   Therefore and using such encoding setup, 111 would represent 
%   an experiment setup with a high group interest distribution standard 
%   deviation, a high unknown consumer interests ratio and a high
%   network capacity. Refer to Table 5.1. of the thesis for further
%   clarification.
%   - Simpler but still similar variable names have been used throughout 
%   this script instead of the mathematical notations used in the thesis.
%   - The assumptions used in the script are the same as those used in the thesis.
%   - Figures and animations are created throughout this script to aid 
%   in thesis visualizations and other forms of results sharing.

%%

stream = RandStream.getGlobalStream;
reset(stream);
clear;
clc;

%%

%   Scenario assumptions:

number_of_consumers = 100;
number_of_services = 20;
number_of_groups = 2;
group_interests_distribution_std = number_of_services / 2;
unknown_interests_ratio = 0.9;
xmin = 0;
xmax = 1000;
ymin = 0;
ymax = 500;
group_x_location_std = (xmax - xmin) / number_of_groups / 10;
group_y_location_std = (ymax - ymin) / 10;
duration = 100;
network_capacity = number_of_services / 2;

setup = 111;%   Used to name result files 

%%

%   Consumer interest distributions:

true_interests = zeros(number_of_consumers,number_of_services);

for i = 1:number_of_groups
    
    first_group_consumer = ...
        number_of_consumers / number_of_groups * (i - 1) + 1;
    
    last_group_consumer = ...
        number_of_consumers / number_of_groups * i;
    
    first_group_service = ...
        number_of_services / number_of_groups * (i - 1) + 1;
    
    last_group_service = ...
        number_of_services / number_of_groups * i;
    
    for j =  first_group_consumer:last_group_consumer
        
        true_interests_indices = ...
            floor(normrnd( ...
            round((first_group_service + last_group_service) / 2), ...
            group_interests_distribution_std, ...
            [1,number_of_services / number_of_groups]));
        
        true_interests_indices(true_interests_indices < 1) = [];
        
        true_interests_indices(true_interests_indices > number_of_services) = [];
        
        true_interests(j,true_interests_indices) = 1;
        
    end
    
end

%   Confirming that at least one service is truely liked per consumer:

for i = 1:number_of_consumers   
    
    if all(true_interests(i,:) == 0) == 1    
        
        true_interests(i,randi( ...
            [floor(i / (number_of_consumers / number_of_groups)) * ...
            (number_of_services / number_of_groups) + 1 ...
            (floor(i / (number_of_consumers / number_of_groups)) + 1) * ...
            (number_of_services / number_of_groups)])) = 1; 
        
    end  
    
end

available_interests = true_interests;

for i = 1:number_of_consumers
    
    for j = 1:number_of_services
        
        if rand(1) < unknown_interests_ratio
            
            available_interests(i,j) = NaN;
            
        end
        
    end
    
end

%   Confirming that at least one service is known to be liked per consumer:

for i = 1:number_of_consumers
    
    for j = 1:number_of_services
        
        if (all(available_interests(i,isnan(available_interests(i,:)) == 0) == 0) == 1) && ...
                (isnan(available_interests(i,j)) == 1) && (true_interests(i,j) == 1)
            
            available_interests(i,j) = true_interests(i,j);
            break;
            
        end
        
    end
    
end

%%

%   Interest distributions plotting:

group_popularities = zeros(number_of_groups,number_of_services);

for i = 1:number_of_groups 
    
    for j = 1:number_of_services
    
        group_popularities(i,j) = ...
            sum(true_interests(number_of_consumers / number_of_groups * (i - 1) + 1: ...
            number_of_consumers / number_of_groups * i,j));
    
    end
        
end

figure('Name','Group interest distributions');
bar(group_popularities','stacked')
hold on
title('Group interests','FontSize',18);

max_service_popularity = 0;

for i = 1:number_of_services
    
    max_service_popularity = ...
        max(max_service_popularity,sum(group_popularities(:,i)));
    
end

axis([0,number_of_services + 1,0,max_service_popularity + 1]);
hold on
xlabel('Services','FontSize',18)
hold on
ylabel('Number of consumers interested','FontSize',18)
hold on
grid on

file_name = ...
    sprintf('Group interest distributions with %0d std.fig', ...
    group_interests_distribution_std);
saveas(gcf,file_name);

file_name = ...
    sprintf('Group interest distributions with %0d std.bmp', ...
    group_interests_distribution_std);
saveas(gcf,file_name);

figure('Name','True service interest distributions');
pcolor([true_interests ...
    nan(size(true_interests,1),1); ...
    nan(1,size(true_interests,2) + 1)]);
colormap(winter);
shading flat;
set(gca,'ydir','reverse');
colorbar;
title('True service interests matrix','FontSize',18);
xlabel('Services','FontSize',18);
ylabel('Consumers','FontSize',18);

file_name = ...
    sprintf('True interest distributions with %0d std & %0.1f unknown ratio.fig', ...
    group_interests_distribution_std,unknown_interests_ratio);
saveas(gcf,file_name);

file_name = ...
    sprintf('True interest distributions with %0d std & %0.1f unknown ratio.bmp', ...
    group_interests_distribution_std,unknown_interests_ratio);
saveas(gcf,file_name);

figure('Name','Available service interest distributions');
pcolor([available_interests ...
    nan(size(available_interests,1),1); ...
    nan(1,size(available_interests,2) + 1)]);
colormap(winter);
shading flat;
set(gca,'ydir','reverse');
colorbar;
title('Available service interests matrix','FontSize',18);
xlabel('Services','FontSize',18);
ylabel('Consumers','FontSize',18);

file_name = ...
    sprintf('Available interest distributions with %0d std & %0.1f unknown ratio.fig', ...
    group_interests_distribution_std,unknown_interests_ratio);
saveas(gcf,file_name);

file_name = ...
    sprintf('Available interest distributions with %0d std & %0.1f unknown ratio.bmp', ...
    group_interests_distribution_std,unknown_interests_ratio);
saveas(gcf,file_name);

%%

%   Consumer location distributions:

for i = 1:number_of_groups
    
    first_group_consumer = ...
        number_of_consumers / number_of_groups * (i - 1) + 1;
    
    last_group_consumer = ...
        number_of_consumers / number_of_groups * i;
    
    group_x_location_mean = ...
        ((i - 1) * (xmax - xmin) / number_of_groups) + ...
        ((i * (xmax - xmin) / number_of_groups) - ...
        ((i - 1) * (xmax - xmin) / number_of_groups)) / 2;
    
    group_y_location_mean = (ymax - ymin) / 2;
    
    x_locations(first_group_consumer:last_group_consumer) = ...
        normrnd(group_x_location_mean,group_x_location_std, ...
        [1,number_of_consumers / number_of_groups]);
    
    y_locations(first_group_consumer:last_group_consumer) = ...
        normrnd(group_y_location_mean,group_y_location_std, ...
        [1,number_of_consumers / number_of_groups]);
    
end

%%

%   Location distributions plotting:

figure('Name','Consumer location distributions');
scatter(x_locations,y_locations,99,'y','filled','MarkerEdgeColor','k');
hold on
axis([xmin,xmax,ymin,ymax]);
title('Consumer locations','FontSize',18);
hold on
xlabel('X - axis (m)','FontSize',18);
hold on
ylabel('Y - axis (m)','FontSize',18);
hold on
grid on

saveas(gcf,'Location distributions.fig');

saveas(gcf,'Location distributions.bmp');

%%

%   Category 1 with the non-interactive non-collaborative 
%   non-group-based recommender system:

c1_available_interests = available_interests;

c1_available_interests_ratio = zeros(1,duration);

c1_true_popularities = ...
    zeros(number_of_groups,number_of_services);
c1_true_most_popular_services = ...
    zeros(number_of_groups,number_of_services);
c1_should_be_distributed_services = ...
    zeros(number_of_groups,network_capacity);

number_of_group_consumers = ...
    number_of_consumers / number_of_groups;

for g = 1:number_of_groups
    
    first_group_consumer = number_of_group_consumers * (g - 1) + 1;
    last_group_consumer = number_of_group_consumers * g;
    
    c1_true_popularities(g,:) = ...
        sum(true_interests(first_group_consumer:last_group_consumer,:),1);
    
    [~,c1_true_most_popular_services(g,:)] = ...
        sort(c1_true_popularities(g,:),'descend');
    
    c1_should_be_distributed_services(g,:) = ...
        c1_true_most_popular_services(g,1:network_capacity);
    
end

c1_truely_popular_distributed_services_ratio = ...
    zeros(number_of_groups,duration);
c1_total_truely_popular_distributed_services_ratio = zeros(1,duration);

handle = waitbar(0,'Please wait ... ');

for t = 1:duration
    
    c1_available_interests_ratio(t) = ...
        sum(sum(isnan(c1_available_interests) == 0)) / ...
        (number_of_consumers * number_of_services);

    c1_available_popularities = zeros(1,number_of_services);
    
    for i = 1:number_of_services

        c1_available_popularities(i) = ...
            sum(c1_available_interests(isnan(c1_available_interests(:,i)) == 0,i));
        
    end
    
    [~,c1_available_most_popular_services] = ...
        sort(c1_available_popularities,'descend');
        
    c1_distributed_services = ...
        c1_available_most_popular_services(1:network_capacity);
    
    for g = 1:number_of_groups
        
        c1_truely_popular_distributed_services_ratio(g,t) = ...
            length(intersect(c1_distributed_services, ...
            c1_should_be_distributed_services(g,:))) ...
            / length(c1_distributed_services);
        
    end
    
    c1_total_truely_popular_distributed_services_ratio(t) = ...
        sum(c1_truely_popular_distributed_services_ratio(:,t) .* ...
        (network_capacity),1) ./ (number_of_groups * network_capacity);
    
    waitbar(t / duration,handle)
    
    if t == duration
        
        close(handle)
    
    end
    
end

%%

%   Category 1 summary results:

figure('Name','Category 1 - Interests ratio');
plot(1:duration,c1_available_interests_ratio,'--k','LineWidth',2,'MarkerSize',10);
hold on
legend({'Cat 1'}, ...
    'Location','best','FontSize',18);
hold on
title('Interests ratio vs. time','FontSize',18);
axis([1,duration,0,1.1]);
hold on
xlabel('Time interval','FontSize',18);
hold on
ylabel('Interests ratio','FontSize',18);
hold on
grid on

file_name = ...
    sprintf('c1-interests ratio-setup%3d.fig',setup);
saveas(gcf,file_name);

file_name = ...
    sprintf('c1-interests ratio-setup%3d.bmp',setup);
saveas(gcf,file_name);

figure('Name', ...
    'Category 1 - Popular distributed services ratio');
plot(1:duration,c1_total_truely_popular_distributed_services_ratio,'--k', ...
    'LineWidth',2,'MarkerSize',10);
hold on
legend({'Cat 1'}, ...
    'Location','best','FontSize',18);
hold on
hold on
title('Popular distributed services ratio vs. time','FontSize',18);
axis([1,duration,0,1.1]);
hold on
xlabel('Time interval','FontSize',18);
hold on
ylabel('Popular distributed services ratio','FontSize',18);
hold on
grid on

file_name = ...
    sprintf('c1-popular distributed services ratio-setup%3d.fig', ...
    setup);
saveas(gcf,file_name);

file_name = ...
    sprintf('c1-popular distributed services ratio-setup%3d.bmp', ...
    setup);
saveas(gcf,file_name);

%%

%   Category 2.a with the greedy non-collaborative 
%   non-group-based recommender system:

c2a_available_interests = available_interests;

c2a_available_interests_ratio = zeros(1,duration);

c2a_true_popularities = ...
    zeros(number_of_groups,number_of_services);
c2a_true_most_popular_services = ...
    zeros(number_of_groups,number_of_services);
c2a_should_be_distributed_services = ...
    zeros(number_of_groups,network_capacity);

number_of_group_consumers = ...
    number_of_consumers / number_of_groups;

for g = 1:number_of_groups
    
    first_group_consumer = number_of_group_consumers * (g - 1) + 1;
    last_group_consumer = number_of_group_consumers * g;
    
    c2a_true_popularities(g,:) = ...
        sum(true_interests(first_group_consumer:last_group_consumer,:),1);
    
    [~,c2a_true_most_popular_services(g,:)] = ...
        sort(c2a_true_popularities(g,:),'descend');
    
    c2a_should_be_distributed_services(g,:) = ...
        c2a_true_most_popular_services(g,1:network_capacity);
    
end

c2a_truely_popular_distributed_services_ratio = ...
    zeros(number_of_groups,duration);
c2a_total_truely_popular_distributed_services_ratio = zeros(1,duration);

handle = waitbar(0,'Please wait ... ');

for t = 1:duration
    
    c2a_available_interests_ratio(t) = ...
        sum(sum(isnan(c2a_available_interests) == 0)) / ...
        (number_of_consumers * number_of_services);
    
    c2a_available_popularities = zeros(1,number_of_services);
    
    for i = 1:number_of_services

        c2a_available_popularities(i) = ...
            sum(c2a_available_interests(isnan(c2a_available_interests(:,i)) == 0,i));
        
    end
    
    [~,c2a_available_most_popular_services] = ...
        sort(c2a_available_popularities,'descend');
        
    c2a_distributed_services = ...
        c2a_available_most_popular_services(1:network_capacity);
    
    for g = 1:number_of_groups
        
        c2a_truely_popular_distributed_services_ratio(g,t) = ...
            length(intersect(c2a_distributed_services, ...
            c2a_should_be_distributed_services(g,:))) ...
            / length(c2a_distributed_services);
        
    end
    
    c2a_total_truely_popular_distributed_services_ratio(t) = ...
        sum(c2a_truely_popular_distributed_services_ratio(:,t) .* ...
        (network_capacity),1) ./ (number_of_groups * network_capacity);
    
    for i = 1:number_of_consumers
        
        c2a_available_interests(i,c2a_distributed_services) = ...
            true_interests(i,c2a_distributed_services);

    end 
    
    waitbar(t / duration,handle)
    
    if t == duration
        
        close(handle)
    
    end
    
end

%%

%   Category 2.b with the epsilon-greedy non-collaborative 
%   non-group-based recommender system:

c2b_available_interests = available_interests;

c2b_available_interests_ratio = zeros(1,duration);

c2b_true_popularities = ...
    zeros(number_of_groups,number_of_services);
c2b_true_most_popular_services = ...
    zeros(number_of_groups,number_of_services);
c2b_should_be_distributed_services = ...
    zeros(number_of_groups,network_capacity);

number_of_group_consumers = ...
    number_of_consumers / number_of_groups;

for g = 1:number_of_groups
    
    first_group_consumer = number_of_group_consumers * (g - 1) + 1;
    last_group_consumer = number_of_group_consumers * g;
    
    c2b_true_popularities(g,:) = ...
        sum(true_interests(first_group_consumer:last_group_consumer,:),1);
    
    [~,c2b_true_most_popular_services(g,:)] = ...
        sort(c2b_true_popularities(g,:),'descend');
    
    c2b_should_be_distributed_services(g,:) = ...
        c2b_true_most_popular_services(g,1:network_capacity);
    
end

c2b_truely_popular_distributed_services_ratio = ...
    zeros(number_of_groups,duration);
c2b_total_truely_popular_distributed_services_ratio = zeros(1,duration);

handle = waitbar(0,'Please wait ... ');

for t = 1:duration
    
    c2b_available_interests_ratio(t) = ...
        sum(sum(isnan(c2b_available_interests) == 0)) / ...
        (number_of_consumers * number_of_services);

    c2b_available_popularities = zeros(1,number_of_services);
    
    for i = 1:number_of_services
        
        c2b_available_popularities(i) = ...
            sum(c2b_available_interests(isnan(c2b_available_interests(:,i)) == 0,i));
    end
    
    [~,c2b_available_most_popular_services] = ...
        sort(c2b_available_popularities,'descend');
    
    epsilon = unknown_interests_ratio;
    
    c2b_distributed_services = ...
        c2b_available_most_popular_services(1:floor(network_capacity * (1 - epsilon)));
    
    c2b_distributed_services = horzcat(c2b_distributed_services, ...
        c2b_available_most_popular_services ...
        (randi([floor(network_capacity * (1 - epsilon)) + 1,number_of_services], ...
        1,network_capacity - floor(network_capacity * (1 - epsilon))))); %#ok<AGROW>

    for g = 1:number_of_groups
        
        c2b_truely_popular_distributed_services_ratio(g,t) = ...
            length(intersect(c2b_distributed_services, ...
            c2b_should_be_distributed_services(g,:))) ...
            / length(c2b_distributed_services);
        
    end
    
    c2b_total_truely_popular_distributed_services_ratio(t) = ...
        sum(c2b_truely_popular_distributed_services_ratio(:,t) .* ...
        (network_capacity),1) ./ (number_of_groups * network_capacity);
    
    for i = 1:number_of_consumers
        
        c2b_available_interests(i,c2b_distributed_services) = ...
            true_interests(i,c2b_distributed_services);
            
    end 
    
    waitbar(t / duration,handle)
    
    if t == duration
        
        close(handle)
        
    end
    
end

%%

%   Category 2.c with the decaying epsilon-greedy non-collaborative 
%   non-group-based recommender system:

c2c_available_interests = available_interests;

c2c_available_interests_ratio = zeros(1,duration);

c2c_true_popularities = ...
    zeros(number_of_groups,number_of_services);
c2c_true_most_popular_services = ...
    zeros(number_of_groups,number_of_services);
c2c_should_be_distributed_services = ...
    zeros(number_of_groups,network_capacity);

number_of_group_consumers = ...
    number_of_consumers / number_of_groups;

for g = 1:number_of_groups
    
    first_group_consumer = number_of_group_consumers * (g - 1) + 1;
    last_group_consumer = number_of_group_consumers * g;
    
    c2c_true_popularities(g,:) = ...
        sum(true_interests(first_group_consumer:last_group_consumer,:),1);
    
    [~,c2c_true_most_popular_services(g,:)] = ...
        sort(c2c_true_popularities(g,:),'descend');
    
    c2c_should_be_distributed_services(g,:) = ...
        c2c_true_most_popular_services(g,1:network_capacity);
    
end

c2c_truely_popular_distributed_services_ratio = ...
    zeros(number_of_groups,duration);
c2c_total_truely_popular_distributed_services_ratio = zeros(1,duration);

handle = waitbar(0,'Please wait ... ');

for t = 1:duration
    
    c2c_available_interests_ratio(t) = ...
        sum(sum(isnan(c2c_available_interests) == 0)) / ...
        (number_of_consumers * number_of_services);
    
    c2c_available_popularities = zeros(1,number_of_services);
    
    for i = 1:number_of_services
        
        c2c_available_popularities(i) = ...
            sum(c2c_available_interests(isnan(c2c_available_interests(:,i)) == 0,i));
        
    end
    
    [~,c2c_available_most_popular_services] = ...
        sort(c2c_available_popularities,'descend');
    
    epsilon = 1 - c2c_available_interests_ratio(t);
    
    c2c_distributed_services = ...
        c2c_available_most_popular_services(1:floor(network_capacity * (1 - epsilon)));
    
    c2c_distributed_services = horzcat(c2c_distributed_services, ...
        c2c_available_most_popular_services ...
        (randi([floor(network_capacity * (1 - epsilon)) + 1,number_of_services], ...
        1,network_capacity - floor(network_capacity * (1 - epsilon))))); %#ok<AGROW>

    for g = 1:number_of_groups
        
        c2c_truely_popular_distributed_services_ratio(g,t) = ...
            length(intersect(c2c_distributed_services, ...
            c2c_should_be_distributed_services(g,:))) ...
            / length(c2c_distributed_services);
        
    end
    
    c2c_total_truely_popular_distributed_services_ratio(t) = ...
        sum(c2c_truely_popular_distributed_services_ratio(:,t) .* ...
        (network_capacity),1) ./ (number_of_groups * network_capacity);
    
    for i = 1:number_of_consumers
        
        c2c_available_interests(i,c2c_distributed_services) = ...
            true_interests(i,c2c_distributed_services);
        
    end 
    
    waitbar(t / duration,handle)
    
    if t == duration
        
        close(handle)
        
    end
    
end

%%

%   Category 2.d with the Upper-Popularity-Bound non-collaborative
%   non-group-based recommender system:

c2d_available_interests = available_interests;

c2d_available_interests_ratio = zeros(1,duration);

c2d_true_popularities = ...
    zeros(number_of_groups,number_of_services);
c2d_true_most_popular_services = ...
    zeros(number_of_groups,number_of_services);
c2d_should_be_distributed_services = ...
    zeros(number_of_groups,network_capacity);

number_of_group_consumers = ...
    number_of_consumers / number_of_groups;

for g = 1:number_of_groups
    
    first_group_consumer = number_of_group_consumers * (g - 1) + 1;
    last_group_consumer = number_of_group_consumers * g;
    
    c2d_true_popularities(g,:) = ...
        sum(true_interests(first_group_consumer:last_group_consumer,:),1);
    
    [~,c2d_true_most_popular_services(g,:)] = ...
        sort(c2d_true_popularities(g,:),'descend');
    
    c2d_should_be_distributed_services(g,:) = ...
        c2d_true_most_popular_services(g,1:network_capacity);
    
end

c2d_truely_popular_distributed_services_ratio = ...
    zeros(number_of_groups,duration);
c2d_total_truely_popular_distributed_services_ratio = zeros(1,duration);

handle = waitbar(0,'Please wait ... ');

for t = 1:duration
    
    c2d_available_interests_ratio(t) = ...
        sum(sum(isnan(c2d_available_interests) == 0)) / ...
        (number_of_consumers * number_of_services);
        
    c2d_available_popularities = zeros(1,number_of_services);
    c2d_upper_available_popularity_bounds = zeros(1,number_of_services);
    
    for i = 1:number_of_services
        
        c2d_available_popularities(i) = ...
            sum(c2d_available_interests(isnan(c2d_available_interests(:,i)) == 0,i));
        
        c2d_upper_available_popularity_bounds(i) = ...
            c2d_available_popularities(i) + ...
            sum(isnan(c2d_available_interests(:,i)));
        
    end
    
    [~,c2d_available_most_popular_services] = ...
        sort(c2d_upper_available_popularity_bounds,'descend');
    
    c2d_distributed_services = ...
        c2d_available_most_popular_services(1:network_capacity);
    
    for g = 1:number_of_groups
        
        c2d_truely_popular_distributed_services_ratio(g,t) = ...
            length(intersect(c2d_distributed_services, ...
            c2d_should_be_distributed_services(g,:))) ...
            / length(c2d_distributed_services);
        
    end
    
    c2d_total_truely_popular_distributed_services_ratio(t) = ...
        sum(c2d_truely_popular_distributed_services_ratio(:,t) .* ...
        (network_capacity),1) ./ (number_of_groups * network_capacity);
    
    for i = 1:number_of_consumers
        
        c2d_available_interests(i,c2d_distributed_services) = ...
            true_interests(i,c2d_distributed_services);
            
    end
    
    waitbar(t / duration,handle)
    
    if t == duration
        
        close(handle)
        
    end
    
end

%%

%   Category 2 summary results:

figure('Name','Category 2 - Interests ratio');
plot(1:duration,c2a_available_interests_ratio,'-+b','LineWidth',2, ...
    'MarkerSize',10);
hold on
plot(1:duration,c2b_available_interests_ratio,'-*g','LineWidth',2, ...
    'MarkerSize',10);
hold on
plot(1:duration,c2c_available_interests_ratio,'-xr','LineWidth',2, ...
    'MarkerSize',10);
hold on
plot(1:duration,c2d_available_interests_ratio,'-ok','LineWidth',2, ...
    'MarkerSize',10);
hold on
legend({'Cat 2 - Greedy','Cat 2 - e-greedy', ...
    'Cat 2 - Decaying e-greedy','Cat 2 - UPB'}, ...
    'Location','best','FontSize',18);
hold on
title('Interests ratio vs. time','FontSize',18);
axis([1,duration,0,1.1]);
hold on
xlabel('Time interval','FontSize',18);
hold on
ylabel('Interests ratio','FontSize',18);
hold on
grid on

file_name = ...
    sprintf('c2-interests ratio-setup%3d.fig', ...
    setup);
saveas(gcf,file_name);

file_name = ...
    sprintf('c2-interests ratio-setup%3d.bmp', ...
    setup);
saveas(gcf,file_name);

figure('Name', ...
    'Category 2 - Popular distributed services ratio');
plot(1:duration,c2a_total_truely_popular_distributed_services_ratio,'-+b', ...
    'LineWidth',2,'MarkerSize',10);
hold on
plot(1:duration,c2b_total_truely_popular_distributed_services_ratio,'-*g', ...
    'LineWidth',2,'MarkerSize',10);
hold on
plot(1:duration,c2c_total_truely_popular_distributed_services_ratio,'-xr', ...
    'LineWidth',2,'MarkerSize',10);
hold on
plot(1:duration,c2d_total_truely_popular_distributed_services_ratio,'-ok', ...
    'LineWidth',2,'MarkerSize',10);
hold on
legend({'Cat 2 - Greedy','Cat 2 - e-greedy', ...
    'Cat 2 - Decaying e-greedy','Cat 2 - UPB'}, ...
    'Location','best','FontSize',18);
hold on
title('Popular distributed services ratio vs. time','FontSize',18);
axis([1,duration,0,1.1]);
hold on
xlabel('Time interval','FontSize',18);
hold on
ylabel('Popular distributed services ratio','FontSize',18);
hold on
grid on

file_name = ...
    sprintf('c2-popular distributed services ratio-setup%3d.fig', ...
    setup);
saveas(gcf,file_name);

file_name = ...
    sprintf('c2-popular distributed services ratio-setup%3d.bmp', ...
    setup);
saveas(gcf,file_name);

%%

%   The generateNGBRecommendations function:

function recommended_interests = generateNGBRecommendations( ...
    number_of_consumers, number_of_services, available_interests)

    jaccard_similarities = zeros(number_of_consumers,number_of_consumers);
    
    for i = 1:number_of_consumers
        
        for j = 1:number_of_consumers
            
            if i == j
                
                continue;
                
            else
                
                jaccard_similarities(i,j) = ...
                    sum(available_interests(i,:) == available_interests(j,:))...
                    / number_of_services;
                
            end
            
        end
        
    end
    
    recommended_interests = available_interests;
    
    for i = 1:number_of_consumers
        
        for j = 1:number_of_services
            
            if isnan(recommended_interests(i,j)) == 1
                
                most_similar_consumers = ...
                    find(jaccard_similarities(i,:) == max(jaccard_similarities(i,:)));
                
                recommended_interests(i,j) = ...
                    recommended_interests(most_similar_consumers(1),j);
                
            end
            
        end
        
    end
    
end

%%

%   Category 3.a with the greedy collaborative
%   non-group-based recommender system:

c3a_available_interests = available_interests;

c3a_available_interests_ratio = zeros(1,duration);
c3a_recommended_interests_ratio = zeros(1,duration);

c3a_true_popularities = ...
    zeros(number_of_groups,number_of_services);
c3a_true_most_popular_services = ...
    zeros(number_of_groups,number_of_services);
c3a_should_be_distributed_services = ...
    zeros(number_of_groups,network_capacity);

number_of_group_consumers = ...
    number_of_consumers / number_of_groups;

for g = 1:number_of_groups
    
    first_group_consumer = number_of_group_consumers * (g - 1) + 1;
    last_group_consumer = number_of_group_consumers * g;
    
    c3a_true_popularities(g,:) = ...
        sum(true_interests(first_group_consumer:last_group_consumer,:),1);
    
    [~,c3a_true_most_popular_services(g,:)] = ...
        sort(c3a_true_popularities(g,:),'descend');
    
    c3a_should_be_distributed_services(g,:) = ...
        c3a_true_most_popular_services(g,1:network_capacity);
    
end

c3a_truely_popular_distributed_services_ratio = ...
    zeros(number_of_groups,duration);
c3a_total_truely_popular_distributed_services_ratio = zeros(1,duration);

handle = waitbar(0,'Please wait ... ');

for t = 1:duration
    
    c3a_available_interests_ratio(t) = ...
        sum(sum(isnan(c3a_available_interests) == 0)) / ...
        (number_of_consumers * number_of_services);
    
    c3a_recommended_interests = generateNGBRecommendations( ...
        number_of_consumers, number_of_services, c3a_available_interests);
    
    c3a_recommended_interests_ratio(t) = ...
        sum(sum(c3a_recommended_interests == true_interests)) / ...
        (number_of_consumers * number_of_services);

    c3a_recommended_popularities = zeros(1,number_of_services);
    
    for i = 1:number_of_services
        
        c3a_recommended_popularities(i) = ...
            sum(c3a_recommended_interests(isnan(c3a_recommended_interests(:,i)) == 0,i));
        
    end
    
    [~,c3a_recommended_most_popular_services] = ...
        sort(c3a_recommended_popularities,'descend');
    
    c3a_distributed_services = ...
        c3a_recommended_most_popular_services(1:network_capacity);
    
    for g = 1:number_of_groups
        
        c3a_truely_popular_distributed_services_ratio(g,t) = ...
            length(intersect(c3a_distributed_services, ...
            c3a_should_be_distributed_services(g,:))) ...
            / length(c3a_distributed_services);
        
    end
    
    c3a_total_truely_popular_distributed_services_ratio(t) = ...
        sum(c3a_truely_popular_distributed_services_ratio(:,t) .* ...
        (network_capacity),1) ./ (number_of_groups * network_capacity);
    
    for i = 1:number_of_consumers
        
        c3a_available_interests(i,c3a_distributed_services) = ...
            true_interests(i,c3a_distributed_services);

    end 
    
    waitbar(t / duration,handle)
    
    if t == duration
        
        close(handle)
    
    end
    
end

%%

%   Category 3.b with the epsilon-greedy collaborative
%   non-group-based recommender system:

c3b_available_interests = available_interests;

c3b_available_interests_ratio = zeros(1,duration);
c3b_recommended_interests_ratio = zeros(1,duration);

c3b_true_popularities = ...
    zeros(number_of_groups,number_of_services);
c3b_true_most_popular_services = ...
    zeros(number_of_groups,number_of_services);
c3b_should_be_distributed_services = ...
    zeros(number_of_groups,network_capacity);

number_of_group_consumers = ...
    number_of_consumers / number_of_groups;

for g = 1:number_of_groups
    
    first_group_consumer = number_of_group_consumers * (g - 1) + 1;
    last_group_consumer = number_of_group_consumers * g;
    
    c3b_true_popularities(g,:) = ...
        sum(true_interests(first_group_consumer:last_group_consumer,:),1);
    
    [~,c3b_true_most_popular_services(g,:)] = ...
        sort(c3b_true_popularities(g,:),'descend');
    
    c3b_should_be_distributed_services(g,:) = ...
        c3b_true_most_popular_services(g,1:network_capacity);
    
end

c3b_truely_popular_distributed_services_ratio = ...
    zeros(number_of_groups,duration);
c3b_total_truely_popular_distributed_services_ratio = zeros(1,duration);

handle = waitbar(0,'Please wait ... ');

for t = 1:duration
    
    c3b_available_interests_ratio(t) = ...
        sum(sum(isnan(c3b_available_interests) == 0)) / ...
        (number_of_consumers * number_of_services);
        
    c3b_recommended_interests = generateNGBRecommendations( ...
        number_of_consumers, number_of_services, c3b_available_interests);

    c3b_recommended_interests_ratio(t) = ...
        sum(sum(c3b_recommended_interests == true_interests)) / ...
        (number_of_consumers * number_of_services);

    c3b_recommended_popularities = zeros(1,number_of_services);
    
    for i = 1:number_of_services
        
        c3b_recommended_popularities(i) = ...
            sum(c3b_recommended_interests(isnan(c3b_recommended_interests(:,i)) == 0,i));
        
    end
    
    [~,c3b_recommended_most_popular_services] = ...
        sort(c3b_recommended_popularities,'descend');
    
    epsilon = unknown_interests_ratio;
    
    c3b_distributed_services = ...
        c3b_recommended_most_popular_services(1:floor(network_capacity * (1 - epsilon)));
    
    c3b_distributed_services = horzcat(c3b_distributed_services, ...
        c3b_recommended_most_popular_services ...
        (randi([floor(network_capacity * (1 - epsilon)) + 1,number_of_services], ...
        1,network_capacity - floor(network_capacity * (1 - epsilon))))); %#ok<AGROW>

    for g = 1:number_of_groups
        
        c3b_truely_popular_distributed_services_ratio(g,t) = ...
            length(intersect(c3b_distributed_services, ...
            c3b_should_be_distributed_services(g,:))) ...
            / length(c3b_distributed_services);
        
    end
    
    c3b_total_truely_popular_distributed_services_ratio(t) = ...
        sum(c3b_truely_popular_distributed_services_ratio(:,t) .* ...
        (network_capacity),1) ./ (number_of_groups * network_capacity);
    
    for i = 1:number_of_consumers
        
        c3b_available_interests(i,c3b_distributed_services) = ...
            true_interests(i,c3b_distributed_services);
            
    end 
    
    waitbar(t / duration,handle)
    
    if t == duration
        
        close(handle)
        
    end
    
end

%%

%   Category 3.c with the decaying epsilon-greedy collaborative
%   non-group-based recommender system:

c3c_available_interests = available_interests;

c3c_available_interests_ratio = zeros(1,duration);
c3c_recommended_interests_ratio = zeros(1,duration);

c3c_true_popularities = ...
    zeros(number_of_groups,number_of_services);
c3c_true_most_popular_services = ...
    zeros(number_of_groups,number_of_services);
c3c_should_be_distributed_services = ...
    zeros(number_of_groups,network_capacity);

number_of_group_consumers = ...
    number_of_consumers / number_of_groups;

for g = 1:number_of_groups
    
    first_group_consumer = number_of_group_consumers * (g - 1) + 1;
    last_group_consumer = number_of_group_consumers * g;
    
    c3c_true_popularities(g,:) = ...
        sum(true_interests(first_group_consumer:last_group_consumer,:),1);
    
    [~,c3c_true_most_popular_services(g,:)] = ...
        sort(c3c_true_popularities(g,:),'descend');
    
    c3c_should_be_distributed_services(g,:) = ...
        c3c_true_most_popular_services(g,1:network_capacity);
    
end

c3c_truely_popular_distributed_services_ratio = ...
    zeros(number_of_groups,duration);
c3c_total_truely_popular_distributed_services_ratio = zeros(1,duration);

handle = waitbar(0,'Please wait ... ');

for t = 1:duration
    
    c3c_available_interests_ratio(t) = ...
        sum(sum(isnan(c3c_available_interests) == 0)) / ...
        (number_of_consumers * number_of_services);
    
    c3c_recommended_interests = generateNGBRecommendations( ...
        number_of_consumers, number_of_services, c3c_available_interests);

    c3c_recommended_interests_ratio(t) = ...
        sum(sum(c3c_recommended_interests == true_interests)) / ...
        (number_of_consumers * number_of_services);

    c3c_recommended_popularities = zeros(1,number_of_services);
    
    for i = 1:number_of_services
        
        c3c_recommended_popularities(i) = ...
            sum(c3c_recommended_interests(isnan(c3c_recommended_interests(:,i)) == 0,i));
        
    end
    
    [~,c3c_recommended_most_popular_services] = ...
        sort(c3c_recommended_popularities,'descend');
    
    epsilon = 1 - c3c_available_interests_ratio(t);
    
    c3c_distributed_services = ...
        c3c_recommended_most_popular_services(1:floor(network_capacity * (1 - epsilon)));
    
    c3c_distributed_services = horzcat(c3c_distributed_services, ...
        c3c_recommended_most_popular_services ...
        (randi([floor(network_capacity * (1 - epsilon)) + 1,number_of_services], ...
        1,network_capacity - floor(network_capacity * (1 - epsilon))))); %#ok<AGROW>

    for g = 1:number_of_groups
        
        c3c_truely_popular_distributed_services_ratio(g,t) = ...
            length(intersect(c3c_distributed_services, ...
            c3c_should_be_distributed_services(g,:))) ...
            / length(c3c_distributed_services);
        
    end
    
    c3c_total_truely_popular_distributed_services_ratio(t) = ...
        sum(c3c_truely_popular_distributed_services_ratio(:,t) .* ...
        (network_capacity),1) ./ (number_of_groups * network_capacity);
    
    for i = 1:number_of_consumers
        
        c3c_available_interests(i,c3c_distributed_services) = ...
            true_interests(i,c3c_distributed_services);
           
    end 
    
    waitbar(t / duration,handle)
    
    if t == duration
        
        close(handle)
        
    end
    
end

%%

%   Category 3.d with the Upper-Popularity-Bound collaborative
%   non-group-based recommender system:

c3d_available_interests = available_interests;

c3d_available_interests_ratio = zeros(1,duration);
c3d_recommended_interests_ratio = zeros(1,duration);

c3d_true_popularities = ...
    zeros(number_of_groups,number_of_services);
c3d_true_most_popular_services = ...
    zeros(number_of_groups,number_of_services);
c3d_should_be_distributed_services = ...
    zeros(number_of_groups,network_capacity);

number_of_group_consumers = ...
    number_of_consumers / number_of_groups;

for g = 1:number_of_groups
    
    first_group_consumer = number_of_group_consumers * (g - 1) + 1;
    last_group_consumer = number_of_group_consumers * g;
    
    c3d_true_popularities(g,:) = ...
        sum(true_interests(first_group_consumer:last_group_consumer,:),1);
    
    [~,c3d_true_most_popular_services(g,:)] = ...
        sort(c3d_true_popularities(g,:),'descend');
    
    c3d_should_be_distributed_services(g,:) = ...
        c3d_true_most_popular_services(g,1:network_capacity);
    
end

c3d_truely_popular_distributed_services_ratio = ...
    zeros(number_of_groups,duration);
c3d_total_truely_popular_distributed_services_ratio = zeros(1,duration);

handle = waitbar(0,'Please wait ... ');

for t = 1:duration
    
    c3d_available_interests_ratio(t) = ...
        sum(sum(isnan(c3d_available_interests) == 0)) / ...
        (number_of_consumers * number_of_services);
        
    c3d_recommended_interests = generateNGBRecommendations( ...
        number_of_consumers, number_of_services, c3d_available_interests);
    
    c3d_recommended_interests_ratio(t) = ...
        sum(sum(c3d_recommended_interests == true_interests)) / ...
        (number_of_consumers * number_of_services);

    c3d_recommended_popularities = zeros(1,number_of_services);
    c3d_upper_recommended_popularity_bounds = zeros(1,number_of_services);
    
    for i = 1:number_of_services
        
        c3d_recommended_popularities(i) = ...
            sum(c3d_recommended_interests(isnan(c3d_recommended_interests(:,i)) == 0,i));
        
        c3d_upper_recommended_popularity_bounds(i) = ...
            c3d_recommended_popularities(i) + ...
            sum(isnan(c3d_recommended_interests(:,i)));
        
    end
    
    [~,c3d_recommended_most_popular_services] = ...
        sort(c3d_upper_recommended_popularity_bounds,'descend');
    
    c3d_distributed_services = ...
        c3d_recommended_most_popular_services(1:network_capacity);
    
    for g = 1:number_of_groups
        
        c3d_truely_popular_distributed_services_ratio(g,t) = ...
            length(intersect(c3d_distributed_services, ...
            c3d_should_be_distributed_services(g,:))) ...
            / length(c3d_distributed_services);
        
    end
    
    c3d_total_truely_popular_distributed_services_ratio(t) = ...
        sum(c3d_truely_popular_distributed_services_ratio(:,t) .* ...
        (network_capacity),1) ./ (number_of_groups * network_capacity);
    
    for i = 1:number_of_consumers
        
        c3d_available_interests(i,c3d_distributed_services) = ...
            true_interests(i,c3d_distributed_services);
            
    end
    
    waitbar(t / duration,handle)
    
    if t == duration
        
        close(handle)
        
    end
    
end

%%

%   Category 3 summary results:

figure('Name','Category 3 - Interests ratio');
plot(1:duration,c3a_recommended_interests_ratio,'-+b','LineWidth',2, ...
    'MarkerSize',10);
hold on
plot(1:duration,c3b_recommended_interests_ratio,'-*g','LineWidth',2, ...
    'MarkerSize',10);
hold on
plot(1:duration,c3c_recommended_interests_ratio,'-xr','LineWidth',2, ...
    'MarkerSize',10);
hold on
plot(1:duration,c3d_recommended_interests_ratio,'-ok','LineWidth',2, ...
    'MarkerSize',10);
hold on
legend({'Cat 3 - Greedy','Cat 3 - e-greedy', ...
    'Cat 3 - Decaying e-greedy','Cat 3 - UPB'}, ...
    'Location','best','FontSize',18);
hold on
title('Interests ratio vs. time','FontSize',18);
axis([1,duration,0,1.1]);
hold on
xlabel('Time interval','FontSize',18);
hold on
ylabel('Interests ratio','FontSize',18);
hold on
grid on

file_name = ...
    sprintf('c3-interests ratio-setup%3d.fig', ...
    setup);
saveas(gcf,file_name);

file_name = ...
    sprintf('c3-interests ratio-setup%3d.bmp', ...
    setup);
saveas(gcf,file_name);

figure('Name', ...
    'Category 3 - Popular distributed services ratio');
plot(1:duration,c3a_total_truely_popular_distributed_services_ratio,'-+b', ...
    'LineWidth',2,'MarkerSize',10);
hold on
plot(1:duration,c3b_total_truely_popular_distributed_services_ratio,'-*g', ...
    'LineWidth',2,'MarkerSize',10);
hold on
plot(1:duration,c3c_total_truely_popular_distributed_services_ratio,'-xr', ...
    'LineWidth',2,'MarkerSize',10);
hold on
plot(1:duration,c3d_total_truely_popular_distributed_services_ratio,'-ok', ...
    'LineWidth',2,'MarkerSize',10);
hold on
legend({'Cat 3 - Greedy','Cat 3 - e-greedy', ...
    'Cat 3 - Decaying e-greedy','Cat 3 - UPB'}, ...
    'Location','best','FontSize',18);
hold on
title('Popular distributed services ratio vs. time','FontSize',18);
axis([1,duration,0,1.1]);
hold on
xlabel('Time interval','FontSize',18);
hold on
ylabel('Popular distributed services ratio','FontSize',18);
hold on
grid on

file_name = ...
    sprintf('c3-popular distributed services ratio-setup%3d.fig', ...
    setup);
saveas(gcf,file_name);

file_name = ...
    sprintf('c3-popular distributed services ratio-setup%3d.bmp', ...
    setup);
saveas(gcf,file_name);

%%

%   The generateGBRecommendations function:

function recommended_interests = generateGBRecommendations( ...
    number_of_group_consumers, group_index, number_of_services, available_interests)

    jaccard_similarities = ...
        zeros(number_of_group_consumers,number_of_group_consumers);
        
    for i = 1:number_of_group_consumers
            
        for j = 1:number_of_group_consumers
                
            if i == j
                    
                continue;
                    
            else
                    
                jaccard_similarities(i,j) = ...
                    sum(available_interests(group_index,i,:) == ...
                    available_interests(group_index,j,:))...
                    / number_of_services;
                    
            end
                
        end
            
    end
        
	recommended_interests(group_index,:,:) = ...
        available_interests(group_index,:,:);
        
	for i = 1:number_of_group_consumers
            
        for j = 1:number_of_services
                
            if isnan(recommended_interests(group_index,i,j)) == 1
                    
                most_similar_consumers = ...
                    find(jaccard_similarities(i,:) == max(jaccard_similarities(i,:)));
                    
                recommended_interests(group_index,i,j) = ...
                    recommended_interests(group_index,most_similar_consumers(1),j);
                    
            end
                
        end
            
    end
    
end

%%

%   Category 4.a with the greedy collaborative 
%   group-based recommender system:

number_of_group_consumers = ...
    number_of_consumers / number_of_groups;

c4a_available_interests = ...
    zeros(number_of_groups,number_of_group_consumers,number_of_services);
c4a_true_interests = ...
    zeros(number_of_groups,number_of_group_consumers,number_of_services);

for g = 1:number_of_groups
    
    first_group_consumer = number_of_group_consumers * (g - 1) + 1;
    last_group_consumer = number_of_group_consumers * g;
    
    c4a_available_interests(g,:,:) = ...
        available_interests(first_group_consumer:last_group_consumer,:);
    
    c4a_true_interests(g,:,:) = ...
        true_interests(first_group_consumer:last_group_consumer,:);
    
end

c4a_available_interests_ratio = ...
    zeros(number_of_groups,duration);
c4a_recommended_interests = ...
    zeros(number_of_groups,number_of_group_consumers,number_of_services);
c4a_recommended_interests_ratio = ...
    zeros(number_of_groups,duration);

c4a_recommended_popularities = ...
    zeros(number_of_groups,number_of_services);
c4a_recommended_most_popular_services = ...
    zeros(number_of_groups,number_of_services);
c4a_distributed_services = ...
    zeros(number_of_groups,network_capacity);

c4a_true_popularities = ...
    zeros(number_of_groups,number_of_services);
c4a_true_most_popular_services = ...
    zeros(number_of_groups,number_of_services);
c4a_should_be_distributed_services = ...
    zeros(number_of_groups,network_capacity);

for g = 1:number_of_groups
    
    c4a_true_popularities(g,:) = sum(c4a_true_interests(g,:,:),2);
    
    [~,c4a_true_most_popular_services(g,:)] = ...
        sort(c4a_true_popularities(g,:),'descend');
    
    c4a_should_be_distributed_services(g,:) = ...
        c4a_true_most_popular_services(g,1:network_capacity);
    
end

c4a_truely_popular_distributed_services_ratio = ...
    zeros(number_of_groups,duration);

handle = waitbar(0,'Please wait ... ');

for g = 1:number_of_groups
    
    for t = 1:duration
        
        c4a_available_interests_ratio(g,t) = ...
            sum(sum(isnan(c4a_available_interests(g,:,:)) == 0)) / ...
            (number_of_group_consumers * number_of_services);
        
        c4a_recommended_interests = generateGBRecommendations( ...
            number_of_group_consumers, g, number_of_services, c4a_available_interests);
                   
        c4a_recommended_interests_ratio(g,t) = ...
            sum(sum(c4a_recommended_interests(g,:,:) == c4a_true_interests(g,:,:))) / ...
            (number_of_group_consumers * number_of_services);
        
        for i = 1:number_of_services
            
            c4a_recommended_popularities(g,i) = ...
                sum(c4a_recommended_interests( ...
                g,isnan(c4a_recommended_interests(g,:,i)) == 0,i));
            
        end
        
        [~,c4a_recommended_most_popular_services(g,:)] = ...
            sort(c4a_recommended_popularities(g,:),'descend');
        
        c4a_distributed_services(g,:) = ...
            c4a_recommended_most_popular_services(g,1:network_capacity);
        
        c4a_truely_popular_distributed_services_ratio(g,t) = ...
            length(intersect(c4a_distributed_services(g,:), ...
            c4a_should_be_distributed_services(g,:))) ...
            / length(c4a_distributed_services(g,:));
        
        for i = 1:number_of_group_consumers
            
            c4a_available_interests(g,i,c4a_distributed_services(g,:)) = ...
                c4a_true_interests(g,i,c4a_distributed_services(g,:));
            
        end
        
        waitbar(((g - 1) * duration + t) / (number_of_groups * duration),handle)
        
        if (g * t) == (number_of_groups * duration)
            
            close(handle)
            
        end
        
    end
    
end
    
c4a_total_recommended_interests_ratio = ...
    sum(c4a_recommended_interests_ratio .* ...
    (number_of_group_consumers * number_of_services),1) ...
    ./ (number_of_consumers * number_of_services);

c4a_total_truely_popular_distributed_services_ratio = ...
    sum(c4a_truely_popular_distributed_services_ratio .* ...
    (network_capacity),1) ./ (number_of_groups * network_capacity);

%%

%   Category 4.b with the epsilon-greedy collaborative
%   group-based recommender system:

number_of_group_consumers = ...
    number_of_consumers / number_of_groups;

c4b_available_interests = ...
    zeros(number_of_groups,number_of_group_consumers,number_of_services);
c4b_true_interests = ...
    zeros(number_of_groups,number_of_group_consumers,number_of_services);

for g = 1:number_of_groups
    
    first_group_consumer = number_of_group_consumers * (g - 1) + 1;
    last_group_consumer = number_of_group_consumers * g;
    
    c4b_available_interests(g,:,:) = ...
        available_interests(first_group_consumer:last_group_consumer,:);
    
    c4b_true_interests(g,:,:) = ...
        true_interests(first_group_consumer:last_group_consumer,:);
    
end

c4b_available_interests_ratio = ...
    zeros(number_of_groups,duration);
c4b_recommended_interests = ...
    zeros(number_of_groups,number_of_group_consumers,number_of_services);
c4b_recommended_interests_ratio = ...
    zeros(number_of_groups,duration);

c4b_recommended_popularities = ...
    zeros(number_of_groups,number_of_services);
c4b_recommended_most_popular_services = ...
    zeros(number_of_groups,number_of_services);
c4b_distributed_services = ...
    zeros(number_of_groups,network_capacity);

c4b_true_popularities = ...
    zeros(number_of_groups,number_of_services);
c4b_true_most_popular_services = ...
    zeros(number_of_groups,number_of_services);
c4b_should_be_distributed_services = ...
    zeros(number_of_groups,network_capacity);

for g = 1:number_of_groups
    
    c4b_true_popularities(g,:) = sum(c4b_true_interests(g,:,:),2);
    
    [~,c4b_true_most_popular_services(g,:)] = ...
        sort(c4b_true_popularities(g,:),'descend');
    
    c4b_should_be_distributed_services(g,:) = ...
        c4b_true_most_popular_services(g,1:network_capacity);
    
end

c4b_truely_popular_distributed_services_ratio = ...
    zeros(number_of_groups,duration);
    
handle = waitbar(0,'Please wait ... ');

for g = 1:number_of_groups
    
    for t = 1:duration
        
        c4b_available_interests_ratio(g,t) = ...
            sum(sum(isnan(c4b_available_interests(g,:,:)) == 0)) / ...
            (number_of_group_consumers * number_of_services);
        
        c4b_recommended_interests = generateGBRecommendations( ...
            number_of_group_consumers, g, number_of_services, c4b_available_interests);       
                
        c4b_recommended_interests_ratio(g,t) = ...
            sum(sum(c4b_recommended_interests(g,:,:) == c4b_true_interests(g,:,:))) / ...
            (number_of_group_consumers * number_of_services);
        
        for i = 1:number_of_services
            
            c4b_recommended_popularities(g,i) = ...
                sum(c4b_recommended_interests( ...
                g,isnan(c4b_recommended_interests(g,:,i)) == 0,i));
            
        end
        
        [~,c4b_recommended_most_popular_services(g,:)] = ...
            sort(c4b_recommended_popularities(g,:),'descend');
        
        epsilon = unknown_interests_ratio;
        
        c4b_distributed_services(g,1:floor(network_capacity * (1 - epsilon))) = ...
            c4b_recommended_most_popular_services(g,1:floor(network_capacity * (1 - epsilon)));
        
        c4b_distributed_services ...
            (g,floor(network_capacity * (1 - epsilon)) + 1:network_capacity) = ...
            c4b_recommended_most_popular_services ...
            (g,randi([floor(network_capacity * (1 - epsilon)) + 1,number_of_services], ...
            1,network_capacity - floor(network_capacity * (1 - epsilon))));
        
        c4b_truely_popular_distributed_services_ratio(g,t) = ...
            length(intersect(c4b_distributed_services(g,:), ...
            c4b_should_be_distributed_services(g,:))) ...
            / length(c4b_distributed_services(g,:));
        
        for i = 1:number_of_group_consumers
            
            c4b_available_interests(g,i,c4b_distributed_services(g,:)) = ...
                c4b_true_interests(g,i,c4b_distributed_services(g,:));
                
        end
        
        waitbar(((g - 1) * duration + t) / (number_of_groups * duration),handle)
        
        if (g * t) == (number_of_groups * duration)
            
            close(handle)
            
        end
        
    end
    
end
    
c4b_total_recommended_interests_ratio = ...
    sum(c4b_recommended_interests_ratio .* ...
    (number_of_group_consumers * number_of_services),1) ...
    ./ (number_of_consumers * number_of_services);

c4b_total_truely_popular_distributed_services_ratio = ...
    sum(c4b_truely_popular_distributed_services_ratio .* ...
    (network_capacity),1) ./ (number_of_groups * network_capacity);

%%

%   Category 4.c with the decaying epsilon-greedy collaborative 
%   group-based recommender system:

number_of_group_consumers = ...
    number_of_consumers / number_of_groups;

c4c_available_interests = ...
    zeros(number_of_groups,number_of_group_consumers,number_of_services);
c4c_true_interests = ...
    zeros(number_of_groups,number_of_group_consumers,number_of_services);

for g = 1:number_of_groups
    
    first_group_consumer = number_of_group_consumers * (g - 1) + 1;
    last_group_consumer = number_of_group_consumers * g;
    
    c4c_available_interests(g,:,:) = ...
        available_interests(first_group_consumer:last_group_consumer,:);
    
    c4c_true_interests(g,:,:) = ...
        true_interests(first_group_consumer:last_group_consumer,:);
    
end

c4c_available_interests_ratio = ...
    zeros(number_of_groups,duration);
c4c_recommended_interests = ...
    zeros(number_of_groups,number_of_group_consumers,number_of_services);
c4c_recommended_interests_ratio = ...
    zeros(number_of_groups,duration);

c4c_recommended_popularities = ...
    zeros(number_of_groups,number_of_services);
c4c_recommended_most_popular_services = ...
    zeros(number_of_groups,number_of_services);
c4c_distributed_services = ...
    zeros(number_of_groups,network_capacity);

c4c_true_popularities = ...
    zeros(number_of_groups,number_of_services);
c4c_true_most_popular_services = ...
    zeros(number_of_groups,number_of_services);
c4c_should_be_distributed_services = ...
    zeros(number_of_groups,network_capacity);

for g = 1:number_of_groups
    
    c4c_true_popularities(g,:) = sum(c4c_true_interests(g,:,:),2);
    
    [~,c4c_true_most_popular_services(g,:)] = ...
        sort(c4c_true_popularities(g,:),'descend');
    
    c4c_should_be_distributed_services(g,:) = ...
        c4c_true_most_popular_services(g,1:network_capacity);
    
end

c4c_truely_popular_distributed_services_ratio = ...
    zeros(number_of_groups,duration);
    
handle = waitbar(0,'Please wait ... ');

for g = 1:number_of_groups
    
    for t = 1:duration
        
        c4c_available_interests_ratio(g,t) = ...
            sum(sum(isnan(c4c_available_interests(g,:,:)) == 0)) / ...
            (number_of_group_consumers * number_of_services);
        
        c4c_recommended_interests = generateGBRecommendations( ...
            number_of_group_consumers, g, number_of_services, c4c_available_interests);
        
        c4c_recommended_interests_ratio(g,t) = ...
            sum(sum(c4c_recommended_interests(g,:,:) == c4c_true_interests(g,:,:))) / ...
            (number_of_group_consumers * number_of_services);
        
        for i = 1:number_of_services
            
            c4c_recommended_popularities(g,i) = ...
                sum(c4c_recommended_interests( ...
                g,isnan(c4c_recommended_interests(g,:,i)) == 0,i));
            
        end
        
        [~,c4c_recommended_most_popular_services(g,:)] = ...
            sort(c4c_recommended_popularities(g,:),'descend');
        
        epsilon = 1 - c4c_available_interests_ratio(g,t);
        
        c4c_distributed_services(g,1:floor(network_capacity * (1 - epsilon))) = ...
            c4c_recommended_most_popular_services(g,1:floor(network_capacity * (1 - epsilon)));
        
        c4c_distributed_services ...
            (g,floor(network_capacity * (1 - epsilon)) + 1:network_capacity) = ...
            c4c_recommended_most_popular_services ...
            (g,randi([floor(network_capacity * (1 - epsilon)) + 1,number_of_services], ...
            1,network_capacity - floor(network_capacity * (1 - epsilon))));
        
        c4c_truely_popular_distributed_services_ratio(g,t) = ...
            length(intersect(c4c_distributed_services(g,:), ...
            c4c_should_be_distributed_services(g,:))) ...
            / length(c4c_distributed_services(g,:));
        
        for i = 1:number_of_group_consumers
            
            c4c_available_interests(g,i,c4c_distributed_services(g,:)) = ...
                c4c_true_interests(g,i,c4c_distributed_services(g,:));
                
        end
        
        waitbar(((g - 1) * duration + t) / (number_of_groups * duration),handle)
        
        if (g * t) == (number_of_groups * duration)
            
            close(handle)
            
        end
        
    end
    
end
    
c4c_total_recommended_interests_ratio = ...
    sum(c4c_recommended_interests_ratio .* ...
    (number_of_group_consumers * number_of_services),1) ...
    ./ (number_of_consumers * number_of_services);

c4c_total_truely_popular_distributed_services_ratio = ...
    sum(c4c_truely_popular_distributed_services_ratio .* ...
    (network_capacity),1) ./ (number_of_groups * network_capacity);

%%

%   Category 4.d with the Upper-Popularity-Bound collaborative
%   group-based recommender system:

number_of_group_consumers = ...
    number_of_consumers / number_of_groups;

c4d_available_interests = ...
    zeros(number_of_groups,number_of_group_consumers,number_of_services);
c4d_true_interests = ...
    zeros(number_of_groups,number_of_group_consumers,number_of_services);

for g = 1:number_of_groups
    
    first_group_consumer = number_of_group_consumers * (g - 1) + 1;
    last_group_consumer = number_of_group_consumers * g;
    
    c4d_available_interests(g,:,:) = ...
        available_interests(first_group_consumer:last_group_consumer,:);
    
    c4d_true_interests(g,:,:) = ...
        true_interests(first_group_consumer:last_group_consumer,:);
    
end

c4d_available_interests_ratio = ...
    zeros(number_of_groups,duration);
c4d_recommended_interests = ...
    zeros(number_of_groups,number_of_group_consumers,number_of_services);
c4d_recommended_interests_ratio = ...
    zeros(number_of_groups,duration);

c4d_recommended_popularities = ...
    zeros(number_of_groups,number_of_services);
c4d_upper_recommended_popularity_bounds = ...
    zeros(number_of_groups,number_of_services);
c4d_recommended_most_popular_services = ...
    zeros(number_of_groups,number_of_services);
c4d_distributed_services = ...
    zeros(number_of_groups,network_capacity);

c4d_true_popularities = ...
    zeros(number_of_groups,number_of_services);
c4d_true_most_popular_services = ...
    zeros(number_of_groups,number_of_services);
c4d_should_be_distributed_services = ...
    zeros(number_of_groups,network_capacity);

for g = 1:number_of_groups
    
    c4d_true_popularities(g,:) = sum(c4d_true_interests(g,:,:),2);
    
    [~,c4d_true_most_popular_services(g,:)] = ...
        sort(c4d_true_popularities(g,:),'descend');
    
    c4d_should_be_distributed_services(g,:) = ...
        c4d_true_most_popular_services(g,1:network_capacity);
    
end

c4d_truely_popular_distributed_services_ratio = ...
    zeros(number_of_groups,duration);
    
handle = waitbar(0,'Please wait ... ');

for g = 1:number_of_groups
    
    for t = 1:duration
        
        c4d_available_interests_ratio(g,t) = ...
            sum(sum(isnan(c4d_available_interests(g,:,:)) == 0)) / ...
            (number_of_group_consumers * number_of_services);
        
        c4d_recommended_interests = generateGBRecommendations( ...
            number_of_group_consumers, g, number_of_services, c4d_available_interests);
        
        c4d_recommended_interests_ratio(g,t) = ...
            sum(sum(c4d_recommended_interests(g,:,:) == c4d_true_interests(g,:,:))) / ...
            (number_of_group_consumers * number_of_services);
        
        for i = 1:number_of_services
            
            c4d_recommended_popularities(g,i) = ...
                sum(c4d_recommended_interests( ...
                g,isnan(c4d_recommended_interests(g,:,i)) == 0,i));
            
            c4d_upper_recommended_popularity_bounds(g,i) = ...
                c4d_recommended_popularities(g,i) + ...
                sum(isnan(c4d_recommended_interests(g,:,i)));
            
        end
        
        [~,c4d_recommended_most_popular_services(g,:)] = ...
            sort(c4d_upper_recommended_popularity_bounds(g,:),'descend');
        
        c4d_distributed_services(g,:) = ...
            c4d_recommended_most_popular_services(g,1:network_capacity);
        
        c4d_truely_popular_distributed_services_ratio(g,t) = ...
            length(intersect(c4d_distributed_services(g,:), ...
            c4d_should_be_distributed_services(g,:))) ...
            / length(c4d_distributed_services(g,:));
        
        for i = 1:number_of_group_consumers
            
            c4d_available_interests(g,i,c4d_distributed_services(g,:)) = ...
                c4d_true_interests(g,i,c4d_distributed_services(g,:));
                
        end
        
        waitbar(((g - 1) * duration + t) / (number_of_groups * duration),handle)
        
        if (g * t) == (number_of_groups * duration)
            
            close(handle)
            
        end
        
    end
    
end
    
c4d_total_recommended_interests_ratio = ...
    sum(c4d_recommended_interests_ratio .* ...
    (number_of_group_consumers * number_of_services),1) ...
    ./ (number_of_consumers * number_of_services);

c4d_total_truely_popular_distributed_services_ratio = ...
    sum(c4d_truely_popular_distributed_services_ratio .* ...
    (network_capacity),1) ./ (number_of_groups * network_capacity);

%%

%   Category 4 summary results:

figure('Name','Category 4 - Interests ratio');
plot(1:duration,c4a_total_recommended_interests_ratio,'-+b','LineWidth',2, ...
    'MarkerSize',10);
hold on
plot(1:duration,c4b_total_recommended_interests_ratio,'-*g','LineWidth',2, ...
    'MarkerSize',10);
hold on
plot(1:duration,c4c_total_recommended_interests_ratio,'-xr','LineWidth',2, ...
    'MarkerSize',10);
hold on
plot(1:duration,c4d_total_recommended_interests_ratio,'-ok','LineWidth',2, ...
    'MarkerSize',10);
hold on
legend({'Cat 4 - Greedy','Cat 4 - e-greedy', ...
    'Cat 4 - Decaying e-greedy','Cat 4 - UPB'}, ...
    'Location','best','FontSize',18);
hold on
title('Interests ratio vs. time','FontSize',18);
axis([1,duration,0,1.1]);
hold on
xlabel('Time interval','FontSize',18);
hold on
ylabel('Interests ratio','FontSize',18);
hold on
grid on

file_name = ...
    sprintf('c4-interests ratio-setup%3d.fig', ...
    setup);
saveas(gcf,file_name);

file_name = ...
    sprintf('c4-interests ratio-setup%3d.bmp', ...
    setup);
saveas(gcf,file_name);

figure('Name', ...
    'Category 4 - Popular distributed services ratio');
plot(1:duration,c4a_total_truely_popular_distributed_services_ratio,'-+b', ...
    'LineWidth',2,'MarkerSize',10);
hold on
plot(1:duration,c4b_total_truely_popular_distributed_services_ratio,'-*g', ...
    'LineWidth',2,'MarkerSize',10);
hold on
plot(1:duration,c4c_total_truely_popular_distributed_services_ratio,'-xr', ...
    'LineWidth',2,'MarkerSize',10);
hold on
plot(1:duration,c4d_total_truely_popular_distributed_services_ratio,'-ok', ...
    'LineWidth',2,'MarkerSize',10);
hold on
legend({'Cat 4 - Greedy','Cat 4 - e-greedy', ...
    'Cat 4 - Decaying e-greedy','Cat 4 - UPB'}, ...
    'Location','best','FontSize',18);
hold on
title('Popular distributed services ratio vs. time','FontSize',18);
axis([1,duration,0,1.1]);
hold on
xlabel('Time interval','FontSize',18);
hold on
ylabel('Popular distributed services ratio','FontSize',18);
hold on
grid on

file_name = ...
    sprintf('c4-popular distributed services ratio-setup%3d.fig', ...
    setup);
saveas(gcf,file_name);

file_name = ...
    sprintf('c4-popular distributed services ratio-setup%3d.bmp', ...
    setup);
saveas(gcf,file_name);

%%

%   Saving all results:

file_name = sprintf('setup %3d results.mat',setup);
save(file_name);

%%

%   Written by "Kais Suleiman" (ksuleiman.weebly.com)