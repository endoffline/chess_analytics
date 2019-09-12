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


def compute_move_count(board):
    return len([i for i in board.legal_moves])


# Calculates the score for a move
def compute_score(engine, board, time):
    # Start a search.
    # engine.position(board)
    # engine.go(movetime=100)
    #play = engine.play(board=board, limit=chess.engine.Limit(time=0.100), info=Info.ALL)
    #print(play)
    #print(board.san(play.move))
    #print(board.san(play.ponder))
    info = engine.analyse(board, chess.engine.Limit(time=time), info=Info.ALL)
    if info.get("score"):
        score = info.get("score").white().score()
    else:
        score = 0
    # print("Score: ", score)
    return score


# Calculates the score for a move
def compute_score_by_depth(engine, board, depth):
    # Start a search.
    # engine.position(board)
    # engine.go(movetime=100)
    #play = engine.play(board=board, limit=chess.engine.Limit(time=0.100), info=Info.ALL)
    #print(play)
    #print(board.san(play.move))
    #print(board.san(play.ponder))
    info = engine.analyse(board, chess.engine.Limit(depth=depth), info=Info.ALL)
    if info.get("score"):
        score = info.get("score").white().score()
    else:
        score = 0
    # print("Score: ", score)
    return score


def compute_score_alternative(engine, board, time):
    play = engine.play(board=board, limit=chess.engine.Limit(time=time), info=Info.ALL)
    print("unfiltered score:", play.info.get('score'), "white:", play.info.get('score').white(), play.move)
    score = play.info.get('score').white().score()
    if score is None:
        score = 0
    return score, play.move


def compute_score_alternative_by_depth(engine, board, depth):
    play = engine.play(board=board, limit=chess.engine.Limit(depth=depth), info=Info.ALL)
    score = play.info.get('score').white().score()
    if score is None:
        score = 0
    return score, play.move


def compute_best_move_score_alternative(engine, board, move, time):
    board.push(move)
    info = engine.analyse(board=board, limit=chess.engine.Limit(time=time), info=Info.ALL)
    board.pop()
    score = info.get('score').white().score()
    if score is None:
        score = 0
    return score


def compute_best_move_score_alternative_by_depth(engine, board, move, depth):
    board.push(move)
    info = engine.analyse(board=board, limit=chess.engine.Limit(depth=depth), info=Info.ALL)
    board.pop()
    score = info.get('score').white().score()
    if score is None:
        score = 0
    return score


# Calculates the scores for all possible moves in the current turn
# and returns a list containing the scores and moves as tuple
def compute_legal_move_scores(engine, board, time):
    movescores = list()

    for mov in board.legal_moves:
        board.push(mov)
        # engine.position(board)
        # engine.go(movetime=100)
        info = engine.analyse(board=board, limit=chess.engine.Limit(time=time), info=Info.ALL)
        score = info.get("score").white().score()
        if score is not None:
            if board.turn == chess.WHITE:
                movescores.append(tuple((score, mov)))
            elif board.turn == chess.BLACK:
                movescores.append(tuple((score, mov)))
        board.pop()

    movescores.sort(key=lambda scores: scores[0], reverse=board.turn)
    return movescores


def compute_threat_level(engine, board, time, curr_score):
    move_scores = compute_legal_move_scores(engine, board, time)

    good_scores_count = 0
    for score, move in move_scores:
        if (board.turn == chess.WHITE and score >= curr_score) or (board.turn == chess.BLACK and score <= curr_score):
            good_scores_count += 1
    if board.turn == chess.WHITE:
        print("white")
    else:
        print("black")
    pieces = board.piece_map()
    print("score: ", curr_score, " scores: ", [(i, board.san(j), pieces[j.from_square].symbol()) for i, j in move_scores])
    return good_scores_count


# Calculates the scores for all possible moves in the current turn
# and returns a list containing the scores and moves as tuple
def compute_best_move_by_depth(engine, board, depth):
    movescores = list()

    for mov in board.legal_moves:
        board.push(mov)
        # engine.position(board)
        # engine.go(movetime=100)
        info = engine.analyse(board, chess.engine.Limit(depth=depth))
        score = info.get("score").white().score()
        if score is not None:
            if board.turn == chess.WHITE:
                movescores.append(tuple((score, mov)))
            elif board.turn == chess.BLACK:
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


