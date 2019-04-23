import chess
import chess.svg
import chess.pgn
import chess.engine
from chess.engine import Info
from IPython.display import SVG
import copy

import numpy as np
import chess_io

# use plotly to visualize the chess game in a line graph
import plotly
# import plotly.plotly as py
import plotly.graph_objs as go
import plotly.io as pio


# Convert the board from the FEN notation to an 3 dimensional array for easier evaluation
def fen_to_tensor(input_str):
    pieces_str = "PNBRQK"
    pieces_str += pieces_str.lower()
    pieces = set(pieces_str)
    valid_spaces = set(range(1, 9))
    pieces_dict = {pieces_str[0]: 1, pieces_str[1]: 2, pieces_str[2]: 3, pieces_str[3]: 4,
                   pieces_str[4]: 5, pieces_str[5]: 6,
                   pieces_str[6]: -1, pieces_str[7]: -2, pieces_str[8]: -3, pieces_str[9]: -4,
                   pieces_str[10]: -5, pieces_str[11]: -6}

    # 1st dimension are rows/ranks, 2nd dimension are columns/files, 3rd dimension are the different piece types
    # the values are either -1, 0 or 1
    boardtensor = np.zeros((8, 8, 6))

    inputliste = input_str.split()
    rownr = 0
    colnr = 0
    for i, c in enumerate(inputliste[0]):
        if c in pieces:
            boardtensor[rownr, colnr, np.abs(pieces_dict[c]) - 1] = np.sign(pieces_dict[c])
            colnr = colnr + 1
        elif c == '/':  # new row
            rownr = rownr + 1
            colnr = 0
        elif int(c) in valid_spaces:
            colnr = colnr + int(c)
        else:
            raise ValueError("invalid fenstr at index: {} char: {}".format(i, c))

    return boardtensor


def count_pieces(fen):
    boardtensor = fen_to_tensor(fen)
    count = np.sum(np.abs(boardtensor))
    return count


def pawn_ending(fen):
    boardtensor = fen_to_tensor(fen)
    counts = np.sum(np.abs(boardtensor), axis=(0, 1))
    if counts[1] == 0 and counts[2] == 0 and counts[3] == 0 and counts[4] == 0:
        return True
    else:
        return False


def rook_ending(fen):
    boardtensor = fen_to_tensor(fen)
    counts = np.sum(np.abs(boardtensor), axis=(0, 1))
    if counts[1] == 0 and counts[2] == 0 and counts[4] == 0 and counts[3] > 0:
        return True
    else:
        return False


# Determines how many pieces of the current player are being threatend by the opponent
def compute_attackers(board):
    pieces = board.piece_map()

    attacked_pieces = list()
    for square, piece in pieces.items():
        attackers = [i for i in board.attackers(not piece.color, square) if
                     i > 0 and board.piece_at(i).color != board.turn]
        attacker_types = [board.piece_at(i).symbol() for i in attackers]

        for a in attackers:
            # attacked_pieces.append([chess.SQUARE_NAMES[a], pieces[a].symbol(), chess.SQUARE_NAMES[square], piece.symbol()])
            attacked_pieces.append(chess.Move(a, square))

    return attacked_pieces


# Calculates the score for a move
def compute_score(engine, board):
    # Start a search.
    # engine.position(board)
    # engine.go(movetime=100)
    #play = engine.play(board=board, limit=chess.engine.Limit(time=0.100), info=Info.ALL)
    #print(play)
    #print(board.san(play.move))
    #print(board.san(play.ponder))
    info = engine.analyse(board, chess.engine.Limit(time=1.000))
    score = 0
    if board.turn == chess.WHITE:
        score = info.get("score").white().score()
    else:
        score = info["score"].white().score()
    # print("Score: ", score)
    return score


def compute_score_alternative(engine, board):
    play = engine.play(board=board, limit=chess.engine.Limit(time=1.000), info=Info.ALL)
    #print(play)
    #print("a best move: ", board.san(play.move))


    return play.info.get('score').white().score(), play.move


