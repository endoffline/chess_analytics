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


# Get list of pieces on the board
def get_pieces_list(board):
    pieces = dict()
    pieces[chess.PAWN] = board.pieces(chess.PAWN, chess.WHITE).union(board.pieces(chess.PAWN, chess.BLACK))
    pieces[chess.KNIGHT] = board.pieces(chess.KNIGHT, chess.WHITE).union(board.pieces(chess.KNIGHT, chess.BLACK))
    pieces[chess.BISHOP] = board.pieces(chess.BISHOP, chess.WHITE).union(board.pieces(chess.BISHOP, chess.BLACK))
    pieces[chess.ROOK] = board.pieces(chess.ROOK, chess.WHITE).union(board.pieces(chess.ROOK, chess.BLACK))
    pieces[chess.QUEEN] = board.pieces(chess.QUEEN, chess.WHITE).union(board.pieces(chess.QUEEN, chess.BLACK))
    pieces[chess.KING] = board.pieces(chess.KING, chess.WHITE).union(board.pieces(chess.KING, chess.BLACK))

    return pieces


# Determines pawn end game is present
def compute_pawn_ending(board):
    p = get_pieces_list(board)

    return len(p[chess.PAWN]) > 0 and \
           len(p[chess.KNIGHT]) == 0 and \
           len(p[chess.BISHOP]) == 0 and \
           len(p[chess.ROOK]) == 0 and \
           len(p[chess.QUEEN]) == 0


# Determines pawn end game is present
def compute_rook_ending(board):
    p = get_pieces_list(board)

    return len(p[chess.PAWN]) >= 0 and \
           len(p[chess.KNIGHT]) == 0 and \
           len(p[chess.BISHOP]) == 0 and \
           len(p[chess.ROOK]) > 0 and \
           len(p[chess.QUEEN]) == 0


# Calculates the available legal moves
def compute_move_count(board):
    return len([i for i in board.legal_moves])


# Calculates the score and best move for a move by time
def compute_score(engine, board, time):
    play = engine.play(board=board, limit=chess.engine.Limit(time=time), info=Info.ALL)
    score = play.info.get('score').white().score()
    if score is None:
        score = 0
    return score, play.move


# Calculates the score and best move for a move by depth
def compute_score_by_depth(engine, board, depth):
    play = engine.play(board=board, limit=chess.engine.Limit(depth=depth), info=Info.ALL)
    score = play.info.get('score').white().score()
    if score is None:
        score = 0
    return score, play.move


# Calculates the score for a move by time, deprecated
def compute_score_a(engine, board, time):
    info = engine.analyse(board, chess.engine.Limit(time=time), info=Info.ALL)
    if info.get("score"):
        score = info.get("score").white().score()
    else:
        score = 0
    return score


# Calculates the score for a move by depth, deprecated
def compute_score_a_by_depth(engine, board, depth):
    info = engine.analyse(board, chess.engine.Limit(depth=depth), info=Info.ALL)
    if info.get("score"):
        score = info.get("score").white().score()
    else:
        score = 0
    return score


# Calculates the score for the best move by time
def compute_best_move_score(engine, board, move, time):
    board.push(move)
    info = engine.analyse(board=board, limit=chess.engine.Limit(time=time), info=Info.ALL)
    board.pop()
    score = info.get('score').white().score()
    if score is None:
        score = 0
    return score


# Calculates the score for the best move by depth
def compute_best_move_score_by_depth(engine, board, move, depth):
    board.push(move)
    info = engine.analyse(board=board, limit=chess.engine.Limit(depth=depth), info=Info.ALL)
    board.pop()
    score = info.get('score').white().score()
    if score is None:
        score = 0
    return score


# Calculates the scores for all possible legal moves in the current turn
# and returns a list containing the scores and moves as tuple
def compute_legal_move_scores(engine, board, time):
    move_scores = list()

    for mov in board.legal_moves:
        board.push(mov)
        info = engine.analyse(board=board, limit=chess.engine.Limit(time=time), info=Info.ALL)
        score = info.get("score").white().score()
        if score is not None:
            move_scores.append(tuple((score, mov)))
        board.pop()

    move_scores.sort(key=lambda scores: scores[0], reverse=board.turn)
    return move_scores


