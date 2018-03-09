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

def createTeam(firstIndex, secondIndex, isRed,
               first='TopAgent', second='BottomAgent'):
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
    def __init__(self, index, timeForComputing=.1):
        CaptureAgent.__init__(self, index, timeForComputing=.1)
        self.center = (0, 0)

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
        # Agents try to go to center with top or bottom bias
        self.goToCenter(gameState)

    def chooseAction(self, gameState):
        """
        Picks among the actions with the highest Q(s,a).
        """
        agentCurrentPosition = gameState.getAgentPosition(self.index)
        evaluateType = 'attack'

        # Start at start state, try to get to center then switch to offense
        if not self.atCenter:
            evaluateType = 'start'

        if agentCurrentPosition == self.center and not self.atCenter:
            self.atCenter = True
            evaluateType = 'attack'

        # Consider enemy positions
        enemyPositions = self.getVisibleEnemiesPositions(gameState)
        enemySafeDistance = 6

        if enemyPositions:
            for enemyIndex, enemyPosition in enemyPositions:
                # If we detect an enemy and are on home turf we go after them and defend home
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
        pos = successor.getAgentState(self.index).getPosition()

        if pos != nearestPoint(pos):
            # Only half a grid position was covered
            return successor.generateSuccessor(self.index, action)

        else:
            return successor

    def evaluate(self, gameState, action, evaluateType):
        """
        Computes a linear combination of features and feature weights
        """
        global features, weights

        if evaluateType == 'attack':
            features = self.getFeaturesAttack(gameState, action)
            weights = self.getWeightsAttack(gameState, action)

        elif evaluateType == 'defend':
            features = self.getFeaturesDefend(gameState, action)
            weights = self.getWeightsDefend(gameState, action)

        elif evaluateType == 'start':
            features = self.getFeaturesStart(gameState, action)
            weights = self.getWeightsStart(gameState, action)

        return features * weights

    def getFeaturesAttack(self, gameState, action):
        attackFeatures = util.Counter()
        successor = self.getSuccessor(gameState, action)
        attackFeatures['successorScore'] = self.getScore(successor)

        agentCurrentState = successor.getAgentState(self.index)
        agentCurrentPosition = agentCurrentState.getPosition()

        # Compute distance to the nearest food
        minDistance = min([self.getMazeDistance(agentCurrentPosition, food)
                           for food in self.getFood(successor).asList()])
        attackFeatures['distanceToFood'] = minDistance

        # Compute distance to ally agent (maximize distance between if in enemyTerritory)

        # Compute distance to enemy
        closestEnemyDistance = self.getClosestEnemyDistance(successor)
        minimumEnemyDistance = 4

        if closestEnemyDistance <= minimumEnemyDistance:
            attackFeatures['danger'] = 1
        else:
            attackFeatures['danger'] = 0

            # Compute distance to capsule
        capsules = self.getCapsules(successor)

        try:
            minCapsuleDist = min([self.getMazeDistance(agentCurrentPosition, capsule) for capsule in capsules])
        except ValueError:
            minCapsuleDist = .1

        attackFeatures['capsuleDist'] = 1.0 / minCapsuleDist

        if action == Directions.STOP:
            attackFeatures['stop'] = 1

        rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]

        if action == rev:
            attackFeatures['reverse'] = 1

        return attackFeatures

    def getFeaturesDefend(self, gameState, action):
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

        if action == Directions.STOP:
            defendingFeatures['stop'] = 1

        rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]

        if action == rev:
            defendingFeatures['reverse'] = 1

        return defendingFeatures

    def getFeaturesStart(self, gameState, action):
        startFeatures = util.Counter()
        successor = self.getSuccessor(gameState, action)

        agentCurrentState = successor.getAgentState(self.index)
        agentCurrentPosition = agentCurrentState.getPosition()

        distanceToCenter = self.getMazeDistance(agentCurrentPosition, self.center)
        startFeatures['distanceToCenter'] = distanceToCenter

        if agentCurrentPosition == self.center:
            startFeatures['atCenter'] = 1

        return startFeatures

    def getWeightsAttack(self, gameState, action):
        return {'successorScore': 100, 'danger': -400, 'distanceToFood': -1, 'stop': -2000, 'reverse': -20,
                'capsuleDist': 3}

    def getWeightsDefend(self, gameState, action):
        return {'numberOfInvaders': -1000, 'invaderDistance': -50, 'stop': -2000, 'reverse': -20}

    def getWeightsStart(self, gameState, action):
        return {'distanceToCenter': -1, 'atCenter': 1000}

    # This method is overridden in subclasses
    def goToCenter(self, gameState):
        pass

    def getVisibleEnemiesPositions(self, gameState):
        enemiesAndPositions = [(enemy, gameState.getAgentPosition(enemy)) for enemy in self.getOpponents(gameState)]
        return [element for element in enemiesAndPositions if None not in element]

    def getClosestEnemyDistance(self, gameState):
        try:
            return min([self.getMazeDistance(gameState.getAgentPosition(self.index), position)
                        for (i, position) in self.getVisibleEnemiesPositions(gameState)])
        except ValueError:
            return None

    def isPacman(self, gameState):
        return gameState.getAgentState(self.index).isPacman


class TopAgent(MainAgent):
    def goToCenter(self, gameState):
        locations = []
        self.atCenter = False

        x = gameState.getWalls().width / 2
        y = gameState.getWalls().height / 2

        # 0 to x-1 and x to width
        if self.red:
            x = x - 1

        self.center = (x, y)
        maxHeight = gameState.getWalls().height

        # look for locations to move to that are not walls (favor top positions)
        for i in xrange(maxHeight - y):
            if not gameState.hasWall(x, y):
                locations.append((x, y))

            y = y + 1

        self.center = sorted(locations, key=lambda location: self.getMazeDistance(
            gameState.getAgentState(self.index).getPosition(), location))[0]


class BottomAgent(MainAgent):
    def goToCenter(self, gameState):
        locations = []
        self.atCenter = False

        x = gameState.getWalls().width / 2
        y = gameState.getWalls().height / 2

        # 0 to x-1 and x to width
        if self.red:
            x = x - 1

        self.center = (x, y)

        # look for locations to move to that are not walls (favor bot positions)
        for i in xrange(y):
            if not gameState.hasWall(x, y):
                locations.append((x, y))

            y = y - 1

        self.center = sorted(locations, key=lambda location: self.getMazeDistance(
            gameState.getAgentState(self.index).getPosition(), location))[0]