def compute_best_move_alternative(engine, board, move):
    #print("board:", board)


    #print("movemove: ", board.san(move), move)
    board.push(move)
    #print("board:", board)
    info = engine.analyse(board=board, limit=chess.engine.Limit(time=1.000), info=Info.ALL)
    board.pop()
    print('alt_best_move: ', board.san(move), ' alt_best_score: ', info.get('score').white().score())

    #print('yolo')
    #print(info)
    return info.get('score').white().score()


# Calculates the scores for all possible moves in the current turn and returns a list
def compute_best_move(engine, board):
    movescores = list()

    for mov in board.legal_moves:
        board.push(mov)
        #engine.position(board)
        #engine.go(movetime=100)
        info = engine.analyse(board, chess.engine.Limit(time=1.000))
        score = info.get("score").white().score()
        if board.turn == chess.WHITE:
            if score is not None:
                movescores.append(tuple((score, mov)))
        elif board.turn == chess.BLACK:
            if score is not None:
                movescores.append(tuple((score, mov)))
        board.pop()

    return movescores


# Categorizes a move being a blunder(4), mistake(3), inaccuracy(2), neutral move(1) or good move(0)
def categorize_best_move_score_diff(best_move_score_diff, best_move, actual_move):
    category = 1

    if best_move_score_diff >= 200:
        category = 4
    elif best_move_score_diff >= 90:
        category = 3
    elif best_move_score_diff >= 40:
        category = 2
    elif best_move == actual_move:
        category = 0

    return category


def compute_guarded_pieces(board):
    c_board = copy.deepcopy(board)

    # loop over one colors pieces
    pieces = c_board.piece_map()
    # print("Pieces")
    # print(pieces)
    bait_piece = chess.Piece(chess.QUEEN, not c_board.turn)
    count = 0
    guarded_pieces = list()
    for square, piece in pieces.items():
        if piece.color == c_board.turn:
            p = c_board.remove_piece_at(square);
            c_board.set_piece_at(square, bait_piece)

            for mov in c_board.legal_moves:
                if mov.to_square == square and c_board.is_capture(mov):
                    # guarded_pieces.append([chess.SQUARE_NAMES[mov.from_square], pieces[mov.from_square].symbol(), chess.SQUARE_NAMES[square], piece.symbol()])
                    guarded_pieces.append(mov)
            c_board.remove_piece_at(square)
            c_board.set_piece_at(square, p)

        # remove_piece_at()
        # loop over legal_moves
        # count moves to removed piece position

    return guarded_pieces


def compute_threatened_guarded_pieces(threatened_pieces, guarded_pieces):
    threatened_guarded_pieces = dict({
        'square': [],
        'threatening_move': [],
        'guarding_move': [],
        'threats_square': [],
        'guards_square': []
    })
    for threatening_move in threatened_pieces:
        for guarding_move in guarded_pieces:
            if threatening_move.to_square == guarding_move.to_square:
                if threatening_move.to_square not in threatened_guarded_pieces.get('square'):
                    threatened_guarded_pieces.get('square').append(guarding_move.to_square)
                    threatened_guarded_pieces.get('threatening_move').append(threatening_move)
                    threatened_guarded_pieces.get('guarding_move').append(guarding_move)
                else:
                    if threatening_move is threatened_guarded_pieces.get('threatening_move'):
                        threatened_guarded_pieces.get('threatening_move').append(threatening_move)
                    if guarding_move is threatened_guarded_pieces.get('guarding_move'):
                        threatened_guarded_pieces.get('guarding_move').append(guarding_move)

    return threatened_guarded_pieces


# Connect program with the chess engine Stockfish via UCI
def connect_to_stockfish():
    return chess.engine.SimpleEngine.popen_uci("engine/stockfish_10_x64.exe")


