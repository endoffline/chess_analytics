import chess
import chess.svg
import chess.pgn
import chess.engine
from chess.engine import Info
import copy
from collections import defaultdict


# Connect program with the chess engine Stockfish via UCI
def connect_to_stockfish():
    return chess.engine.SimpleEngine.popen_uci("engine/stockfish_10_x64.exe")


def read_game(pgn):
    return chess.pgn.read_game(pgn)


def get_pieces_list(board):
    pieces = dict()
    pieces[chess.PAWN] = board.pieces(chess.PAWN, chess.WHITE).union(board.pieces(chess.PAWN, chess.BLACK))
    pieces[chess.KNIGHT] = board.pieces(chess.KNIGHT, chess.WHITE).union(board.pieces(chess.KNIGHT, chess.BLACK))
    pieces[chess.BISHOP] = board.pieces(chess.BISHOP, chess.WHITE).union(board.pieces(chess.BISHOP, chess.BLACK))
    pieces[chess.ROOK] = board.pieces(chess.ROOK, chess.WHITE).union(board.pieces(chess.ROOK, chess.BLACK))
    pieces[chess.QUEEN] = board.pieces(chess.QUEEN, chess.WHITE).union(board.pieces(chess.QUEEN, chess.BLACK))
    pieces[chess.KING] = board.pieces(chess.KING, chess.WHITE).union(board.pieces(chess.KING, chess.BLACK))

    return pieces


def compute_pawn_ending(board):
    p = get_pieces_list(board)

    return len(p[chess.PAWN]) > 0 and \
           len(p[chess.KNIGHT]) == 0 and \
           len(p[chess.BISHOP]) == 0 and \
           len(p[chess.ROOK]) == 0 and \
           len(p[chess.QUEEN]) == 0


def compute_rook_ending(board):
    p = get_pieces_list(board)

    return len(p[chess.PAWN]) >= 0 and \
           len(p[chess.KNIGHT]) == 0 and \
           len(p[chess.BISHOP]) == 0 and \
           len(p[chess.ROOK]) > 0 and \
           len(p[chess.QUEEN]) == 0


def compute_move_count(board):
    return len([i for i in board.legal_moves])


# Calculates the score for a move
def compute_score_a(engine, board, time):
    info = engine.analyse(board, chess.engine.Limit(time=time), info=Info.ALL)
    if info.get("score"):
        score = info.get("score").white().score()
    else:
        score = 0
    return score


# Calculates the score for a move
def compute_score_a_by_depth(engine, board, depth):
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


def compute_score(engine, board, time):
    play = engine.play(board=board, limit=chess.engine.Limit(time=time), info=Info.ALL)
    score = play.info.get('score').white().score()
    if score is None:
        score = 0
    return score, play.move


def compute_score_by_depth(engine, board, depth):
    play = engine.play(board=board, limit=chess.engine.Limit(depth=depth), info=Info.ALL)
    score = play.info.get('score').white().score()
    if score is None:
        score = 0
    return score, play.move


def compute_best_move_score(engine, board, move, time):
    board.push(move)
    info = engine.analyse(board=board, limit=chess.engine.Limit(time=time), info=Info.ALL)
    board.pop()
    score = info.get('score').white().score()
    if score is None:
        score = 0
    return score


def compute_best_move_score_by_depth(engine, board, move, depth):
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


# Calculates the scores for all possible moves in the current turn
# and returns a list containing the scores and moves as tuple
def compute_legal_move_scores_by_depth(engine, board, depth):
    move_scores = list()

    for mov in board.legal_moves:
        board.push(mov)
        info = engine.analyse(board, chess.engine.Limit(depth=depth), info=Info.ALL)
        score = info.get("score").white().score()
        if score is not None:
            if board.turn == chess.WHITE:
                move_scores.append(tuple((score, mov)))
            elif board.turn == chess.BLACK:
                move_scores.append(tuple((score, mov)))
        board.pop()

    move_scores.sort(key=lambda scores: scores[0], reverse=board.turn)
    return move_scores


def compute_possible_moves_quality(engine, board, time, curr_score):
    move_scores = compute_legal_move_scores(engine, board, time)
    tolerance = 25  # inaccuracy / 2
    good_scores_count = 0
    for score, move in move_scores:
        if (board.turn == chess.WHITE and score >= (curr_score - tolerance)) \
                or (board.turn == chess.BLACK and score <= (curr_score + tolerance)):
            good_scores_count += 1

    pieces = board.piece_map()
    print("move quality: score: ", curr_score, " scores: ", [(i, board.san(j), pieces[j.from_square].symbol()) for i, j in move_scores])
    return good_scores_count


