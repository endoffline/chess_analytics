import chess
import chess.svg
import chess.pgn
import chess.engine
from chess.engine import Info
import copy
import numpy as np
from collections import defaultdict


# Connect program with the chess engine Stockfish via UCI
def connect_to_stockfish():
    return chess.engine.SimpleEngine.popen_uci("engine/stockfish_10_x64.exe")


def read_game(pgn):
    return chess.pgn.read_game(pgn)


# Convert the board from the FEN notation to an 3 dimensional array for easier evaluation
# deprecated
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


# deprecated
def count_pieces(fen):
    boardtensor = fen_to_tensor(fen)
    count = np.sum(np.abs(boardtensor))
    return count


# deprecated
def pawn_ending(fen):
    boardtensor = fen_to_tensor(fen)
    counts = np.sum(np.abs(boardtensor), axis=(0, 1))
    if counts[1] == 0 and counts[2] == 0 and counts[3] == 0 and counts[4] == 0:
        return True
    else:
        return False


# deprecated
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
    move_scores = list()

    for mov in board.legal_moves:
        board.push(mov)
        # engine.position(board)
        # engine.go(movetime=100)
        info = engine.analyse(board=board, limit=chess.engine.Limit(time=time), info=Info.ALL)
        score = info.get("score").white().score()
        if score is not None:
            if board.turn == chess.WHITE:
                move_scores.append(tuple((score, mov)))
            elif board.turn == chess.BLACK:
                move_scores.append(tuple((score, mov)))
        board.pop()

    move_scores.sort(key=lambda scores: scores[0], reverse=board.turn)
    return move_scores


# introduce tolerance of 30 to 50 centipawn
def compute_possible_moves_quality(engine, board, time, curr_score):
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
    move_scores = list()

    for mov in board.legal_moves:
        board.push(mov)
        # engine.position(board)
        # engine.go(movetime=100)
        info = engine.analyse(board, chess.engine.Limit(depth=depth))
        score = info.get("score").white().score()
        if score is not None:
            if board.turn == chess.WHITE:
                move_scores.append(tuple((score, mov)))
            elif board.turn == chess.BLACK:
                move_scores.append(tuple((score, mov)))
        board.pop()

    return move_scores


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


def compute_is_capture_weighted(board, move):
    value = 0
    if board.is_capture(move):
        already_deducted = False
        value = get_piece_centipawn(board, move.to_square)
        previous_move = board.pop()
        if board.is_capture(previous_move) and previous_move.to_square == move.to_square:
            value -= get_piece_centipawn(board, previous_move.to_square)
            already_deducted = True
        board.push(previous_move)
        if not already_deducted and len(board.attackers(not board.turn, move.to_square)) > 0:
            value -= get_piece_centipawn(board, move.from_square)

    return value


def compute_attack_moves_for_one_piece(board, square):
    attack_moves = list()
    attacked_squares = [i for i in board.attacks(square) if board.color_at(i) is (not board.color_at(square))]
    for a in attacked_squares:
        attack_moves.append(chess.Move(square, a))
    return attack_moves


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


# deprecated
def compute_guard_moves_old(board, color):
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


#deprecated
def compute_guard_moves_old2(board, color):
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


# generate guard moves for one square
def compute_guard_moves_for_one_piece(board, square):
    guard_moves = list()
    guards = [i for i in board.attackers(board.color_at(square), square)]
    for guard in guards:
        guard_moves.append(chess.Move(guard, square))
    return guard_moves


# generate defending moves for a player
def compute_guard_moves(board, color):
    # loop over one colors pieces
    pieces = board.piece_map()

    guard_moves = list()
    for square, piece in pieces.items():
        if piece.color == color:
            guards = board.attackers(color, square)
            for guard in guards:
                guard_moves.append(chess.Move(guard, square))

    return guard_moves


