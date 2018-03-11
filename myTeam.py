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
    # The following line is an example only; feel free to change it.

    agent1 = eval(first)(firstIndex)
    agent2 = eval(second)(secondIndex)

    agent1.setOtherAgent(agent2)
    agent2.setOtherAgent(agent1)

    agent1.setThreatened(False)
    agent2.setThreatened(False)

    return [agent1, agent2]


##########
# Agents #
##########

class MainAgent(CaptureAgent):
    # noinspection PyUnusedLocal
    def __init__(self, index, timeForComputing=.1):
        CaptureAgent.__init__(self, index, timeForComputing=.1)
        self.otherAgent = None
        self.reachedCenter = False
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
            self.agentsOnTeam = gameState.getRedTeamIndices()

        else:
            self.agentsOnTeam = gameState.getBlueTeamIndices()

        self.goToCenter(gameState)

    def chooseAction(self, gameState):
        """
        Picks among the actions with the highest Q(s,a).
        """
        # agentCurrentPosition = gameState.getAgentPosition(self.index)
        # evaluateType = 'attack'
        #
        # if agentCurrentPosition == self.initialPosition:
        #     self.reachedCenter = False
        #
        # if not self.reachedCenter:
        #     evaluateType = 'center'
        #
        # if agentCurrentPosition == self.mazeCenter and not self.reachedCenter:
        #     self.reachedCenter = True
        #     evaluateType = 'attack'
        #
        # # Consider the number fo enemies in your territory and number of Pacmen
        # numberOfPacmen = len(list(
        #     filter(lambda agent: agent.isPacman, [gameState.getAgentState(index) for index in self.indices])))
        #
        # thisAgentDistance = self.getMazeDistance(gameState.getAgentPosition(self.index), self.mazeCenter)
        #
        # # If more than one member of the team is a pacman and the enemy has pacmen, switch the closest team member
        # # from attacking to defending
        # if numberOfPacmen > 1 and self.getNumberOfEnemyPacman(gameState):
        #     for index in self.indices:
        #         if index is not self.index:
        #             distanceOther = self.getMazeDistance(gameState.getAgentPosition(index), self.mazeCenter)
        #
        #             if thisAgentDistance < distanceOther:
        #                 evaluateType = 'defend'
        #                 # reason = 'Agent {} defends because of # of pacmen'.format(self.index)
        #
        # # Consider enemy positions
        # enemyPositions = self.getVisibleEnemiesPositions(gameState)
        # enemySafeDistance = 6
        #
        # if enemyPositions:
        #     for enemyIndex, enemyPosition in enemyPositions:
        #         if self.getMazeDistance(agentCurrentPosition,
        #                                 enemyPosition) < enemySafeDistance and not self.isPacman(gameState):
        #             evaluateType = 'defend'
        #             break
        #
        # numberOfPacmans = 0
        #
        # for index in self.indices:
        #     agentState = gameState.getAgentState(index)
        #
        #     if agentState.isPacman:
        #         numberOfPacmans += 1
        #
        # if numberOfPacmans > 1 and self.getNumberOfEnemyPacman(gameState):
        #     for index in self.indices:
        #         if index is not self.index:
        #             distanceOther = self.getMazeDistance(gameState.getAgentPosition(index), self.mazeCenter)
        #             distanceThis = self.getMazeDistance(gameState.getAgentPosition(self.index), self.mazeCenter)
        #
        #             if distanceThis < distanceOther:
        #                 evaluateType = 'defend'
        #
        # actions = gameState.getLegalActions(self.index)
        # values = [self.evaluate(gameState, action, evaluateType) for action in actions]
        #
        # maxValue = max(values)
        # bestActions = [action for action, value in zip(actions, values) if value is maxValue]
        #
        # if self.previousRole is None:
        #     self.previousRole = self.currentRole
        #
        # self.previousRole = self.currentRole
        # self.currentRole = evaluateType
        #
        # # Ignore role changing rules if agent is trying to reach the center
        # if self.currentRole != 'center':
        #     if self.previousRole != self.currentRole:
        #         if self.lastRoleChange < 1:
        #             # print('\tRole change not allowed, last role change: {}'.format(self.lastRoleChange))
        #             self.currentRole = self.previousRole
        #
        #         else:
        #             # print('New role for agent {}: {}'.format(self.index, self.currentRole))
        #             self.lastRoleChange = 0
        #
        # self.lastRoleChange += 1
        #
        # return random.choice(bestActions)

        evaluateType = 'offense'

        currentAgentPosition = self.getCurrentAgentPosition(gameState)
        opponentPositions = self.getOpponentPositions(gameState)

        if opponentPositions:
            for index, pos in opponentPositions:
                if self.getMazeDistance(currentAgentPosition, pos) < 6 and self.isAtHome(gameState):
                    evaluateType = 'defense'
                    break

        actions = gameState.getLegalActions(self.index)
        values = [self.evaluate(gameState, action, evaluateType) for action in actions]

        maxValue = max(values)
        bestActions = [action for action, value in zip(actions, values) if value == maxValue]

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

        if evaluateType == 'offense':
            features = self.featuresForAttack(gameState, action)

        elif evaluateType == 'defense':
            features = self.featuresForDefense(gameState, action)

        elif evaluateType == 'start':
            features = self.featuresForGoingToCenter(gameState, action)

        return sum(features[key] * weights.get(key, 0) for key in features)

    def featuresForAttack(self, gameState, action):
        # attackFeatures = util.Counter()
        # successor = self.getSuccessor(gameState, action)
        #
        # agentCurrentState = successor.getAgentState(self.index)
        # agentCurrentPosition = agentCurrentState.getPosition()
        #
        # # Compute distance to the nearest food
        # minDistance = min([self.getMazeDistance(agentCurrentPosition, food)
        #                    for food in self.getFood(successor).asList()])
        # attackFeatures['distanceToFood'] = minDistance
        #
        # # Compute distance to enemy
        # closestEnemyDistance = self.getClosestEnemyDistance(successor)
        # minimumEnemyDistance = 2
        #
        # if closestEnemyDistance <= minimumEnemyDistance:
        #     attackFeatures['danger'] = 1
        #
        # # Compute distance to capsule
        # capsules = self.getCapsules(successor)
        #
        # try:
        #     closestCapsuleDistance = min([self.getMazeDistance(agentCurrentPosition, capsule) for capsule in capsules])
        # except ValueError:
        #     closestCapsuleDistance = .1
        #
        # attackFeatures['capsuleDistance'] = 1.0 / closestCapsuleDistance
        #
        # # Get distance to closest scared enemy
        # closestEnemyDistance = self.getClosestScaredEnemyDistance(successor)
        #
        # if closestEnemyDistance is not None and closestEnemyDistance < 3:
        #     attackFeatures['scaredNearbyEnemy'] = 1
        #
        # # Check if state is a dead end
        # if self.isDeadEnd(successor):
        #     x, y = successor.getAgentState(self.index).getPosition()
        #
        #     if successor.getAgentState(self.index).isPacman:
        #         if not gameState.hasFood(int(x), int(y)) and (x, y) != self.initialPosition:
        #             attackFeatures['cornerTrap'] = 1
        #
        # attackFeatures['successorScore'] = self.getScore(successor)
        #
        # try:
        #     attackFeatures['distanceBetweenMates'] = 1 / self.getDistanceBetweenTeamMates(successor)
        # except ZeroDivisionError:
        #     attackFeatures['distanceBetweenMates'] = 1
        #
        # # Undesirable actions
        # if action == Directions.STOP:
        #     attackFeatures['stop'] = 1
        #
        # reverseAction = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
        #
        # if action == reverseAction:
        #     attackFeatures['reverse'] = 1
        #
        # return attackFeatures

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

    def featuresForDefense(self, gameState, action):
        # defendingFeatures = util.Counter()
        # successor = self.getSuccessor(gameState, action)
        #
        # agentCurrentState = successor.getAgentState(self.index)
        # agentCurrentPosition = agentCurrentState.getPosition()
        #
        # # Find number of invaders
        # enemies = [successor.getAgentState(opponent) for opponent in self.getOpponents(successor)]
        # invaders = list(
        #     filter(lambda thisInvader: thisInvader.isPacman and thisInvader.getPosition() is not None, enemies))
        # defendingFeatures['numberOfInvaders'] = len(invaders)
        #
        # minimumInvaderDistance = 0
        #
        # # Find distance to closest invader
        # if invaders:
        #     minimumInvaderDistance = min([self.getMazeDistance(agentCurrentPosition, invader.getPosition())
        #                                   for invader in invaders])
        #     defendingFeatures['invaderDistance'] = minimumInvaderDistance
        #
        # # If you are a scared ghost, don't go after enemy Pacman
        # agentScaredTimer = agentCurrentState.scaredTimer
        #
        # if agentScaredTimer > 0:
        #     print('Agent scared timer: {}, minimum invader distance: {}'.format(agentScaredTimer, minimumInvaderDistance))
        #
        # if agentScaredTimer and minimumInvaderDistance < 3:
        #     defendingFeatures['teammateIsScaredGhost'] = 1
        #     print('Scared agent')
        #
        # try:
        #     defendingFeatures['distanceBetweenMates'] = 1 / self.getDistanceBetweenTeamMates(successor)
        # except ZeroDivisionError:
        #     defendingFeatures['distanceBetweenMates'] = 1
        #
        # # Undesirable actions
        # if action == Directions.STOP:
        #     defendingFeatures['stop'] = 1
        #
        # reverseAction = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
        #
        # if action == reverseAction:
        #     defendingFeatures['reverse'] = 1
        #
        # return defendingFeatures

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
        # return {'numberOfInvaders': -0.5, 'invaderDistance': -0.025, 'cornerTrap': -0.05, 'successorScore': 0.05,
        #         'danger': -0.2, 'distanceToFood': -0.0005, 'capsuleDistance': 0.025, 'scaredNearbyEnemy': 0.05,
        #         'distanceToCenter': -0.0005, 'atCenter': 0.5, 'stop': -1.0, 'reverse': -0.01,
        #         'teammateIsScaredGhost': -0.2, 'distanceBetweenMates': -0.5}

        return {'numberOfInvaders': -1000, 'invaderDistance': -10, 'stop': -100, 'reverse': -2, 'suicide': -5000,
                'successorScore': 200, 'distanceToFood': -5, 'distanceToOther': -40, 'distanceToOpponent': -225,
                'distanceToCapsule': 45, 'distanceToCapsuleThreatened': -230, 'atHomeThreatened': 400,
                'distanceToCenter': -10, 'atCenter': 100}

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

    def getDistanceBetweenTeamMates(self, gameState):
        return self.getMazeDistance(gameState.getAgentPosition(self.indices[0]),
                                    gameState.getAgentPosition(self.indices[1]))

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

    def getNumberOfEnemyPacman(self, gameState):
        return sum([gameState.getAgentState(enemy).isPacman for enemy in self.getOpponents(gameState)])

    def isPacman(self, gameState):
        return gameState.getAgentState(self.index).isPacman

    def getCurrentAgentPosition(self, gameState):
        return gameState.getAgentState(self.index).getPosition()

    def getOpponentPositions(self, gameState):
        # might want to implement inference to store the most likely position
        # if the enemy position can't be detected (is None)
        opponentPositions = []

        for opponentIndex in self.getOpponents(gameState):
            pos = gameState.getAgentPosition(opponentIndex)

            if pos is not None:
                opponentPositions.append((opponentIndex, pos))

        return opponentPositions

    def isAtHome(self, gameState):
        return not gameState.getAgentState(self.index).isPacman

    def getDistanceToTeammate(self, gameState):
        distanceToAgent = None

        if self.index != self.agentsOnTeam[0]:
            otherAgentIndex = self.agentsOnTeam[0]
            # The below code is indented under 'else'
            # so that only 1 of the agents cares how close it is to the other
            myPos = self.getCurrentAgentPosition(gameState)
            otherPos = gameState.getAgentState(otherAgentIndex).getPosition()
            distanceToAgent = self.getMazeDistance(myPos, otherPos)

            if distanceToAgent == 0:
                distanceToAgent = 0.5

        return distanceToAgent

    def getDistanceToClosestFood(self, gameState):
        myPos = self.getCurrentAgentPosition(gameState)
        foodList = self.getFood(gameState).asList()

        if len(foodList) > 0:  # This should always be True,  but better safe than sorry
            return min([self.getMazeDistance(myPos, food) for food in foodList])

        else:
            # somehow none of the opponent's food is left on the grid
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

    def setOtherAgent(self, other):
        self.otherAgent = other

    def setThreatened(self, val):
        self.threatened = val
