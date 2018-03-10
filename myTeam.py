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
    def __init__(self, index, timeForComputing=.1):
        CaptureAgent.__init__(self, index, timeForComputing=.1)
        self.isAtCenter = False
        self.labyrinthCenter = None
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
        if not self.isAtCenter:
            evaluateType = 'center'

        if agentCurrentPosition == self.labyrinthCenter and not self.isAtCenter:
            self.isAtCenter = True
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
        global features, weights

        if evaluateType == 'attack':
            # print("Attack agent")
            features = self.featuresForAttack(gameState, action)
            weights = self.weightsForAttack(gameState, action)

        elif evaluateType == 'defend':
            # print("Defense agent")
            features = self.featuresForDefense(gameState, action)
            weights = self.weightsForDefense(gameState, action)

        elif evaluateType == 'center':
            # print("Center agent")
            features = self.featuresForGoingToCenter(gameState, action)
            weights = self.weightsForGoingToCenter(gameState, action)

        return features * weights

    def featuresForAttack(self, gameState, action):
        attackFeatures = util.Counter()
        successor = self.getSuccessor(gameState, action)

        attackFeatures['cornerTrap'] = 0

        if self.isDeadEnd(successor):
            x, y = successor.getAgentState(self.index).getPosition()

            if successor.getAgentState(self.index).isPacman:
                if not gameState.hasFood(int(x), int(y)) and (x, y) != self.initialPosition:
                    attackFeatures['cornerTrap'] = 1

        attackFeatures['successorScore'] = self.getScore(successor)

        agentCurrentState = successor.getAgentState(self.index)
        agentCurrentPosition = agentCurrentState.getPosition()

        # Compute distance to the nearest food
        minDistance = min([self.getMazeDistance(agentCurrentPosition, food)
                           for food in self.getFood(successor).asList()])
        attackFeatures['distanceToFood'] = minDistance

        # Get scared enemies
        # enemies = [successor.getAgentState(opponent) for opponent in self.getOpponents(successor)]
        #
        # scaredEnemies = list(filter(lambda thisEnemy: thisEnemy.scaredTimer is not 0
        #                             and not thisEnemy.isPacman, enemies))
        #
        # # TODO: if you are a scared ghost, don't go after enemy PacMan
        #
        # if scaredEnemies:
        #     # sortedScaredEnemies = sorted(scaredEnemies, key=lambda enemy: self.getMazeDistance(
        #     #     agentCurrentPosition, enemy.configuration.pos))
        #     attackFeatures['scaredNearbyEnemy'] = 1
        #
        # else:
        #     attackFeatures['scaredNearbyEnemy'] = 0

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

        # Undesirable actions
        if action == Directions.STOP:
            attackFeatures['stop'] = 1

        rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]

        if action == rev:
            attackFeatures['reverse'] = 1

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

        # Undesirable actions
        if action == Directions.STOP:
            defendingFeatures['stop'] = 1

        rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]

        if action == rev:
            defendingFeatures['reverse'] = 1

        return defendingFeatures

    def featuresForGoingToCenter(self, gameState, action):
        startFeatures = util.Counter()
        successor = self.getSuccessor(gameState, action)

        agentCurrentState = successor.getAgentState(self.index)
        agentCurrentPosition = agentCurrentState.getPosition()

        distanceToCenter = self.getMazeDistance(agentCurrentPosition, self.labyrinthCenter)
        startFeatures['distanceToCenter'] = distanceToCenter

        if agentCurrentPosition == self.labyrinthCenter:
            startFeatures['atCenter'] = 1

        return startFeatures

    def weightsForAttack(self, gameState, action):
        return {'successorScore': 100, 'danger': -400, 'distanceToFood': -1, 'stop': -2000, 'reverse': -20,
                'capsuleDist': 3, 'scaredNearbyEnemy': 50, 'cornerTrap': -50}

    def weightsForDefense(self, gameState, action):
        return {'numberOfInvaders': -1000, 'invaderDistance': -50, 'stop': -2000, 'reverse': -20}

    def weightsForGoingToCenter(self, gameState, action):
        return {'distanceToCenter': -1, 'atCenter': 1000}

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

        self.labyrinthCenter = sorted(locations, key=lambda location: self.getMazeDistance(
            gameState.getAgentState(self.index).getPosition(), location))[0]

    def getVisibleEnemiesPositions(self, gameState):
        enemiesAndPositions = [(enemy, gameState.getAgentPosition(enemy)) for enemy in self.getOpponents(gameState)]
        return [element for element in enemiesAndPositions if None not in element]

    def getClosestEnemyDistance(self, gameState):
        try:
            return min([self.getMazeDistance(gameState.getAgentPosition(self.index), position)
                        for (index, position) in self.getVisibleEnemiesPositions(gameState)])
        except ValueError:
            return None

    def isPacman(self, gameState):
        return gameState.getAgentState(self.index).isPacman