# Determines the attacking moves the given color can make
# Determines how many pieces of the current player are being threatened by the opponent
def compute_attack_defense_relation_centipawn1(board):
    c_board = copy.deepcopy(board)
    # loop over one colors pieces
    pieces = board.piece_map()

    attackers_white, attackers_black, attacked_pieces_white, attacked_pieces_black, guards_white, guards_black, guarded_pieces_white, guarded_pieces_black = ([] for i in range(8))
    for square, piece in pieces.items():
        attackers = [i for i in board.attackers(not piece.color, square)]
        if piece.color == chess.WHITE:
            attackers_white.extend(attackers)
            if len(attackers) > 0:
                attacked_pieces_white.append(square)
                guards = [i for i in board.attackers(piece.color, square)]
                guards_white.extend(guards)
                if len(guards) > 0:
                    guarded_pieces_white.append(square)
        else:
            attackers_black.extend(attackers)
            if len(attackers) > 0:
                attacked_pieces_black.append(square)
                guards = [i for i in board.attackers(piece.color, square)]
                guards_black.extend(guards)
                if len(guards) > 0:
                    guarded_pieces_black.append(square)

    score_white = (get_pieces_centipawn_sum(board, guarded_pieces_white)
                   + get_pieces_centipawn_sum(board, guards_white)
                   - get_pieces_centipawn_sum(board, attacked_pieces_white)
                   - get_pieces_centipawn_sum(board, attackers_white))
    score_black = (get_pieces_centipawn_sum(board, guarded_pieces_black)
                   + get_pieces_centipawn_sum(board, guards_black)
                   - get_pieces_centipawn_sum(board, attacked_pieces_black)
                   - get_pieces_centipawn_sum(board, attackers_black))
    return score_white - score_black


def compute_attack_defense_relation_centipawn2(guards_centipawn_white, guarded_pieces_centipawn_white,
                                               attacked_pieces_centipawn_white, attackers_centipawn_white,
                                               guards_centipawn_black, guarded_pieces_centipawn_black,
                                               attacked_pieces_centipawn_black, attackers_centipawn_black):
    return ((guards_centipawn_white + guarded_pieces_centipawn_white
             - attacked_pieces_centipawn_white - attackers_centipawn_white)
            - (guards_centipawn_black + guarded_pieces_centipawn_black
               - attacked_pieces_centipawn_black - attackers_centipawn_black))


def compute_possible_captures(board):
    return [i for i in board.legal_moves if board.is_capture(i)]


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


def compute_attacked_guarded_pieces(attack_moves, guard_moves):
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

    print("Material white: ", get_pieces_centipawn_sum(board, material_white), ", ", material_white)
    print("Material black: ", get_pieces_centipawn_sum(board, material_black), ", ", material_black)
    return get_pieces_centipawn_sum(board, material_white) - get_pieces_centipawn_sum(board, material_black)


# This method should determine the change in scores between two moves
# It is therefore possible to determine which player benefits from the move
def compute_score_change(prev_score, curr_score):
    print("prev_score: ", prev_score, ", curr_score: ", curr_score)
    if not prev_score:
        prev_score = 0
    if not curr_score:
        curr_score = 0
    return abs(curr_score - prev_score)


def compute_score_change_category(diff):
    return diff / 50


def compute_forks(board, color):
    pieces = board.piece_map()

    forking_squares = list()
    for square, piece in pieces.items():
        if piece.color == color:
            attacked_squares = board.attacks(square)
            attacked_count = 0
            for attacked_square in attacked_squares:
                if board.color_at(attacked_square) is (not color):
                    # only consider pieces with defended pieces with higher value or undefended pieces
                    if len(compute_guard_moves_for_one_piece(board, attacked_square)) > 0:
                        if get_piece_centipawn(board, attacked_square) > get_piece_centipawn(board, square):
                            attacked_count += 1
                    else:
                        attacked_count += 1

                # if attacked_square in pieces and board.piece_at(attacked_square).color is not color:
                #    print("pieces", pieces[attacked_square])
                #    attacked_count += 1
            if attacked_count > 1:
                print("fork by ", piece, " on ", get_square_name(square))
            #if len(attacked_squares) > 1:
            #    print(get_square_names(attacked_squares))
            #    forking_squares.append(square)

    return forking_squares


# todo rethink return parameter
def compute_xray_attacks(board, color):
    c_board = copy.deepcopy(board)
    attack_moves = compute_attack_moves(c_board, color)
    value = 0

    for move in attack_moves:
        attacker = move.from_square
        attacked_square = move.to_square
        # check if attacking piece is a sliding piece (bishop, rook, queen)
        if c_board.piece_type_at(attacker) in [3, 4, 5]:
            attacked_piece_value = get_piece_centipawn(c_board, attacked_square)
            attacked_piece = c_board.remove_piece_at(attacked_square)
            altered_attack_moves = compute_attack_moves_for_one_piece(c_board, attacker)

            xray = [a for a in altered_attack_moves if a not in attack_moves]

            if xray:
                indirectly_attacked_piece_value = get_piece_centipawn(c_board, xray[0].to_square)

                if indirectly_attacked_piece_value > attacked_piece_value:
                    # pin
                    value += indirectly_attacked_piece_value + (indirectly_attacked_piece_value - attacked_piece_value)
                    print("pin: ", get_square_name(attacker))
                else:
                    # skewer
                    value += attacked_piece_value + (attacked_piece_value - indirectly_attacked_piece_value)
                    print("skewer: ", get_square_name(attacker))
            c_board.set_piece_at(attacked_square, attacked_piece)
    return value


