# myTeam.py
# ---------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

import random

import util
from captureAgents import CaptureAgent
from game import Directions
from util import nearestPoint


#################
# Team creation #
#################

# noinspection PyUnusedLocal
def createTeam(firstIndex, secondIndex, isRed,
               first='MainAgent', second='MainAgent'):
    """
    This function should return a list of two agents that will form the
    team, initialized using firstIndex and secondIndex as their agent
    index numbers.  isRed is True if the red team is being created, and
    will be False if the blue team is being created.
    As a potentially helpful development aid, this function can take
    additional string-valued keyword arguments ("first" and "second" are
    such arguments in the case of this function), which will come from
    the --redOpts and --blueOpts command-line arguments to capture.py.
    For the nightly contest, however, your team will be created without
    any extra arguments, so you should make sure that the default
    behavior is what you want for the nightly contest.
    """
    agent1 = eval(first)(firstIndex)
    agent2 = eval(second)(secondIndex)

    agent1.setOtherAgent(agent2)
    agent2.setOtherAgent(agent1)

    agent1.setThreatened(False)
    agent2.setThreatened(False)

    agent1.setNorthBias(True)
    agent2.setNorthBias(False)

    return [agent1, agent2]


##########
# Agents #
##########


class MainAgent(CaptureAgent):
    # noinspection PyUnusedLocal
    def registerInitialState(self, gameState):
        """
        This method handles the initial setup of the
        agent to populate useful fields (such as what team
        we're on).

        A distanceCalculator instance caches the maze distances
        between each pair of positions, so your agents can use:
        self.distancer.getDistance(p1, p2)
        IMPORTANT: This method may run for at most 15 seconds.
        """

        ''' 
        Make sure you do not delete the following line. If you would like to
        use Manhattan distances instead of maze distances in order to save
        on initialization time, please take a look at
        CaptureAgent.registerInitialState in captureAgents.py. 
        '''
        CaptureAgent.registerInitialState(self, gameState)

        ''' 
        Your initialization code goes here, if you need any.
        '''
        if self.red:
            self.agentsOnTeam = gameState.getRedTeamIndices()

        else:
            self.agentsOnTeam = gameState.getBlueTeamIndices()

        # Avoid target being None
        x = int(gameState.getWalls().width / 2)
        y = int(gameState.getWalls().height / 2)

        self.center = (x, y)

        self.goToCenter(gameState)

    def chooseAction(self, gameState):
        """
        Picks among the actions with the highest Q(s,a).
        """
        evaluateType = 'attack'

        if not self.reachedCenter:
            evaluateType = 'goToCenter'

        agentCurrentPosition = self.getCurrentAgentPosition(gameState)

        if agentCurrentPosition == self.center and not self.reachedCenter:
            evaluateType = 'attack'
            self.reachedCenter = True

        opponentPositions = self.getOpponentPositions(gameState)

        if opponentPositions:
            for index, pos in opponentPositions:
                if self.getMazeDistance(agentCurrentPosition, pos) < 6 and self.isAtHome(gameState):
                    evaluateType = 'defense'
                    break

        actions = gameState.getLegalActions(self.index)
        values = [self.evaluate(gameState, a, evaluateType) for a in actions]

        maxValue = max(values)
        bestActions = [a for a, v in zip(actions, values) if v == maxValue]

        return random.choice(bestActions)

    def getSuccessor(self, gameState, action):
        """
        Finds the next successor which is a grid position (location tuple).
        """
        successor = gameState.generateSuccessor(self.index, action)
        agentCurrentPosition = successor.getAgentState(self.index).getPosition()

        if agentCurrentPosition != nearestPoint(agentCurrentPosition):
            # Only half a grid position was covered
            return successor.generateSuccessor(self.index, action)
        else:
            return successor

    def evaluate(self, gameState, action, agentType='attack'):
        """
        Computes a linear combination of features and feature weights
        """
        global features
        weights = self.getWeights()

        if agentType == 'attack':
            features = self.getFeaturesForAttack(gameState, action)

        elif agentType == 'defense':
            features = self.getFeaturesForDefense(gameState, action)

        elif agentType == 'goToCenter':
            features = self.getFeaturesForGoingToCenter(gameState, action)

        return sum(features[key] * weights.get(key, 0) for key in features)

    def getFeaturesForAttack(self, gameState, action):
        attackFeatures = util.Counter()
        successor = self.getSuccessor(gameState, action)

        attackFeatures['successorScore'] = self.getScore(successor)

        attackFeatures['distanceToFood'] = self.getDistanceToClosestFood(successor)

        closestCapsuleDistance = self.getDistanceToClosestCapsule(gameState, successor)

        if closestCapsuleDistance == 0:
            closestCapsuleDistance = 0.1

        if closestCapsuleDistance is not None:
            attackFeatures['distanceToCapsule'] = 1.0 / closestCapsuleDistance

        if not self.isAtHome(successor):
            distanceToAgent = self.getDistanceToTeammate(successor)

            if distanceToAgent is not None:
                attackFeatures['distanceToTeammate'] = 1.0 / distanceToAgent

        enemyIndex, enemyDistance = self.getIndexAndDistanceToDetectedEnemy(successor)

        safeEnemyDistance = 4

        if enemyDistance is not None:
            if enemyDistance <= safeEnemyDistance:
                self.threatened = True

                if gameState.getAgentState(enemyIndex).scaredTimer > 1:
                    attackFeatures['distanceToOpponent'] = 0

                else:
                    if closestCapsuleDistance is not None:
                        attackFeatures['distanceToCapsuleThreatened'] = closestCapsuleDistance

                    attackFeatures['distanceToOpponent'] = 1.0 / enemyDistance

                    if self.isAtHome(successor) and self.getCurrentAgentScaredTime(successor) <= 1:
                        attackFeatures['atHomeThreatened'] = 1

                    if enemyDistance <= 1:
                        attackFeatures['suicide'] = 1

        if enemyDistance is None or enemyDistance > safeEnemyDistance:
            self.threatened = False

        safeClosestCapsuleDistance = 5

        if self.otherAgent.threatened and closestCapsuleDistance is not None and closestCapsuleDistance\
                <= safeClosestCapsuleDistance:
            attackFeatures['distanceToCapsuleThreatened'] = closestCapsuleDistance

        # Actions to avoid
        if action == Directions.STOP:
            attackFeatures['stop'] = 1

        reverse = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]

        if action == reverse:
            attackFeatures['reverse'] = 1

        return attackFeatures
    
    def getFeaturesForDefense(self, gameState, action):
        defenseFeatures = util.Counter()
        successor = self.getSuccessor(gameState, action)

        enemies = [successor.getAgentState(opponent) for opponent in self.getOpponents(successor)]
        invaders = [enemy for enemy in enemies if enemy.isPacman and enemy.getPosition() is not None]
        defenseFeatures['numberOfInvaders'] = len(invaders)

        if invaders:
            minimumEnemyIndex, minimumDistance = self.getIndexAndDistanceToDetectedEnemy(successor)
            defenseFeatures['invaderDistance'] = minimumDistance

            if minimumDistance <= 1 and self.getCurrentAgentScaredTime(successor) > 0 and self.isAtHome(successor):
                defenseFeatures['suicide'] = 1

            if not self.isAtHome(successor) and minimumDistance <= 1:
                defenseFeatures['suicide'] = 1

        # Actions to avoid
        if action == Directions.STOP:
            defenseFeatures['stop'] = 0

        reverse = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]

        if action == reverse:
            defenseFeatures['reverse'] = 1

        return defenseFeatures

    def getFeaturesForGoingToCenter(self, gameState, action):
        gotToCenterFeatures = util.Counter()
        successor = self.getSuccessor(gameState, action)

        currentAgentPosition = self.getCurrentAgentPosition(successor)

        distanceToCenter = self.getMazeDistance(currentAgentPosition, self.center)
        gotToCenterFeatures['distanceToCenter'] = distanceToCenter

        if currentAgentPosition == self.center:
            gotToCenterFeatures['atCenter'] = 1

        return gotToCenterFeatures

    def getWeights(self):
        return {'numberOfInvaders': -1000, 'invaderDistance': -10, 'stop': -100, 'reverse': -2, 'suicide': -5000,
                'successorScore': 200, 'distanceToFood': -5, 'distanceToTeammate': -40, 'distanceToOpponent': -225,
                'distanceToCapsule': 45, 'distanceToCapsuleThreatened': -230, 'atHomeThreatened': 400,
                'distanceToCenter': -10, 'atCenter': 100}

    # Utility methods
    def setOtherAgent(self, other):
        self.otherAgent = other

    def setThreatened(self, val):
        self.threatened = val

    def setNorthBias(self, val):
        self.northBias = val

    def getCurrentAgentPosition(self, gameState):
        return gameState.getAgentState(self.index).getPosition()

    def getCurrentAgentScaredTime(self, gameState):
        return gameState.getAgentState(self.index).scaredTimer
    
    def isAttacking(self, gameState):
        return gameState.getAgentState(self.index).isPacman

    def isAtHome(self, gameState):
        return not self.isAttacking(gameState)

    def getOpponentPositions(self, gameState):
        enemiesAndPositions = [(enemy, gameState.getAgentPosition(enemy)) for enemy in self.getOpponents(gameState)]
        return [element for element in enemiesAndPositions if None not in element]

    def getDistanceToTeammate(self, gameState):
        distanceToAgent = None

        if self.index != self.agentsOnTeam[0]:
            otherAgentIndex = self.agentsOnTeam[0]
            otherAgentPosition = gameState.getAgentState(otherAgentIndex).getPosition()
            distanceToAgent = self.getMazeDistance(self.getCurrentAgentPosition(gameState), otherAgentPosition)

            if distanceToAgent == 0:
                distanceToAgent = 0.5

        return distanceToAgent

    def getDistanceToClosestFood(self, gameState):
        try:
            return min([self.getMazeDistance(self.getCurrentAgentPosition(gameState), food)
                        for food in self.getFood(gameState).asList()])
        except ValueError:
            return None

    def getIndexAndDistanceToDetectedEnemy(self, gameState):
        agentCurrentPosition = self.getCurrentAgentPosition(gameState)

        try:
            enemyIndex, enemyDistance = min([(index, self.getMazeDistance(agentCurrentPosition, enemyPosition))
                                             for (index, enemyPosition) in self.getOpponentPositions(gameState)])
            if enemyDistance == 0:
                enemyDistance = 0.5

            return enemyIndex, enemyDistance

        except ValueError:
            return None, None

    def getDistanceToClosestCapsule(self, gameState, successor):
        if len(self.getCapsules(successor)) < len(self.getCapsules(gameState)):
            return 0

        else:
            try:
                return min([self.getMazeDistance(self.getCurrentAgentPosition(successor), capsulePosition)
                            for capsulePosition in self.getCapsules(successor)])
            except ValueError:
                return None

    def goToCenter(self, gameState):
        self.reachedCenter = False

        # Get geographical center
        x = int(gameState.getWalls().width / 2)
        y = int(gameState.getWalls().height / 2)

        # Adjust center x for red
        if self.red:
            x = x - 1

        if self.northBias:
            maxHeight = gameState.getWalls().height
            locations = [(x, thisY) for thisY in range(maxHeight - y, maxHeight, +1) if not gameState.hasWall(x, thisY)]
        else:
            locations = [(x, thisY) for thisY in range(y, 0, -1) if not gameState.hasWall(x, thisY)]

        self.center = sorted(locations, key=lambda location: self.getMazeDistance(
            self.getCurrentAgentPosition(gameState), location))[0]