def plot_graph(act_game, filename, counts):
    # plotly.tools.set_credentials_file(username='s1710629025', api_key='••••••••••')
    plotly.offline.init_notebook_mode(connected=True)

    check_color = ['red' if i else 'white' for i in counts["is_check"]]
    check_no = [i for (i, s) in enumerate(counts["is_check"]) if s]
    bubble = [s / 2 for s in counts["move_count"]]
    # best = [np.log(s+1) for s in counts["bestdiff"]]
    # best = [s for s in counts["bestdiff"]]
    best = counts["best_move_score_diff_category"]

    rook_color = ['blue' if i else 'white' for i in counts["rookending"]]
    pawn_color = ['green' if i else 'white' for i in counts["pawnending"]]
    capture_color = ['yellow' if i else 'white' for i in counts["is_capture"]]
    capture_no = [i for (i, s) in enumerate(counts["is_capture"]) if s]

    shapes = []
    lists = [check_color, capture_color, rook_color, pawn_color]
    for (i, list) in enumerate(lists):
        shapes = shapes + [
            dict(
                type='rect',
                # x-reference is assigned to the x-values
                xref='x',
                # y-reference is assigned to the plot paper [0,1]
                yref='paper',
                x0=i,
                y0=0,
                x1=i + 1,
                y1=1,
                fillcolor=s,
                opacity=0.2,
                line=dict(
                    width=0,
                )
            )
            for (i, s) in enumerate(list)]

    annotations = [dict(
        xref='x',
        yref='paper',
        x=s,
        y=(0.05 + i * 0.2) % 1,
        text='Check!',
        opacity=0.8,
        xanchor='left',
        showarrow=False,
        ax=20,
        ay=-30,
        font=dict(
            family='Courier New, monospace',
            size=16,
            color='red'
        ),
    )
        for (i, s) in enumerate(check_no)]

    trace1 = go.Scatter(
        mode='markers+lines',
        y=counts["score"],
        # y = score_history,
        name='Scores',

        line=dict(
            color=('black'),
            width=4,
        ),
        marker=dict(
            size=bubble,
            line=dict(color='rgb(231, 99, 250)', width=1),
            cmax=max(best),
            cmin=min(best),
            color=best,
            colorbar=dict(title='Mistakes'),
            colorscale='Jet'
        )
    )

    data = [trace1]

    layout = dict(title=act_game.headers["Event"] + " / " + act_game.headers["White"] + " - "
                        + act_game.headers["Black"] + "  " + act_game.headers["Result"] + " / "
                        + act_game.headers["Date"],
                  xaxis=dict(title='Move'),
                  yaxis=dict(title='Score'),
                  shapes=shapes,
                  annotations=annotations
                  )

    fig = {
        'data': data,
        'layout': layout,
    }

    # plot chart in notebook as well as write it to html file
    plotly.offline.iplot(fig)
    plotly.offline.plot(fig, filename='output/' + filename + '/' + filename + '.html')