# Calculates the scores for all possible moves in the current turn
# and returns a sorted list containing the scores and moves as tuple
def compute_legal_move_scores_by_depth(engine, board, depth):
    move_scores = list()

    for mov in board.legal_moves:
        board.push(mov)
        info = engine.analyse(board, chess.engine.Limit(depth=depth), info=Info.ALL)
        score = info.get("score").white().score()
        if score is not None:
            move_scores.append(tuple((score, mov)))
        board.pop()

    move_scores.sort(key=lambda scores: scores[0], reverse=board.turn)
    return move_scores


# Computes a list of legal moves which lead to an improved or equal score evaluation
def compute_possible_moves_quality(engine, board, time, curr_score):
    move_scores = compute_legal_move_scores(engine, board, time)
    tolerance = 25  # inaccuracy / 2
    good_scores_count = 0
    for score, move in move_scores:
        if (board.turn == chess.WHITE and score >= (curr_score - tolerance)) \
                or (board.turn == chess.BLACK and score <= (curr_score + tolerance)):
            good_scores_count += 1

    pieces = board.piece_map()
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


# Evaluates a captures and returns a positive or negative centipawn value if the capture was a win or loss of material
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


# # Determines the attacking moves for a given square
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


# Generate guard moves for a given square
def compute_guard_moves_for_one_piece(board, square):
    guard_moves = list()
    guards = [i for i in board.attackers(board.color_at(square), square)]
    for guard in guards:
        guard_moves.append(chess.Move(guard, square))
    return guard_moves


# Generate defending moves for a player
def compute_guard_moves(board, color):
    pieces = board.piece_map()

    guard_moves = list()
    for square, piece in pieces.items():
        if piece.color == color:
            guards = board.attackers(color, square)
            for guard in guards:
                guard_moves.append(chess.Move(guard, square))

    return guard_moves


# Computes the attack defense relation and returns a centipawn value
# The attack defense relation takes all pieces involved in an attack into account, including the attacked piece,
# the attacker, the possible guards, and if the attacked piece is guarded
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


# Determines the moves which lead to possible captures
def compute_possible_captures(board):
    return [i for i in board.legal_moves if board.is_capture(i)]


# Determines a list of pieces which are guarded as well as attacked
def compute_attacked_guarded_pieces(attack_moves, guard_moves):
    threatened_guarded_pieces = list()
    for threatening_move in attack_moves:
        for guarding_move in guard_moves:
            if threatening_move.to_square == guarding_move.to_square:
                if threatening_move.to_square not in threatened_guarded_pieces:
                    threatened_guarded_pieces.append(guarding_move.to_square)

    return threatened_guarded_pieces


# Determines a list of pieces which are undefended and attacked
def compute_unopposed_threats(attacked_pieces, guarded_pieces):
    unopposed_threats = set()
    for attacked_piece in attacked_pieces:
        if attacked_piece not in guarded_pieces:
            unopposed_threats.add(attacked_piece)

    return list(unopposed_threats)


# Computes the centipawn values for one color's remaining pieces on the board
def compute_material_for_color(board, color):
    pieces = board.piece_map()
    squares = list()
    for square, piece in pieces.items():
        if piece.color == color:
            squares.append(square)
    return squares


# Compares the material for both players
def compute_material_centipawn(board):
    material_white = compute_material_for_color(board, chess.WHITE)
    material_black = compute_material_for_color(board, chess.BLACK)

    return get_pieces_centipawn_sum(board, material_white, False) - get_pieces_centipawn_sum(board, material_black, False)


# This method should determine the change in scores between two moves
def compute_score_change(prev_score, curr_score):
    if not prev_score:
        prev_score = 0
    if not curr_score:
        curr_score = 0
    return abs(curr_score - prev_score)


# This method evaluates if a move has an impact on the game,
# a score change category > 1 means the move caused a greater score change than the median of score changes
# 64 is the median score change from the analyzed 989 games
def compute_score_change_category(diff):
    return diff / 64


# Computes a fork for a square
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


# Computes the forks a given color has on the board and returns the attackers' squares
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


# Computes the a centipawn value for the in pins and skewers involved pieces of a given color
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


# Determines if a move is a pin or skewer
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


# Calculates the number of pins and skewers for a given color on the board
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


# Determines the threats on the board for the given attack moves or a certain color and evaluates them with the pieces associated centipawn value
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


# Determines the threats on the board for the given attack moves of a certain color
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