# Categorizes a move being a blunder(4), mistake(3), inaccuracy(2), neutral move(1) or good move(0)
def categorize_best_move_score_diff(best_move_score_diff, best_move, actual_move):
    category = 1

    if best_move_score_diff >= 300:
        category = 4
    elif best_move_score_diff >= 100:
        category = 3
    elif best_move_score_diff >= 50:
        category = 2
    elif best_move == actual_move:
        category = 0

    return category


def compute_is_capture_weighted(board, move):
    value = 0
    if board.is_capture(move):
        value = get_piece_centipawn(board, move.to_square, True)
        if len(board.attackers(not board.turn, move.to_square)) > 0:  # guarded
            value -= get_piece_centipawn(board, move.from_square, False)
        else:
            previous_move = board.pop()
            if board.is_capture(previous_move) and previous_move.to_square == move.to_square:  # exchange
                value -= get_piece_centipawn(board, previous_move.to_square, False)
            board.push(previous_move)

    return value


#deprecated
def compute_is_capture_weighted_old(board, move):
    value = 0
    if board.is_capture(move):
        already_deducted = False
        value = get_piece_centipawn(board, move.to_square, True)
        previous_move = board.pop()
        if board.is_capture(previous_move) and previous_move.to_square == move.to_square:  # exchange
            value -= get_piece_centipawn(board, previous_move.to_square, False)
            already_deducted = True
        board.push(previous_move)
        if not already_deducted and len(board.attackers(not board.turn, move.to_square)) > 0:  # guarded
            value -= get_piece_centipawn(board, move.from_square, False)

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

        for a in attackers:
            attack_moves.append(chess.Move(a, square))

    return attack_moves


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


def compute_attacked_guarded_pieces(attack_moves, guard_moves):
    threatened_guarded_pieces = list()
    for threatening_move in attack_moves:
        for guarding_move in guard_moves:
            if threatening_move.to_square == guarding_move.to_square:
                if threatening_move.to_square not in threatened_guarded_pieces:
                    threatened_guarded_pieces.append(guarding_move.to_square)

    return threatened_guarded_pieces


def compute_unopposed_threats(attacked_pieces, guarded_pieces):
    unopposed_threats = set()
    for attacked_piece in attacked_pieces:
        if attacked_piece not in guarded_pieces:
            unopposed_threats.add(attacked_piece)

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

    return get_pieces_centipawn_sum(board, material_white, False) - get_pieces_centipawn_sum(board, material_black, False)


# This method should determine the change in scores between two moves
# It is therefore possible to determine which player benefits from the move
def compute_score_change(prev_score, curr_score):
    if not prev_score:
        prev_score = 0
    if not curr_score:
        curr_score = 0
    return abs(curr_score - prev_score)


# 64 is the median score change from the analyzed 989 games
def compute_score_change_category(diff):
    return diff / 64


def compute_fork(board, color, square, piece):
    forking_square = None
    if piece.color == color:
        attacked_squares = board.attacks(square)
        attacked_count = 0
        for attacked_square in attacked_squares:
            if board.color_at(attacked_square) is (not color):
                # only consider defended pieces with higher value or undefended pieces
                if len(compute_guard_moves_for_one_piece(board, attacked_square)) > 0:
                    if get_piece_centipawn(board, attacked_square, True) > get_piece_centipawn(board, square, True):
                        attacked_count += 1
                else:
                    attacked_count += 1
        if attacked_count > 1:
            forking_square = square
    return forking_square


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
                        if get_piece_centipawn(board, attacked_square, True) > get_piece_centipawn(board, square, True):
                            attacked_count += 1
                    else:
                        attacked_count += 1

            if attacked_count > 1:
                print("fork by ", piece, " on ", get_square_name(square))
                forking_squares.append(square)

    return forking_squares


def compute_xray_attacks_weighted(board, color):
    c_board = copy.deepcopy(board)
    attack_moves = compute_attack_moves(c_board, color)
    value = 0

    for move in attack_moves:
        attacker = move.from_square
        attacked_square = move.to_square
        # check if attacking piece is a sliding piece (bishop, rook, queen)
        if c_board.piece_type_at(attacker) in [chess.BISHOP, chess.ROOK, chess.QUEEN]:
            attacked_piece_value = get_piece_centipawn(c_board, attacked_square, True)
            attacked_piece = c_board.remove_piece_at(attacked_square)
            altered_attack_moves = compute_attack_moves_for_one_piece(c_board, attacker)

            xray = [a for a in altered_attack_moves if a not in attack_moves]

            if xray:
                indirectly_attacked_piece_value = get_piece_centipawn(c_board, xray[0].to_square, True)

                if indirectly_attacked_piece_value > attacked_piece_value:  # pin
                    value += indirectly_attacked_piece_value + (indirectly_attacked_piece_value - attacked_piece_value)
                else:  # skewer
                    value += attacked_piece_value + (attacked_piece_value - indirectly_attacked_piece_value)
            c_board.set_piece_at(attacked_square, attacked_piece)
    return value


