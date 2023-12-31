"""
tuned 4x4

approccio  genetico/q-learning

l'agente impara col q-learning per num_training_episodes
poi viene valutato su num_test_episodes

scelta dei genitori stocastic beam search:
più l'agente è adatto e più probabilità ha di essere scelto

la nuova generazione viene prodotta dai due migliori

il crossover viene fatto riga per riga

i genitori scelti faranno parte della nuova generazione per non rischiare
di peggiorare il caso migliore

"""
import gym
import time
import random
import numpy as np

import matplotlib.pyplot as plt

from IPython.display import clear_output

def select_parent(score):
    max1=0
    max2=0
    x1=0
    x2=0
    for x in score.keys():
        if score[x]>max1:
            max2=max1
            x2=x1
            max1=score[x]
            x1=x
    return x1,x2

def select_parent2(score):
    s=sum(list(score.values()))
    if s==0:
        p=np.random.choice(list(score.keys()),2)
    else:
        p=np.random.choice(list(score.keys()),2,[i/s for i in list(score.values())])
    return p[0],p[1]

def crossover(q_a,q_b):
    a,b=np.shape(q_a)
    c = random.randint(0,a*b-1)

    nq_a=np.zeros((a,b))
    nq_b=np.zeros((a,b))

    for i in range(0,a):
        for j in range(0,b):
            if (i*b+j) <c:
                nq_a[int(i),int(j)]=q_a[int(i),int(j)]
                nq_b[i,j]=q_b[i,j]
            else:
                nq_a[i,j]=q_b[i,j]
                nq_b[i,j]=q_a[i,j]
    return nq_a,nq_b

def crossover2(q_a,q_b):
    a,b=np.shape(q_a)
    c = random.randint(0,a-1)

    nq_a=np.zeros((a,b))
    nq_b=np.zeros((a,b))

    for i in range(0,a):
            if i<c:
                nq_a[i]=q_a[i]
                nq_b[i]=q_b[i]
            else:
                nq_a[i]=q_b[i]
                nq_b[i]=q_a[i]
    return nq_a,nq_b

env = gym.make('FrozenLake-v0')
action_space_size=env.action_space.n
state_space_size = env.observation_space.n

population_size=10

q_table = np.random.rand(population_size,state_space_size, action_space_size)

num_generation=20
num_training_episodes = 1000
num_test_episode=1000
max_steps_per_episode = 1000

learning_rate = 0.1
discount_rate = 0.99

exploration_rate = 1
max_exploration_rate = 1
min_exploration_rate = 0.01
exploration_decay_rate = 0.001

score=[]
index=0
max_value=0

for gen in range(num_generation):
    print("generation",gen)
    rewards_all_episodes = {}
    for agent in range(population_size):
        print("agent",agent)
        exploration_rate = 1
        for episode in range(num_training_episodes):
            state = env.reset()
            done = False
            rewards_current_episode = 0
            for step in range(max_steps_per_episode):
                exploration_rate_threshold = random.uniform(0, 1)
                if exploration_rate_threshold > exploration_rate:
                    action = np.argmax(q_table[agent,state,:])
                else:
                    action = env.action_space.sample()

                new_state, reward, done, info = env.step(action)
                q_table[agent,state, action] = q_table[agent,state, action] * (1 - learning_rate) + learning_rate * (reward + discount_rate * np.max(q_table[agent,new_state, :]))
                state = new_state
                if done == True:
                    break
            exploration_rate = min_exploration_rate + (max_exploration_rate - min_exploration_rate) * np.exp(-exploration_decay_rate*episode)
    for agent in range(population_size):
        for episode in range(num_test_episode):
            state = env.reset()
            done = False
            rewards_current_episode = 0
            for step in range(max_steps_per_episode):

                action = np.argmax(q_table[agent,state,:])

                new_state, reward, done, info = env.step(action)
                state = new_state
                rewards_current_episode += reward
                if done == True:
                    break
            if agent in rewards_all_episodes:
                rewards_all_episodes[agent]=rewards_current_episode+rewards_all_episodes[agent]
            else:
                rewards_all_episodes[agent]=rewards_current_episode

    print(rewards_all_episodes)
    new_q_table=q_table.copy()
    for i in range(int((population_size-2)/2)):
        g1,g2=select_parent2(rewards_all_episodes)
        new_q_table[i],new_q_table[i+int(population_size/2)]=crossover2(q_table[int(g1),:,:].copy(),q_table[int(g2),:,:].copy())
    g1,g2=select_parent(rewards_all_episodes)
    new_q_table[8]=q_table[int(g1),:,:].copy()
    new_q_table[9]=q_table[int(g2),:,:].copy()
    q_table=new_q_table
    maxx=0
    for i in rewards_all_episodes.keys():
        if maxx<rewards_all_episodes[i]:
            maxx=rewards_all_episodes[i]
    score.append(maxx)
    if maxx>max_value:
        max_value=maxx
        index=gen

print(rewards_all_episodes)

plt.ylim(0,1)
plt.plot([i for i in range(1,num_generation+1)],[s/num_test_episode for s in score],label="success rate")
print(index,max_value)
plt.plot(index+1, max_value/num_test_episode, 'ro',color='red',label="max success rate")
plt.legend()
plt.savefig("frozenLakeGenetico4x4.png")