# calculates the number of pins and skewers
def compute_xray_attacks_counts(board, color):
    c_board = copy.deepcopy(board)
    attack_moves = compute_attack_moves(c_board, color)
    pin_count = 0
    skewer_count = 0

    for move in attack_moves:
        attacker = move.from_square
        attacked_square = move.to_square
        # check if attacking piece is a sliding piece (bishop, rook, queen)
        if c_board.piece_type_at(attacker) in [3, 4, 5]:
            attacked_piece_value = get_piece_centipawn(c_board, attacked_square)
            attacked_piece = c_board.remove_piece_at(attacked_square)
            altered_attack_moves = compute_attack_moves_for_one_piece(c_board, attacker)

            xray = [a for a in altered_attack_moves if a not in attack_moves]

            if xray:
                indirectly_attacked_piece_value = get_piece_centipawn(c_board, xray[0].to_square)

                if indirectly_attacked_piece_value > attacked_piece_value:
                    pin_count += 1
                else:
                    skewer_count += 1
            c_board.set_piece_at(attacked_square, attacked_piece)
    return pin_count, skewer_count


# proposal include centipawn for threatened piece, least valuable attacker and least valuable defender
def compute_threats_weighted(board, attack_moves, guard_moves, threatened_guarded_squares):
    value = 0
    # attack_dict = set()
    attack_dict = defaultdict(list)
    guard_dict = defaultdict(list)
    for attack_move in attack_moves:
        if attack_move.to_square in threatened_guarded_squares:
            attack_dict[attack_move.to_square].append(attack_move.from_square)
        else:
            value += get_piece_centipawn(board, attack_move.to_square)

    for guard_move in guard_moves:
        if guard_move.to_square in threatened_guarded_squares:
            attack_dict[attack_move.to_square].append(guard_move.from_square)

        # if attack_move.to_square not in guarded_squares:
        #    value += compute_piece_centipawn(board, attack_move.to_square)
        # else:
            # attack_dict.add(attack_move.from_square)
            # attack_dict[attack_move.to_square].append(attack_move.from_square)

    # if len(attack_dict) > 0:
    #    value -= compute_pieces_centipawn_sum(board, attack_dict) / len(attack_dict)
    already_deducted_attacking_squares = set()
    for guarded_square, attacking_squares in attack_dict.items():
        value -= min(get_pieces_centipawn(board, attacking_squares))
        # value -= compute_pieces_centipawn_sum(board, attacking_squares) / len(attacking_squares)
    # for guarded_square, guarding_squares in guard_dict.items():
    #    value += min(compute_pieces_centipawn(board, guarding_squares))

    return value


# proposal include centipawn for threatened piece, least valuable attacker and least valuable defender
def compute_threats_weighted_count(board, attack_moves, guard_moves, attacked_guarded_squares):
    threat_moves = list()
    for attack_move in attack_moves:
        if attack_move.to_square in attacked_guarded_squares:
            if get_piece_centipawn(board, attack_move.to_square) > get_piece_centipawn(board, attack_move.from_square):
                threat_moves.append(attack_move)
        else:
            threat_moves.append(attack_move)

    return threat_moves


# Get a list of squares from a moves list using the origin of the move
def get_from_square_pieces(moves):
    return list(i.from_square for i in moves)


# Get a list of squares from a moves list using the destination of the move
def get_to_square_pieces(moves):
    return list(i.to_square for i in moves)


def get_square_name(square):
    return chess.SQUARE_NAMES[square]


def get_square_names(squares):
    return [get_square_name(square) for square in squares]


def format_move(move):
    # [chess.SQUARE_NAMES[mov.from_square], pieces[mov.from_square].symbol(), chess.SQUARE_NAMES[square], piece.symbol()]
    return [chess.SQUARE_NAMES[move.from_square], chess.SQUARE_NAMES[move.to_square]]


def format_moves(moves):
    return [format_move(move) for move in moves]


def get_piece_centipawn(board, square):
    piece_values = [100, 300, 300, 500, 900, 2200]
    return piece_values[board.piece_at(square).piece_type-1]


def get_pieces_centipawn(board, squares):
    piece_values = [100, 300, 300, 500, 900, 2200]
    return [piece_values[board.piece_at(square).piece_type-1] for square in squares]


def get_pieces_centipawn_sum(board, squares):
    return sum(get_pieces_centipawn(board, squares))