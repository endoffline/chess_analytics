import chess
import chess.svg
import chess.pgn
import chess.engine
from chess.engine import Info
import copy
import numpy as np


# Connect program with the chess engine Stockfish via UCI
def connect_to_stockfish():
    return chess.engine.SimpleEngine.popen_uci("engine/stockfish_10_x64.exe")


def read_game(pgn):
    return chess.pgn.read_game(pgn)


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


# Calculates the score for a move
def compute_score(engine, board):
    # Start a search.
    # engine.position(board)
    # engine.go(movetime=100)
    #play = engine.play(board=board, limit=chess.engine.Limit(time=0.100), info=Info.ALL)
    #print(play)
    #print(board.san(play.move))
    #print(board.san(play.ponder))
    info = engine.analyse(board, chess.engine.Limit(time=0.100))
    score = 0
    if board.turn == chess.WHITE:
        score = info.get("score").white().score()
    else:
        score = info["score"].white().score()
    # print("Score: ", score)
    return score


def compute_score_alternative(engine, board):
    play = engine.play(board=board, limit=chess.engine.Limit(time=0.100), info=Info.ALL)
    #print(play)
    #print("a best move: ", board.san(play.move))


    return play.info.get('score').white().score(), play.move


def compute_best_move_alternative(engine, board, move):
    #print("board:", board)


    #print("movemove: ", board.san(move), move)
    board.push(move)
    #print("board:", board)
    info = engine.analyse(board=board, limit=chess.engine.Limit(time=0.100), info=Info.ALL)
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
        info = engine.analyse(board, chess.engine.Limit(time=0.100))
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


# Determines how many pieces of the current player are being threatend by the opponent
def compute_attack_moves(board):
    pieces = board.piece_map()

    attack_moves = list()
    for square, piece in pieces.items():
        attackers = [i for i in board.attackers(not piece.color, square) if
                     i > 0 and board.piece_at(i).color != board.turn]
        attacker_types = [board.piece_at(i).symbol() for i in attackers]

        for a in attackers:
            # attacked_pieces.append([chess.SQUARE_NAMES[a], pieces[a].symbol(), chess.SQUARE_NAMES[square], piece.symbol()])
            attack_moves.append(chess.Move(a, square))

    return attack_moves


def compute_guard_moves(board):
    c_board = copy.deepcopy(board)

    # loop over one colors pieces
    pieces = c_board.piece_map()
    # print("Pieces")
    # print(pieces)
    bait_piece = chess.Piece(chess.QUEEN, not c_board.turn)
    count = 0
    guard_moves = list()
    for square, piece in pieces.items():
        if piece.color == c_board.turn:
            p = c_board.remove_piece_at(square);
            c_board.set_piece_at(square, bait_piece)

            for mov in c_board.legal_moves:
                if mov.to_square == square and c_board.is_capture(mov):
                    # guarded_pieces.append([chess.SQUARE_NAMES[mov.from_square], pieces[mov.from_square].symbol(), chess.SQUARE_NAMES[square], piece.symbol()])
                    guard_moves.append(mov)
            c_board.remove_piece_at(square)
            c_board.set_piece_at(square, p)

        # remove_piece_at()
        # loop over legal_moves
        # count moves to removed piece position

    return guard_moves


def compute_captures(board):
    return [i for i in board.legal_moves if board.is_capture(i)]


def compute_from_square_pieces(moves):
    return set(i.from_square for i in moves)


def compute_to_square_pieces(moves):
    return set(i.to_square for i in moves)


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
                if threatening_move not in threatened_guarded_pieces.get('threatening_move'):
                    threatened_guarded_pieces.get('threatening_move').append(threatening_move)
                if guarding_move not in threatened_guarded_pieces.get('guarding_move'):
                    threatened_guarded_pieces.get('guarding_move').append(guarding_move)

    return threatened_guarded_pieces

def compute_threatened_guarded_pieces_new(threatened_pieces, guarded_pieces):
    threatened_guarded_pieces = list()
    for threatening_move in threatened_pieces:
        for guarding_move in guarded_pieces:
            if threatening_move.to_square == guarding_move.to_square:
                if threatening_move.to_square not in threatened_guarded_pieces:
                    threatened_guarded_pieces.append(guarding_move.to_square)

    return threatened_guarded_pieces

def compute_unopposed_threats(threatened_pieces, guarded_pieces):
    unopposed_threats = set()
    for threatened_piece in threatened_pieces:
        if threatened_piece not in guarded_pieces:
            unopposed_threats.add(threatened_piece)

    return unopposed_threats


def format_move(move):
    # [chess.SQUARE_NAMES[mov.from_square], pieces[mov.from_square].symbol(), chess.SQUARE_NAMES[square], piece.symbol()]
    return [chess.SQUARE_NAMES[move.from_square], chess.SQUARE_NAMES[move.to_square]]


