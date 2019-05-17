import os
import csv
import chess
#gamename


def create_path(path):
    if not os.path.exists(path):
        os.mkdir(path)


def open_pgn(filename):
    create_path('pgn')
    return open('pgn' + '/' + filename + '.pgn')


# write analysis to a csv file
def write_dict_to_csv(filename, content):
    create_path('output' + '/' + filename)
    with open('output' + '/' + filename + '/' + filename + '.csv', 'w', newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=';')
        writer.writerow(content.keys())
        writer.writerows(zip(*content.values()))


def export_board_svg(board, game_name, filename):
    create_path('output' + '/' + game_name + '/' + 'images')
    file = open('output' + '/' + game_name + '/' + 'images' + '/' + str(filename) + '.svg', 'w')
    file.write(chess.svg.board(board=board, size=400))
    file.close()


def init_folder_structure(filename):
    create_path('output')
    create_path('output' + '/' + filename)
    create_path('output' + '/' + filename + '/' + 'images')