# Determines the attacking moves the given color can make
# Determines how many pieces of the current player are being threatened by the opponent
def compute_attack_moves(board, color):
    pieces = board.piece_map()

    attack_moves = list()
    for square, piece in pieces.items():
        attackers = [i for i in board.attackers(not piece.color, square) if
                     board.piece_at(i).color == color]
        attacker_types = [board.piece_at(i).symbol() for i in attackers]

        for a in attackers:
            attack_moves.append(chess.Move(a, square))

    return attack_moves


def compute_guard_moves(board, color):
    c_board = copy.deepcopy(board)

    # loop over one colors pieces
    pieces = c_board.piece_map()
    # print("Pieces")
    # print(pieces)
    bait_piece = chess.Piece(chess.QUEEN, not color)
    count = 0
    guard_moves = list()
    for square, piece in pieces.items():
        if piece.color == color:
            p = c_board.remove_piece_at(square)
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


def compute_guard_moves_alt(board, color):
    c_board = copy.deepcopy(board)

    # loop over one colors pieces
    pieces = c_board.piece_map()
    # print("Pieces")
    # print(pieces)
    bait_piece = chess.Piece(chess.QUEEN, not color)
    count = 0
    guard_moves = list()
    for square, piece in pieces.items():

        if piece.color == color:
            #print(get_square_name(square))
            p = c_board.remove_piece_at(square)
            c_board.set_piece_at(square, bait_piece)
            attackers = [i for i in board.attackers(color, square)]
            attacker_types = [board.piece_at(i).symbol() for i in attackers]
            #print(get_square_names(attackers))
            for a in attackers:
                # attacked_pieces.append([chess.SQUARE_NAMES[a], pieces[a].symbol(), chess.SQUARE_NAMES[square], piece.symbol()])
                guard_moves.append(chess.Move(a, square))

            c_board.remove_piece_at(square)
            c_board.set_piece_at(square, p)

            #p = c_board.remove_piece_at(square)
            #c_board.set_piece_at(square, bait_piece)

            #for mov in c_board.legal_moves:
            #    if mov.to_square == square and c_board.is_capture(mov):
                    # guarded_pieces.append([chess.SQUARE_NAMES[mov.from_square], pieces[mov.from_square].symbol(), chess.SQUARE_NAMES[square], piece.symbol()])
            #        guard_moves.append(mov)
            #c_board.remove_piece_at(square)
            #c_board.set_piece_at(square, p)

        # remove_piece_at()
        # loop over legal_moves
        # count moves to removed piece position

    return guard_moves


# Determines the attacking moves the given color can make
# Determines how many pieces of the current player are being threatened by the opponent
def compute_attack_defense_relation_centipawn1(board):
    c_board = copy.deepcopy(board)
    # loop over one colors pieces
    pieces = board.piece_map()

    attackers_white, attackers_black, threatened_pieces_white, threatened_pieces_black, guards_white, guards_black, guarded_pieces_white, guarded_pieces_black = ([] for i in range(8))
    for square, piece in pieces.items():
        attackers = [i for i in board.attackers(not piece.color, square)]
        if piece.color == chess.WHITE:
            attackers_white.extend(attackers)
            if len(attackers) > 0:
                threatened_pieces_white.append(square)
                guards = [i for i in board.attackers(piece.color, square)]
                guards_white.extend(guards)
                if len(guards) > 0:
                    guarded_pieces_white.append(square)
        else:
            attackers_black.extend(attackers)
            if len(attackers) > 0:
                threatened_pieces_black.append(square)
                guards = [i for i in board.attackers(piece.color, square)]
                guards_black.extend(guards)
                if len(guards) > 0:
                    guarded_pieces_black.append(square)

    score_white = (compute_pieces_centipawn_sum(board, guarded_pieces_white)
                   + compute_pieces_centipawn_sum(board, guards_white)
                   - compute_pieces_centipawn_sum(board, threatened_pieces_white)
                   - compute_pieces_centipawn_sum(board, attackers_white))
    score_black = (compute_pieces_centipawn_sum(board, guarded_pieces_black)
                   + compute_pieces_centipawn_sum(board, guards_black)
                   - compute_pieces_centipawn_sum(board, threatened_pieces_black)
                   - compute_pieces_centipawn_sum(board, attackers_black))
    return score_white - score_black