def main():

    engine = connect_to_stockfish()


    # Open PGN file
    filename = "kasparov_karpov_1986"
    chess_io.init_folder_structure(filename)
    # filename = "kramnik_leko_2001"
    # filename = "lcc2017"
    pgn = chess_io.open_pgn(filename)

    # for i in range(35):
    #    act_game = chess.pgn.read_game(pgn)

    act_game = chess.pgn.read_game(pgn)

    print(act_game.headers["Event"] + " / " + act_game.headers["White"] +
          " - " + act_game.headers["Black"] + "  " + act_game.headers["Result"] +
          " / " + act_game.headers["Date"])

    # Register a standard info handler.
    # info_handler = chess.uci.InfoHandler()
    # engine.info_handlers.append(info_handler)

    counts = {
        "fullmove_number": [],  # stores the move numbers
        "san": [],  # stores a move in Standard Algebraic Notation (SAN)
        "lan": [],  # stores a move in Long Algebraic Notation (LAN)
        "move_count": [],  # stores the number of possible moves in this turn
        "score": [],  # stores the scores calculated by Stockfish
        "best_move_score_diff": [],  # stores the difference between the calculated best move and the actual move
        "best_move_score_diff_category": [],  # stores the category for the calculated difference
        "best_move": [],  # stores the best move in SAN
        "best_move_score": [],  # stores the best move's score
        "is_check": [],  # stores if the move checks the opposed king
        "is_capture": [],  # stores is the move actually captures a piece
        "pawnending": [],  # stores if only kings and pawns are left on the board
        "rookending": [],  # stores if only kings, rooks and possible pawns are left on the board
        "attackers": [],
        "attackers_count": [],  # stores the number of possible attacks/threats by the opponent
        "is_capture_count": [],  # stores the number of possible captures
        "is_castling": [],  # stores if the king has been castled
        "next_move_count": [],  # stores the number of possible moves for the next player
        "guarded_pieces": [],
        "guarded_pieces_count": [],
        "threatened_guarded_pieces": [],
        "threatened_guarded_pieces_count": []
    }

    # Get the intial board of the game
    board = act_game.board()
    print(board.fen())
    chess_io.export_board_svg(board, filename, len(counts["san"]))

    # Iterate through all moves and play them on a board.
    for move in act_game.mainline_moves():
        # calculate opportunities before applying the move
        actual_move = board.san(move)
        counts["fullmove_number"].append(board.fullmove_number)
        counts["san"].append(actual_move)
        counts["lan"].append(board.lan(move))
        move_cnt = [i for i in board.legal_moves]
        counts["move_count"].append(len(move_cnt))
        counts["is_capture"].append(board.is_capture(move))
        counts["is_castling"].append(board.is_castling(move))
        print("turn: ", board.turn)
        print("actual move: ", board.san(move), move)

        a_score, a_best_move = compute_score_alternative(engine, board)
        a_best_move_score = compute_best_move_alternative(engine, board, a_best_move)

        # apply move
        board.push(move)

        score = compute_score(engine, board)



        counts["score"].append(score)
        counts["is_check"].append(board.is_check())

        counts["pawnending"].append(pawn_ending(board.fen()))
        counts["rookending"].append(rook_ending(board.fen()))

        attacked_pieces = compute_attackers(board)
        counts["attackers"].append(attacked_pieces)
        counts["attackers_count"].append(len(attacked_pieces))
        counts["is_capture_count"].append(len([i for i in board.legal_moves if board.is_capture(i)]))

        guarded_pieces = compute_guarded_pieces(board)
        # print(guarded_pieces)
        counts["guarded_pieces"].append(guarded_pieces)
        counts["guarded_pieces_count"].append(len(guarded_pieces))
        threatened_guarded_pieces = compute_threatened_guarded_pieces(attacked_pieces, guarded_pieces)
        counts["threatened_guarded_pieces"].append(threatened_guarded_pieces)
        counts["threatened_guarded_pieces_count"].append(len(threatened_guarded_pieces.get('square')))

        move_cnt = len([i for i in board.legal_moves])
        counts["next_move_count"].append(move_cnt)
        # remove move to calculate the best move as well as the difference between the best move and the actual move
        board.pop()

        nextmovescores = compute_best_move(engine, board)

        if len(nextmovescores) > 1:
            # next_scores = [*nextmovescores.keys()]
            # next_scores.sort(reverse=board.turn)
            # print(nextmovescores)
            nextmovescores.sort(key=lambda scores: scores[0], reverse=board.turn)
            # print(nextmovescores)
            best_move = board.san(nextmovescores[0][1])
            counts["best_move"].append(best_move)
            counts["best_move_score"].append(nextmovescores[0][0])
            best_move_score_diff = abs(nextmovescores[0][0] - score)
            counts["best_move_score_diff"].append(best_move_score_diff)
            counts["best_move_score_diff_category"].append(
                categorize_best_move_score_diff(best_move_score_diff, best_move, actual_move))
        else:
            counts["best_move"].append("-")
            counts["best_move_score"].append(0)
            counts["best_move_score_diff"].append(0)

        # push actual move to the board again
        board.push(move)
        chess_io.export_board_svg(board, filename, len(counts["san"]))
        print('actual_score: ', score, ' alt_score: ', a_score)
        print('actual_best_move: ', best_move, ' best_score: ', nextmovescores[0][0])
        #print('alt_best_move: ', a_best_move, ' alt_best_score: ', a_best_move_score)

        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")


    SVG(chess.svg.board(board=board, size=400))

    plot_graph(act_game, filename, counts)

    chess_io.write_dict_to_csv(filename, counts)

    return 0


main()