def compute_xray_attacks_for_single_move(board, attack_moves, move):
    pin_move = None
    skewer_move = None
    attacker = move.from_square
    attacked_square = move.to_square
    # check if attacking piece is a sliding piece (bishop, rook, queen)
    if board.piece_type_at(attacker) in [chess.BISHOP, chess.ROOK, chess.QUEEN]:
        attacked_piece_value = get_piece_centipawn(board, attacked_square, True)
        attacked_piece = board.remove_piece_at(attacked_square)
        altered_attack_moves = compute_attack_moves_for_one_piece(board, attacker)

        xray = [a for a in altered_attack_moves if a not in attack_moves]

        if xray:
            indirectly_attacked_piece_value = get_piece_centipawn(board, xray[0].to_square, True)

            if indirectly_attacked_piece_value > attacked_piece_value:
                pin_move = move
            else:
                skewer_move = move
        board.set_piece_at(attacked_square, attacked_piece)

    return pin_move, skewer_move


# calculates the number of pins and skewers
def compute_xray_attack_moves(board, color):
    c_board = copy.deepcopy(board)
    attack_moves = compute_attack_moves(c_board, color)
    pin_moves = list()
    skewer_moves = list()

    for move in attack_moves:
        attacker = move.from_square
        attacked_square = move.to_square
        # check if attacking piece is a sliding piece (bishop, rook, queen)
        if c_board.piece_type_at(attacker) in [chess.BISHOP, chess.ROOK, chess.QUEEN]:
            attacked_piece_value = get_piece_centipawn(c_board, attacked_square, True)
            attacked_piece = c_board.remove_piece_at(attacked_square)
            altered_attack_moves = compute_attack_moves_for_one_piece(c_board, attacker)

            xray = [a for a in altered_attack_moves if a not in attack_moves]

            if xray:
                indirectly_attacked_piece_value = get_piece_centipawn(c_board, xray[0].to_square, True)

                if indirectly_attacked_piece_value > attacked_piece_value:
                    pin_moves.append(move)
                else:
                    skewer_moves.append(move)
            c_board.set_piece_at(attacked_square, attacked_piece)
    return pin_moves, skewer_moves


# proposal include centipawn for threatened piece and least valuable attacker if threatened piece is guarded
def compute_threats_weighted(board, attack_moves, attacked_guarded_squares):
    value = 0
    attack_dict = defaultdict(list)
    for attack_move in attack_moves:
        if attack_move.to_square in attacked_guarded_squares:
            if get_piece_centipawn(board, attack_move.to_square, True) > get_piece_centipawn(board, attack_move.from_square, True):
                value += get_piece_centipawn(board, attack_move.to_square, True)
                attack_dict[attack_move.to_square].append(attack_move.from_square)
        else:
            value += get_piece_centipawn(board, attack_move.to_square, True)

    for guarded_square, attacking_squares in attack_dict.items():
        value -= min(get_pieces_centipawn(board, attacking_squares, True))

    return value


# proposal include centipawn for threatened piece, least valuable attacker and least valuable defender
def compute_threat_moves_weighted(board, attack_moves, attacked_guarded_squares):
    threat_moves = list()
    for attack_move in attack_moves:

        if attack_move.to_square in attacked_guarded_squares:
            if get_piece_centipawn(board, attack_move.to_square, True) > get_piece_centipawn(board, attack_move.from_square, True):
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
    return [chess.SQUARE_NAMES[move.from_square], chess.SQUARE_NAMES[move.to_square]]


def format_moves(moves):
    return [format_move(move) for move in moves]


def get_piece_centipawn(board, square, include_king=False):
    piece_values = [100, 300, 300, 500, 900, 2200 if include_king else 0]
    return piece_values[(board.piece_at(square).piece_type-1) if board.piece_at(square) else 0] # check for en passant


def get_pieces_centipawn(board, squares, include_king=False):
    piece_values = [100, 300, 300, 500, 900, 2200 if include_king else 0]
    return [piece_values[(board.piece_at(square).piece_type-1) if board.piece_at(square) else 0] for square in squares]


def get_pieces_centipawn_sum(board, squares, include_king=False):
    return sum(get_pieces_centipawn(board, squares, include_king))