def compute_attack_defense_relation_centipawn2(guards_centipawn_white, guarded_pieces_centipawn_white,
                                               threatened_pieces_centipawn_white, attackers_centipawn_white,
                                               guards_centipawn_black, guarded_pieces_centipawn_black,
                                               threatened_pieces_centipawn_black, attackers_centipawn_black):
    return ((guards_centipawn_white + guarded_pieces_centipawn_white
             - threatened_pieces_centipawn_white - attackers_centipawn_white)
            - (guards_centipawn_black + guarded_pieces_centipawn_black
               - threatened_pieces_centipawn_black - attackers_centipawn_black))


def compute_captures(board):
    return [i for i in board.legal_moves if board.is_capture(i)]


# Get a list of squares from a moves list using the origin of the move
def compute_from_square_pieces(moves):
    return list(i.from_square for i in moves)


# Get a list of squares from a moves list using the destination of the move
def compute_to_square_pieces(moves):
    return list(i.to_square for i in moves)


def get_square_name(square):
    return chess.SQUARE_NAMES[square]


def get_square_names(squares):
    return [get_square_name(square) for square in squares]


# def compute_threatened_guarded_pieces(threatened_pieces, guarded_pieces):
#    threatened_guarded_pieces = dict({
#        'square': [],
#        'threatening_move': [],
#        'guarding_move': [],
#        'threats_square': [],
#        'guards_square': []
#    })
#    for threatening_move in threatened_pieces:
#        for guarding_move in guarded_pieces:
#            if threatening_move.to_square == guarding_move.to_square:
#                if threatening_move.to_square not in threatened_guarded_pieces.get('square'):
#                    threatened_guarded_pieces.get('square').append(guarding_move.to_square)
#                if threatening_move not in threatened_guarded_pieces.get('threatening_move'):
#                    threatened_guarded_pieces.get('threatening_move').append(threatening_move)
#                if guarding_move not in threatened_guarded_pieces.get('guarding_move'):
#                    threatened_guarded_pieces.get('guarding_move').append(guarding_move)
#    return threatened_guarded_pieces


def compute_threatened_guarded_pieces(attack_moves, guard_moves):
    threatened_guarded_pieces = list()
    for threatening_move in attack_moves:
        for guarding_move in guard_moves:
            if threatening_move.to_square == guarding_move.to_square:
                if threatening_move.to_square not in threatened_guarded_pieces:
                    threatened_guarded_pieces.append(guarding_move.to_square)

    return threatened_guarded_pieces


def compute_unopposed_threats(threatened_pieces, guarded_pieces):
    unopposed_threats = set()
    for threatened_piece in threatened_pieces:
        if threatened_piece not in guarded_pieces:
            unopposed_threats.add(threatened_piece)

    return list(unopposed_threats)


def compute_pieces_centipawn(board, squares):
    centipawns = [100, 300, 300, 500, 900, 0]
    return [centipawns[board.piece_at(square).piece_type-1] for square in squares]


def compute_pieces_centipawn_sum(board, squares):
    return sum(compute_pieces_centipawn(board, squares))


def compute_material_for_color(board, color):
    pieces = board.piece_map()
    squares = list()
    for square, piece in pieces.items():
        if piece.color == color:
            squares.append(square)
    return squares


def compute_material_centipawn(board):
    material_white = compute_material_for_color(board, chess.WHITE)
    material_black = compute_material_for_color(board, chess.BLACK)

    print("Material white: ", compute_pieces_centipawn_sum(board, material_white), ", ", material_white)
    print("Material black: ", compute_pieces_centipawn_sum(board, material_black), ", ", material_black)
    return compute_pieces_centipawn_sum(board, material_white) - compute_pieces_centipawn_sum(board, material_black)


# This method should determine the change in scores between two moves
# It is therefore possible to determine which player benefits from the move
# TODO evaluate
def compute_score_shift(prev_score, curr_score):
    print("prev_score: ", prev_score, ", curr_score: ", curr_score)
    if not prev_score:
        prev_score = 0
    if not curr_score:
        curr_score = 0
    return abs(curr_score - prev_score)


def compute_score_shift_category(diff):
    return diff / 50


def format_move(move):
    # [chess.SQUARE_NAMES[mov.from_square], pieces[mov.from_square].symbol(), chess.SQUARE_NAMES[square], piece.symbol()]
    return [chess.SQUARE_NAMES[move.from_square], chess.SQUARE_NAMES[move.to_square]]


