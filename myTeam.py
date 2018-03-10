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
    # The following line is an example only; feel free to change it.
    return [eval(first)(firstIndex), eval(second)(secondIndex)]


##########
# Agents #
##########

class MainAgent(CaptureAgent):
    # noinspection PyUnusedLocal
    def __init__(self, index, timeForComputing=.1):
        CaptureAgent.__init__(self, index, timeForComputing=.1)
        self.isAtCenter = False
        self.mazeCenter = None
        self.initialPosition = None
        self.indices = None

        if index is 0 or index is 1:
            self.northBias = True
        else:
            self.northBias = False

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

        if self.red:
            self.indices = tuple(gameState.getRedTeamIndices())
        else:
            self.indices = tuple(gameState.getBlueTeamIndices())

        if self.initialPosition is None:
            self.initialPosition = gameState.getAgentState(self.indices[1]).getPosition()

        # At the start of the game, or when respawned, agents try to reach the middle
        self.goToCenter(gameState)

    def chooseAction(self, gameState):
        """
        Picks among the actions with the highest Q(s,a).
        """
        agentCurrentPosition = gameState.getAgentPosition(self.index)
        evaluateType = 'attack'

        if not self.isAtCenter:
            evaluateType = 'center'

        if agentCurrentPosition == self.mazeCenter and not self.isAtCenter:
            self.isAtCenter = True
            evaluateType = 'attack'

        # Consider enemy positions
        enemyPositions = self.getVisibleEnemiesPositions(gameState)
        enemySafeDistance = 6

        if enemyPositions:
            for enemyIndex, enemyPosition in enemyPositions:
                if self.getMazeDistance(agentCurrentPosition, enemyPosition) < enemySafeDistance and not self.isPacman(
                        gameState):
                    evaluateType = 'defend'
                    break

        actions = gameState.getLegalActions(self.index)
        values = [self.evaluate(gameState, action, evaluateType) for action in actions]

        maxValue = max(values)
        bestActions = [action for action, value in zip(actions, values) if value is maxValue]

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

    def evaluate(self, gameState, action, evaluateType):
        """
        Computes a linear combination of features and feature weights
        """
        global features
        weights = self.getWeights()

        if evaluateType == 'attack':
            features = self.featuresForAttack(gameState, action)

        elif evaluateType == 'defend':
            features = self.featuresForDefense(gameState, action)

        elif evaluateType == 'center':
            features = self.featuresForGoingToCenter(gameState, action)

        return sum(features[key] * weights.get(key, 0) for key in features)

    def featuresForAttack(self, gameState, action):
        attackFeatures = util.Counter()
        successor = self.getSuccessor(gameState, action)

        agentCurrentState = successor.getAgentState(self.index)
        agentCurrentPosition = agentCurrentState.getPosition()

        # Compute distance to the nearest food
        minDistance = min([self.getMazeDistance(agentCurrentPosition, food)
                           for food in self.getFood(successor).asList()])
        attackFeatures['distanceToFood'] = minDistance

        # TODO: Compute distance to other agent on team to maximize distance if in enemy territory

        # Compute distance to enemy
        closestEnemyDistance = self.getClosestEnemyDistance(successor)
        minimumEnemyDistance = 4

        if closestEnemyDistance <= minimumEnemyDistance:
            attackFeatures['danger'] = 1

        # Compute distance to capsule
        capsules = self.getCapsules(successor)

        try:
            closestCapsuleDistance = min([self.getMazeDistance(agentCurrentPosition, capsule) for capsule in capsules])
        except ValueError:
            closestCapsuleDistance = .1

        attackFeatures['capsuleDistance'] = 1.0 / closestCapsuleDistance

        # Get distance to closest scared enemy
        closestEnemyDistance = self.getClosestScaredEnemyDistance(gameState)

        if closestEnemyDistance is not None and closestEnemyDistance < 3:
            attackFeatures['scaredNearbyEnemy'] = 1

        # Check if state is a dead end
        if self.isDeadEnd(successor):
            x, y = successor.getAgentState(self.index).getPosition()

            if successor.getAgentState(self.index).isPacman:
                if not gameState.hasFood(int(x), int(y)) and (x, y) != self.initialPosition:
                    attackFeatures['cornerTrap'] = 1

        attackFeatures['successorScore'] = self.getScore(successor)

        return attackFeatures

    def featuresForDefense(self, gameState, action):
        defendingFeatures = util.Counter()
        successor = self.getSuccessor(gameState, action)

        agentCurrentState = successor.getAgentState(self.index)
        agentCurrentPosition = agentCurrentState.getPosition()

        # Find number of invaders
        enemies = [successor.getAgentState(opponent) for opponent in self.getOpponents(successor)]
        invaders = list(
            filter(lambda thisInvader: thisInvader.isPacman and thisInvader.getPosition() is not None, enemies))
        defendingFeatures['numberOfInvaders'] = len(invaders)

        # Find distance to closest invader
        if invaders:
            defendingFeatures['invaderDistance'] = min(
                [self.getMazeDistance(agentCurrentPosition, invader.getPosition()) for invader in invaders])

        # TODO: if you are a scared ghost, don't go after enemy Pacman

        return defendingFeatures

    def featuresForGoingToCenter(self, gameState, action):
        startFeatures = util.Counter()
        successor = self.getSuccessor(gameState, action)

        agentCurrentState = successor.getAgentState(self.index)
        agentCurrentPosition = agentCurrentState.getPosition()

        startFeatures['distanceToCenter'] = self.getMazeDistance(agentCurrentPosition, self.mazeCenter)

        if agentCurrentPosition == self.mazeCenter:
            startFeatures['atCenter'] = 1

        return startFeatures

    def getWeights(self):
        return {'numberOfInvaders': -1000, 'invaderDistance': -50, 'cornerTrap': -50, 'successorScore': 100,
                'danger': -400, 'distanceToFood': -1, 'capsuleDistance': 3, 'scaredNearbyEnemy': 100,
                'distanceToCenter': -1, 'atCenter': 1000}

    def isDeadEnd(self, gameState):
        actions = gameState.getLegalActions(self.index)
        result = len(actions) <= 2
        return result

    def goToCenter(self, gameState):
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

        self.mazeCenter = sorted(locations, key=lambda location: self.getMazeDistance(
            gameState.getAgentState(self.index).getPosition(), location))[0]

    def getVisibleEnemiesPositions(self, gameState):
        enemiesAndPositions = [(enemy, gameState.getAgentPosition(enemy)) for enemy in self.getOpponents(gameState)]
        return [element for element in enemiesAndPositions if None not in element]

    def getClosestEnemyDistance(self, gameState):
        try:
            filteredEnemiesAndPositions = list(filter(lambda element:
                                                      gameState.getAgentState(element[0]).scaredTimer is 0
                                                      and not gameState.getAgentState(element[0]).isPacman,
                                                      self.getVisibleEnemiesPositions(gameState)))

            return min([self.getMazeDistance(gameState.getAgentPosition(self.index), position)
                        for (index, position) in filteredEnemiesAndPositions])
        except ValueError:
            return None

    def getClosestScaredEnemyDistance(self, gameState):
        try:
            filteredEnemiesAndPositions = list(filter(lambda element:
                                                      gameState.getAgentState(element[0]).scaredTimer > 0
                                                      and not gameState.getAgentState(element[0]).isPacman,
                                                      self.getVisibleEnemiesPositions(gameState)))

            return min([self.getMazeDistance(gameState.getAgentPosition(self.index), position)
                        for (index, position) in filteredEnemiesAndPositions])
        except ValueError:
            return None

    def isPacman(self, gameState):
        return gameState.getAgentState(self.index).isPacman
