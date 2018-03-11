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
               first='MainAgentTop', second='MainAgentBottom'):
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

        self.target = (x, y)

        self.goToCenter(gameState)

    def chooseAction(self, gameState):
        """
        Picks among the actions with the highest Q(s,a).
        """
        evaluateType = 'offense'

        if not self.reachedTarget:
            evaluateType = 'start'

        agentCurrentPosition = self.getCurrentAgentPosition(gameState)

        if agentCurrentPosition == self.target and not self.reachedTarget:
            evaluateType = 'offense'
            self.reachedTarget = True

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
        pos = successor.getAgentState(self.index).getPosition()

        if pos != nearestPoint(pos):
            # Only half a grid position was covered
            return successor.generateSuccessor(self.index, action)
        else:
            return successor

    def evaluate(self, gameState, action, mode='offense'):
        """
        Computes a linear combination of features and feature weights
        """
        global features
        weights = self.getWeights()

        if mode == 'offense':
            features = self.featuresForAttack(gameState, action)

        elif mode == 'defense':
            features = self.featuresForDefense(gameState, action)

        elif mode == 'start':
            features = self.featuresForGoingToCenter(gameState, action)

        return sum(features[key] * weights.get(key, 0) for key in features)

    def featuresForDefense(self, gameState, action):
        defenseFeatures = util.Counter()
        successor = self.getSuccessor(gameState, action)

        enemies = [successor.getAgentState(opponent) for opponent in self.getOpponents(successor)]
        invaders = [enemy for enemy in enemies if enemy.isPacman and enemy.getPosition() is not None]
        defenseFeatures['numInvaders'] = len(invaders)

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

        rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]

        if action == rev:
            defenseFeatures['reverse'] = 1

        return defenseFeatures

    def featuresForAttack(self, gameState, action):
        offenseFeatures = util.Counter()
        successor = self.getSuccessor(gameState, action)
        offenseFeatures['successorScore'] = self.getScore(successor)

        offenseFeatures['distanceToFood'] = self.getDistanceToClosestFood(successor)

        closestCapsuleDistance = self.getDistanceToClosestCapsule(gameState, successor)

        if closestCapsuleDistance == 0:
            closestCapsuleDistance = 0.1

        if closestCapsuleDistance is not None:
            offenseFeatures['distanceToCapsule'] = 1.0 / closestCapsuleDistance

        if not self.isAtHome(successor):
            distanceToAgent = self.getDistanceToTeammate(successor)

            if distanceToAgent is not None:
                offenseFeatures['distanceToOther'] = 1.0 / distanceToAgent

        enemyIndex, enemyDistance = self.getIndexAndDistanceToDetectedEnemy(successor)
        closestCapsuleDistance = self.getDistanceToClosestCapsule(gameState, successor)

        if enemyDistance is not None:
            if enemyDistance <= 4:
                self.threatened = True

                if gameState.getAgentState(enemyIndex).scaredTimer > 1:
                    offenseFeatures['distanceToOpponent'] = 0

                else:
                    if closestCapsuleDistance is not None:
                        offenseFeatures['distanceToCapsuleThreatened'] = closestCapsuleDistance

                    offenseFeatures['distanceToOpponent'] = 1.0 / enemyDistance

                    if self.isAtHome(successor) and self.getCurrentAgentScaredTime(successor) <= 1:
                        offenseFeatures['atHomeThreatened'] = 1

                    if enemyDistance <= 1:
                        offenseFeatures['suicide'] = 1

        if enemyDistance is None or enemyDistance > 4:
            self.threatened = False

        if self.otherAgent.threatened and closestCapsuleDistance is not None and closestCapsuleDistance <= 5:
            offenseFeatures['distanceToCapsuleThreatened'] = closestCapsuleDistance

        # Actions to avoid
        if action == Directions.STOP:
            offenseFeatures['stop'] = 1

        return offenseFeatures

    def featuresForGoingToCenter(self, gameState, action):
        startFeatures = util.Counter()
        successor = self.getSuccessor(gameState, action)

        currentAgentPosition = self.getCurrentAgentPosition(successor)

        distanceToCenter = self.getMazeDistance(currentAgentPosition, self.target)
        startFeatures['distanceToTarget'] = distanceToCenter

        if currentAgentPosition == self.target:
            startFeatures['atTarget'] = 1

        return startFeatures

    def getWeights(self):
        return {'numInvaders': -1000, 'invaderDistance': -10, 'stop': -100, 'reverse': -2, 'suicide': -5000,
                'successorScore': 200, 'distanceToFood': -5, 'distanceToOther': -40, 'distanceToOpponent': -225,
                'distanceToCapsule': 45, 'distanceToCapsuleThreatened': -230, 'atHomeThreatened': 400,
                'distanceToTarget': -10, 'atTarget': 100}

    # Utility methods
    def setOtherAgent(self, other):
        self.otherAgent = other

    def setThreatened(self, val):
        self.threatened = val

    def setNorthBias(self, val):
        self.northBias = val

    def getCurrentAgentPosition(self, gameState):
        return gameState.getAgentState(self.index).getPosition()

    def isAtHome(self, gameState):
        return not gameState.getAgentState(self.index).isPacman

    def getOpponentPositions(self, gameState):
        # might want to implement inference to store the most likely position
        # if the enemy position can't be detected (is None)
        opponentPositions = []

        for opponentIndex in self.getOpponents(gameState):
            pos = gameState.getAgentPosition(opponentIndex)

            if pos is not None:
                opponentPositions.append((opponentIndex, pos))

        return opponentPositions

    def getDistanceToTeammate(self, gameState):
        distanceToAgent = None

        if self.index != self.agentsOnTeam[0]:
            otherAgentIndex = self.agentsOnTeam[0]
            myPos = self.getCurrentAgentPosition(gameState)
            otherPos = gameState.getAgentState(otherAgentIndex).getPosition()
            distanceToAgent = self.getMazeDistance(myPos, otherPos)

            if distanceToAgent == 0:
                distanceToAgent = 0.5

        return distanceToAgent

    def getDistanceToClosestFood(self, gameState):
        myPos = self.getCurrentAgentPosition(gameState)
        foodList = self.getFood(gameState).asList()

        if len(foodList) > 0:
            return min([self.getMazeDistance(myPos, food) for food in foodList])

        else:
            return None

    # Compute the index of, and distance to, closest enemy (if detected)
    def getIndexAndDistanceToDetectedEnemy(self, gameState):
        enemyIndex = None
        distToEnemy = None
        opponentPositions = self.getOpponentPositions(gameState)

        if opponentPositions:
            min_dist = 10000
            min_index = None
            myPos = self.getCurrentAgentPosition(gameState)

            for index, pos in opponentPositions:
                dist = self.getMazeDistance(myPos, pos)

                if dist < min_dist:
                    min_dist = dist
                    min_index = index

                    if min_dist == 0:
                        min_dist = 0.5

            enemyIndex = min_index
            distToEnemy = min_dist

        return enemyIndex, distToEnemy

    def getDistanceToClosestCapsule(self, gameState, successor):
        myPos = self.getCurrentAgentPosition(successor)
        oldCapsuleList = self.getCapsules(gameState)
        capsuleList = self.getCapsules(successor)

        minDistance = None

        if len(capsuleList) < len(oldCapsuleList):
            minDistance = 0

        elif len(capsuleList) > 0:
            minDistance = min([self.getMazeDistance(myPos, capsule) for capsule in capsuleList])

        return minDistance

    def getCurrentAgentScaredTime(self, gameState):
        return gameState.getAgentState(self.index).scaredTimer

    def goToCenter(self, gameState):
        self.reachedTarget = False

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

        self.target = sorted(locations, key=lambda location: self.getMazeDistance(
            self.getCurrentAgentPosition(gameState), location))[0]
