# Intelligent-Pac-Man
### In Collaboration with [Andy Vitek](https://github.com/apvitek)<br/><br/>

<img src="https://i.imgur.com/kopKUYn.png">

## Prompt
 
This project involves a multi-player capture-the-flag variant of Pac-Man, where agents control both Pac-Man and ghosts in coordinated team-based strategies. The goal is to develop a team that will try to eat the food on the far side of the map, while defending the food on the home side.


<center><img src="https://i.imgur.com/20yA8Uo.png"></center>

## Problems Modeling and Representation (initial thoughts)
We originally thought that the best strategy would be for one team member to be always defending, and for the other to be always attacking. Because of this, we designed two different agents, called AttackingAgent and DefendingAgent, both a subclass of a more general class called MainAgent; the two agents had different evaluation functions with different weights, representing different features needed for their role. However, we quickly realized that this approach would not work; our agents would win a few games by a great margin, and lose spectacularly majority of the times, because the defending agent would be eaten by an attacking agent all the pellets would be eaten before it had a chance to move back through the corridor near the origin.

Ultimately, we decided that the agents would change the way they operate based on a simple logic: at the start of the game, they would simply try to get to the center of the maze, while trying to maximize the distance between each other, and they would start attacking or defending based on the actions of the enemy agents once the center was reached. To implement this, we eliminated the two sub-classes, and modified the evaluation function of the agents to choose what state to be in (reaching the center, attacking, or defending) based on the circumstances.
## Computational Strategy to Solve Problems and Algorithmic Choices

**The intuition to Pac-Man's movements are determined as follows:**
1. When a new MainAgent is instantiated, we simply assign the current team indices to a property in the agent (for simplicity of later reference), mark them as not being in danger (through another agent’s property), and giving them either a north bias or a south bias (for reaching the center in separate parts of the maze, if possible). Thus, the initialization time is negligible.

2. We set the agent to using the “goToCenter” evaluation, where the features and weight simply rely on how far the agent is from the “center” of the maze, calculated either with a south or north bias, and whether that center was reached or not. This allows the agents not to stall in the maze initial corridor, and not to linger in their own territory at the start of the game, waiting to be attacked.

3. We implemented the “chooseAction” method to dynamically compute whether the agent should attack, defend, or reach the center; when the agent reaches the center, it is by default set to attack, unless the estimated position of one of the enemy agents is closer than an arbitrary number of tiles (in our case, 6), in which case the agent is set to defend.

4. We implemented the ‘evaluate” method to get the features and weights relevant to the agent’s current role, and simply return their dot product to produce an evaluation of the goodness of a successor state.

5. We added three functions, called “getFeaturesForAttack”, “getFeaturesForDefense”, and “getFeaturesForGoingToCenter”, which return the features of the corresponding agent roles. The features were devised based on watching dozens of games, either of our own agent or of other agents designed by our classmates.

      a) Features for attacking include distance to a capsule while a teammate is under threat, estimated distance to nearby enemy, and distance to teammate, in order to encourage agents to spread out while both attacking in order to eat the largest number of pellets.
      
      b) Features for defense include number of enemies currently attacking our territory, and the distance to the closest attacker, if not scared.

      c) Features for going to center include distance to said center, and whether the center was reached.
6. We implemented a separate “getWeights” function to return the weights all of the features we identified, which were calculated based on playing 100 iterations of a game with a certain value and then retried until we were losing as little as 3% of the games against the baseline team.

        [+] Contestant Result
        This Pac-Man scored the 5th out of 50 other contestants.
