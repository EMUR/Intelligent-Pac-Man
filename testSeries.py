#!/usr/bin/python
import subprocess

number_of_games = 100
total_score = 0
games_won = 0
games_lost = 0
games_tied = 0

print_interval = 20
counter = 0

for _ in range(number_of_games):
    p = subprocess.check_output(['python', 'capture.py', '-r', 'myTeam', '-b', 'baselineTeam', '-q'])

    if counter % print_interval is 0:
        print('Game {}'.format(counter))

    counter += 1

    for line in p.split('\n'):
        if 'Average Score' in line:
            # print(line)
            score = float(line.split(':')[1].strip())
            if score > 0.0:
                games_won += 1
            elif score < 0.0:
                games_lost += 1
            else:
                games_tied += 1
            total_score += score

print('Average score after {} games: {}'.format(number_of_games, total_score / number_of_games))
print('Won: {}, lost: {}, tied: {}'.format(games_won, games_lost, games_tied))
