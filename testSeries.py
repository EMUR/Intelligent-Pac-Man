#!/usr/bin/python
import subprocess

number_of_games = 100
total_score = 0
games_won = 0
games_lost = 0
games_tied = 0

best_win = 0
worst_loss = 0

print_interval = 10
counter = 0

for _ in range(number_of_games):
    p = subprocess.check_output(['python', 'capture.py', '-r', 'myTeam', '-b', 'baselineTeam', '-Q'])

    if counter % print_interval is 0:
        print('Game {}'.format(counter))

    counter += 1

    for line in p.split('\n'):
        if 'Average Score' in line:
            # print(line)
            score = float(line.split(':')[1].strip())
            if score > 0.0:
                games_won += 1
                if score > best_win:
                    best_win = score
            elif score < 0.0:
                games_lost += 1
                if score < worst_loss:
                    worst_loss = score
            else:
                games_tied += 1
            total_score += score

print('Average score after {} games: {}'.format(number_of_games, total_score / number_of_games))
print('Won: {}, lost: {}, tied: {}'.format(games_won, games_lost, games_tied))
print('Loss rate: {}%. Worst loss: {}. Best win: {}'.format(games_lost / float(number_of_games) * 100, worst_loss, best_win))
