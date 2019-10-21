import chess
from lib import chess_analysis
from models.move import Move
from models.score import Score
from models.timing import Timing
from models.timing_score import TimingScore
from time import monotonic


def compute_move(engine, board, mv, ply_number, times, depths, prev_score, best_moves_b):
    move_start_time = monotonic()
    scores_a, best_moves_a, best_move_scores_a, best_move_score_diffs_a, best_move_score_diff_categories_a = [], [], [], [], []
    scores_b, next_best_moves_b, best_move_scores_b, best_move_score_diffs_b, best_move_score_diff_categories_b = [], [], [], [], []
    t_scores_a, t_best_moves_a, t_best_move_scores_a, t_best_move_score_diffs_a, t_best_move_score_diff_categories_a = [], [], [], [], []
    t_scores_b, t_best_moves_b, t_best_move_scores_b, t_best_move_score_diffs_b, t_best_move_score_diff_categories_b = [], [], [], [], []

    start = monotonic()
    fullmove_number = board.fullmove_number
    t_fullmove_number = monotonic() - start

    start = monotonic()
    turn = board.turn
    t_turn = monotonic() - start

    start = monotonic()
    san = board.san(mv)
    t_san = monotonic() - start

    start = monotonic()
    lan = board.lan(mv)
    t_lan = monotonic() - start

    start = monotonic()
    move_count = chess_analysis.compute_move_count(board)
    t_move_count = monotonic() - start

    start = monotonic()
    is_capture = board.is_capture(mv)
    t_is_capture = monotonic() - start

    start = monotonic()
    is_castling = board.is_castling(mv)
    t_is_castling = monotonic() - start

    # apply move
    board.push(mv)

    for time in times:
        start = monotonic()
        score_a = chess_analysis.compute_score(engine, board, time)
        t_score_a = monotonic() - start
        scores_a.append(score_a)
        t_scores_a.append(t_score_a)

    for depth in depths:
        start = monotonic()
        score_a = chess_analysis.compute_score_by_depth(engine, board, depth)
        t_score_a = monotonic() - start
        scores_a.append(score_a)
        t_scores_a.append(t_score_a)

    start = monotonic()
    score_shift = chess_analysis.compute_score_shift(prev_score, scores_a[3])
    t_score_shift = monotonic() - start

    start = monotonic()
    score_shift_category = chess_analysis.compute_score_shift_category(score_shift)
    t_score_shift_category = monotonic() - start

    start = monotonic()
    is_check = board.is_check()
    t_is_check = monotonic() - start

    start = monotonic()
    possible_moves_count = chess_analysis.compute_move_count(board)
    t_possible_moves_count = monotonic() - start

    start = monotonic()
    captures = chess_analysis.compute_possible_captures(board)
    captures = chess_analysis.compute_to_square_pieces(captures)
    t_captures = monotonic() - start

    start = monotonic()
    is_capture_count = len(captures)
    t_is_capture_count = monotonic() - start

    # White player
    start = monotonic()
    attack_moves_white = chess_analysis.compute_attack_moves(board, chess.BLACK)
    attackers_white = chess_analysis.compute_from_square_pieces(attack_moves_white)
    t_attackers_white = monotonic() - start

    start = monotonic()
    attackers_count_white = len(attackers_white)
    t_attackers_count_white = monotonic() - start

    start = monotonic()
    threatened_pieces_white = chess_analysis.compute_to_square_pieces(attack_moves_white)
    t_threatened_pieces_white = monotonic() - start

    start = monotonic()
    threatened_pieces_count_white = len(threatened_pieces_white)
    t_threatened_pieces_count_white = monotonic() - start

    start = monotonic()
    guard_moves_white = chess_analysis.compute_guard_moves_alt(board, chess.WHITE)
    guards_white = chess_analysis.compute_from_square_pieces(guard_moves_white)
    t_guards_white = monotonic() - start

    start = monotonic()
    guards_count_white = len(guards_white)
    t_guards_count_white = monotonic() - start

    start = monotonic()
    guarded_pieces_white = chess_analysis.compute_to_square_pieces(guard_moves_white)
    t_guarded_pieces_white = monotonic() - start

    start = monotonic()
    guarded_pieces_count_white = len(guarded_pieces_white)
    t_guarded_pieces_count_white = monotonic() - start

    start = monotonic()
    threatened_guarded_pieces_white = chess_analysis.compute_threatened_guarded_pieces(attack_moves_white,
                                                                                       guard_moves_white)
    t_threatened_guarded_pieces_white = monotonic() - start

    start = monotonic()
    threatened_guarded_pieces_count_white = len(threatened_guarded_pieces_white)
    t_threatened_guarded_pieces_count_white = monotonic() - start

    start = monotonic()
    unopposed_threats_white = chess_analysis.compute_unopposed_threats(threatened_pieces_white, guarded_pieces_white)
    t_unopposed_threats_white = monotonic() - start

    start = monotonic()
    unopposed_threats_count_white = len(unopposed_threats_white)
    t_unopposed_threats_count_white = monotonic() - start

    # Black player
    start = monotonic()
    attack_moves_black = chess_analysis.compute_attack_moves(board, chess.WHITE)
    attackers_black = chess_analysis.compute_from_square_pieces(attack_moves_black)
    t_attackers_black = monotonic() - start

    start = monotonic()
    attackers_count_black = len(attackers_black)
    t_attackers_count_black = monotonic() - start

    start = monotonic()
    threatened_pieces_black = chess_analysis.compute_to_square_pieces(attack_moves_black)
    t_threatened_pieces_black = monotonic() - start

    start = monotonic()
    threatened_pieces_count_black = len(threatened_pieces_black)
    t_threatened_pieces_count_black = monotonic() - start

    start = monotonic()
    guard_moves_black = chess_analysis.compute_guard_moves_alt(board, chess.BLACK)
    guards_black = chess_analysis.compute_from_square_pieces(guard_moves_black)
    t_guards_black = monotonic() - start

    start = monotonic()
    guards_count_black = len(guards_black)
    t_guards_count_black = monotonic() - start

    start = monotonic()
    guarded_pieces_black = chess_analysis.compute_to_square_pieces(guard_moves_black)
    t_guarded_pieces_black = monotonic() - start

    start = monotonic()
    guarded_pieces_count_black = len(guarded_pieces_black)
    t_guarded_pieces_count_black = monotonic() - start

    start = monotonic()
    threatened_guarded_pieces_black = chess_analysis.compute_threatened_guarded_pieces(attack_moves_black,
                                                                                       guard_moves_black)
    t_threatened_guarded_pieces_black = monotonic() - start

    start = monotonic()
    threatened_guarded_pieces_count_black = len(threatened_guarded_pieces_black)
    t_threatened_guarded_pieces_count_black = monotonic() - start

    start = monotonic()
    unopposed_threats_black = chess_analysis.compute_unopposed_threats(threatened_pieces_black, guarded_pieces_black)
    t_unopposed_threats_black = monotonic() - start

    start = monotonic()
    unopposed_threats_count_black = len(unopposed_threats_black)
    t_unopposed_threats_count_black = monotonic() - start

    attackers_centipawn_white = chess_analysis.compute_pieces_centipawn_sum(board, attackers_white)
    start = monotonic()
    threatened_pieces_centipawn_white = chess_analysis.compute_pieces_centipawn_sum(board, threatened_pieces_white)
    t_threatened_pieces_centipawn_white = monotonic() - start
    guards_centipawn_white = chess_analysis.compute_pieces_centipawn_sum(board, guards_white)
    guarded_pieces_centipawn_white = chess_analysis.compute_pieces_centipawn_sum(board, guarded_pieces_white)
    threatened_guarded_pieces_centipawn_white = chess_analysis.compute_pieces_centipawn_sum(board,
                                                                                            threatened_guarded_pieces_white)
    unopposed_threats_centipawn_white = chess_analysis.compute_pieces_centipawn_sum(board, unopposed_threats_white)
    attackers_centipawn_black = chess_analysis.compute_pieces_centipawn_sum(board, attackers_black)
    threatened_pieces_centipawn_black = chess_analysis.compute_pieces_centipawn_sum(board, threatened_pieces_black)
    guards_centipawn_black = chess_analysis.compute_pieces_centipawn_sum(board, guards_black)
    guarded_pieces_centipawn_black = chess_analysis.compute_pieces_centipawn_sum(board, guarded_pieces_black)
    threatened_guarded_pieces_centipawn_black = chess_analysis.compute_pieces_centipawn_sum(board,
                                                                                            threatened_guarded_pieces_black)
    unopposed_threats_centipawn_black = chess_analysis.compute_pieces_centipawn_sum(board, unopposed_threats_black)

    start = monotonic()
    attack_defense_relation1 = chess_analysis.compute_attack_defense_relation_centipawn1(board)
    t_attack_defense_relation1 = monotonic() - start

    start = monotonic()
    attack_defense_relation2 = chess_analysis.compute_attack_defense_relation_centipawn2(guards_centipawn_white,
                                                                                         guarded_pieces_centipawn_white,
                                                                                         threatened_pieces_centipawn_white,
                                                                                         attackers_centipawn_white,
                                                                                         guards_centipawn_black,
                                                                                         guarded_pieces_centipawn_black,
                                                                                         threatened_pieces_centipawn_black,
                                                                                         attackers_centipawn_black)
    t_attack_defense_relation2 = monotonic() - start

    start = monotonic()
    pawn_ending = chess_analysis.pawn_ending(board.fen())
    t_pawn_ending = monotonic() - start

    start = monotonic()
    rook_ending = chess_analysis.rook_ending(board.fen())
    t_rook_ending = monotonic() - start

    board.pop()

    is_first_turn = len(best_moves_b) == 0

    for i, time in enumerate(times):
        print("Time: ", time)
        start = monotonic()
        best_move_scores = chess_analysis.compute_legal_move_scores(engine, board, time)

        if len(best_move_scores) > 1:
            best_move_scores.sort(key=lambda scores: scores[0], reverse=board.turn)
            best_move_score_a = best_move_scores[0][0]
            t_best_move_score_a = monotonic() - start

            start = monotonic()
            best_move_a = board.san(best_move_scores[0][1])
            t_best_move_a = monotonic() - start

            start = monotonic()
            best_move_score_diff_a = abs(best_move_scores[0][0] - score_a)
            t_best_move_score_diff_a = monotonic() - start

            start = monotonic()
            best_move_score_diff_category_a = chess_analysis.categorize_best_move_score_diff(best_move_score_diff_a,
                                                                                             best_move_a, san)
            t_best_move_score_diff_category_a = monotonic() - start
        else:
            best_move_a = "-"
            t_best_move_a = monotonic() - start
            best_move_score_a = 0
            best_move_score_diff_a = 0
            best_move_score_diff_category_a = -1

        best_moves_a.append(best_move_a)
        best_move_scores_a.append(best_move_score_a)
        best_move_score_diffs_a.append(best_move_score_diff_a)
        best_move_score_diff_categories_a.append(best_move_score_diff_category_a)
        t_best_moves_a.append(t_best_move_a)
        t_best_move_scores_a.append(t_best_move_score_a)
        t_best_move_score_diffs_a.append(t_best_move_score_diff_a)
        t_best_move_score_diff_categories_a.append(t_best_move_score_diff_category_a)

        if is_first_turn:
            start = monotonic()
            not_needed, best_move_b = chess_analysis.compute_score_alternative(engine, board, time)
            t_best_move_b = monotonic() - start
            best_moves_b.append(best_move_b)
        else:
            best_move_b = best_moves_b[i]

        start = monotonic()
        board.push(mv)
        score_b, next_best_move_b = chess_analysis.compute_score_alternative(engine, board, time)
        board.pop()
        t_score_b = monotonic() - start
        t_best_move_b = t_score_b

        start = monotonic()
        best_move_score_b = chess_analysis.compute_best_move_score_alternative(engine, board, best_move_b, time)
        t_best_move_score_b = monotonic() - start

        start = monotonic()
        best_move_score_diff_b = abs(best_move_score_b - score_b)
        t_best_move_score_diff_b = monotonic() - start

        start = monotonic()
        best_move_b = board.san(best_move_b)
        t_best_move_b = t_best_move_b + monotonic() - start

        start = monotonic()
        best_move_score_diff_category_b = chess_analysis.categorize_best_move_score_diff(best_move_score_diff_b,
                                                                                         best_move_b, san)
        t_best_move_score_diff_category_b = monotonic() - start

        scores_b.append(score_b)
        next_best_moves_b.append(next_best_move_b)
        best_move_scores_b.append(best_move_score_b)
        best_move_score_diffs_b.append(best_move_score_diff_b)
        best_move_score_diff_categories_b.append(best_move_score_diff_category_b)
        t_scores_b.append(t_score_b)
        t_best_moves_b.append(t_best_move_b)
        t_best_move_scores_b.append(t_best_move_score_b)
        t_best_move_score_diffs_b.append(t_best_move_score_diff_b)
        t_best_move_score_diff_categories_b.append(t_best_move_score_diff_category_b)

    for i, depth in enumerate(depths):
        print("Depth: ", depth)
        start = monotonic()
        best_move_scores = chess_analysis.compute_best_move_by_depth(engine, board, depth)

        if len(best_move_scores) > 1:
            best_move_scores.sort(key=lambda scores: scores[0], reverse=board.turn)
            best_move_score_a = best_move_scores[0][0]
            t_best_move_score_a = monotonic() - start

            start = monotonic()
            best_move_a = board.san(best_move_scores[0][1])
            t_best_move_a = monotonic() - start

            start = monotonic()
            best_move_score_diff_a = abs(best_move_scores[0][0] - score_a)
            t_best_move_score_diff_a = monotonic() - start

            start = monotonic()
            best_move_score_diff_category_a = chess_analysis.categorize_best_move_score_diff(best_move_score_diff_a,
                                                                                             best_move_a, san)
            t_best_move_score_diff_category_a = monotonic() - start
        else:
            best_move_a = "-"
            t_best_move_a = monotonic() - start
            best_move_score_a = 0
            best_move_score_diff_a = 0
            best_move_score_diff_category_a = -1

        best_moves_a.append(best_move_a)
        best_move_scores_a.append(best_move_score_a)
        best_move_score_diffs_a.append(best_move_score_diff_a)
        best_move_score_diff_categories_a.append(best_move_score_diff_category_a)
        t_best_moves_a.append(t_best_move_a)
        t_best_move_scores_a.append(t_best_move_score_a)
        t_best_move_score_diffs_a.append(t_best_move_score_diff_a)
        t_best_move_score_diff_categories_a.append(t_best_move_score_diff_category_a)

        if is_first_turn:
            start = monotonic()
            not_needed, best_move_b = chess_analysis.compute_score_alternative_by_depth(engine, board, depth)
            t_best_move_b = monotonic() - start
            best_moves_b.append(best_move_b)
        else:
            best_move_b = best_moves_b[len(times) + i]

        start = monotonic()
        board.push(mv)
        score_b, next_best_move_b = chess_analysis.compute_score_alternative_by_depth(engine, board, depth)
        board.pop()
        t_score_b = monotonic() - start
        t_best_move_b = t_score_b

        start = monotonic()
        best_move_score_b = chess_analysis.compute_best_move_score_alternative_by_depth(engine, board, best_move_b, depth)
        t_best_move_score_b = monotonic() - start

        start = monotonic()
        best_move_score_diff_b = abs(best_move_score_b - score_b)
        t_best_move_score_diff_b = monotonic() - start

        start = monotonic()
        best_move_b = board.san(best_move_b)
        t_best_move_b = t_best_move_b + monotonic() - start

        start = monotonic()
        best_move_score_diff_category_b = chess_analysis.categorize_best_move_score_diff(best_move_score_diff_b,
                                                                                         best_move_b, san)
        t_best_move_score_diff_category_b = monotonic() - start

        scores_b.append(score_b)
        next_best_moves_b.append(next_best_move_b)
        best_move_scores_b.append(best_move_score_b)
        best_move_score_diffs_b.append(best_move_score_diff_b)
        best_move_score_diff_categories_b.append(best_move_score_diff_category_b)
        t_scores_b.append(t_score_b)
        t_best_moves_b.append(t_best_move_b)
        t_best_move_scores_b.append(t_best_move_score_b)
        t_best_move_score_diffs_b.append(t_best_move_score_diff_b)
        t_best_move_score_diff_categories_b.append(t_best_move_score_diff_category_b)

    best_moves_b = [board.san(i) for i in best_moves_b]

    move_runtime = monotonic() - move_start_time
    print("Move runtime: ", move_runtime)
    db_timing_score = TimingScore(
        score_a0010=t_scores_a[0],
        score_a0020=t_scores_a[1],
        score_a0050=t_scores_a[2],
        score_a0100=t_scores_a[3],
        score_a0200=t_scores_a[4],
        score_a0500=t_scores_a[5],
        score_a1000=t_scores_a[6],
        score_a2000=t_scores_a[7],
        score_a5000=t_scores_a[8],
        score_a10=t_scores_a[9],
        score_a20=t_scores_a[10],
        best_move_a0010=t_best_moves_a[0],
        best_move_a0020=t_best_moves_a[1],
        best_move_a0050=t_best_moves_a[2],
        best_move_a0100=t_best_moves_a[3],
        best_move_a0200=t_best_moves_a[4],
        best_move_a0500=t_best_moves_a[5],
        best_move_a1000=t_best_moves_a[6],
        best_move_a2000=t_best_moves_a[7],
        best_move_a5000=t_best_moves_a[8],
        best_move_a10=t_best_moves_a[9],
        best_move_a20=t_best_moves_a[10],
        best_move_score_a0010=t_best_move_scores_a[0],
        best_move_score_a0020=t_best_move_scores_a[1],
        best_move_score_a0050=t_best_move_scores_a[2],
        best_move_score_a0100=t_best_move_scores_a[3],
        best_move_score_a0200=t_best_move_scores_a[4],
        best_move_score_a0500=t_best_move_scores_a[5],
        best_move_score_a1000=t_best_move_scores_a[6],
        best_move_score_a2000=t_best_move_scores_a[7],
        best_move_score_a5000=t_best_move_scores_a[8],
        best_move_score_a10=t_best_move_scores_a[9],
        best_move_score_a20=t_best_move_scores_a[10],
        best_move_score_diff_a0010=t_best_move_score_diffs_a[0],
        best_move_score_diff_a0020=t_best_move_score_diffs_a[1],
        best_move_score_diff_a0050=t_best_move_score_diffs_a[2],
        best_move_score_diff_a0100=t_best_move_score_diffs_a[3],
        best_move_score_diff_a0200=t_best_move_score_diffs_a[4],
        best_move_score_diff_a0500=t_best_move_score_diffs_a[5],
        best_move_score_diff_a1000=t_best_move_score_diffs_a[6],
        best_move_score_diff_a2000=t_best_move_score_diffs_a[7],
        best_move_score_diff_a5000=t_best_move_score_diffs_a[8],
        best_move_score_diff_a10=t_best_move_score_diffs_a[9],
        best_move_score_diff_a20=t_best_move_score_diffs_a[10],
        best_move_score_diff_category_a0010=t_best_move_score_diff_categories_a[0],
        best_move_score_diff_category_a0020=t_best_move_score_diff_categories_a[1],
        best_move_score_diff_category_a0050=t_best_move_score_diff_categories_a[2],
        best_move_score_diff_category_a0100=t_best_move_score_diff_categories_a[3],
        best_move_score_diff_category_a0200=t_best_move_score_diff_categories_a[4],
        best_move_score_diff_category_a0500=t_best_move_score_diff_categories_a[5],
        best_move_score_diff_category_a1000=t_best_move_score_diff_categories_a[6],
        best_move_score_diff_category_a2000=t_best_move_score_diff_categories_a[7],
        best_move_score_diff_category_a5000=t_best_move_score_diff_categories_a[8],
        best_move_score_diff_category_a10=t_best_move_score_diff_categories_a[9],
        best_move_score_diff_category_a20=t_best_move_score_diff_categories_a[10],

        score_b0010=t_scores_b[0],
        score_b0020=t_scores_b[1],
        score_b0050=t_scores_b[2],
        score_b0100=t_scores_b[3],
        score_b0200=t_scores_b[4],
        score_b0500=t_scores_b[5],
        score_b1000=t_scores_b[6],
        score_b2000=t_scores_b[7],
        score_b5000=t_scores_b[8],
        score_b10=t_scores_b[9],
        score_b20=t_scores_b[10],
        best_move_b0010=t_best_moves_b[0],
        best_move_b0020=t_best_moves_b[1],
        best_move_b0050=t_best_moves_b[2],
        best_move_b0100=t_best_moves_b[3],
        best_move_b0200=t_best_moves_b[4],
        best_move_b0500=t_best_moves_b[5],
        best_move_b1000=t_best_moves_b[6],
        best_move_b2000=t_best_moves_b[7],
        best_move_b5000=t_best_moves_b[8],
        best_move_b10=t_best_moves_b[9],
        best_move_b20=t_best_moves_b[10],
        best_move_score_b0010=t_best_move_scores_b[0],
        best_move_score_b0020=t_best_move_scores_b[1],
        best_move_score_b0050=t_best_move_scores_b[2],
        best_move_score_b0100=t_best_move_scores_b[3],
        best_move_score_b0200=t_best_move_scores_b[4],
        best_move_score_b0500=t_best_move_scores_b[5],
        best_move_score_b1000=t_best_move_scores_b[6],
        best_move_score_b2000=t_best_move_scores_b[7],
        best_move_score_b5000=t_best_move_scores_b[8],
        best_move_score_b10=t_best_move_scores_b[9],
        best_move_score_b20=t_best_move_scores_b[10],
        best_move_score_diff_b0010=t_best_move_score_diffs_b[0],
        best_move_score_diff_b0020=t_best_move_score_diffs_b[1],
        best_move_score_diff_b0050=t_best_move_score_diffs_b[2],
        best_move_score_diff_b0100=t_best_move_score_diffs_b[3],
        best_move_score_diff_b0200=t_best_move_score_diffs_b[4],
        best_move_score_diff_b0500=t_best_move_score_diffs_b[5],
        best_move_score_diff_b1000=t_best_move_score_diffs_b[6],
        best_move_score_diff_b2000=t_best_move_score_diffs_b[7],
        best_move_score_diff_b5000=t_best_move_score_diffs_b[8],
        best_move_score_diff_b10=t_best_move_score_diffs_b[9],
        best_move_score_diff_b20=t_best_move_score_diffs_b[10],
        best_move_score_diff_category_b0010=t_best_move_score_diff_categories_b[0],
        best_move_score_diff_category_b0020=t_best_move_score_diff_categories_b[1],
        best_move_score_diff_category_b0050=t_best_move_score_diff_categories_b[2],
        best_move_score_diff_category_b0100=t_best_move_score_diff_categories_b[3],
        best_move_score_diff_category_b0200=t_best_move_score_diff_categories_b[4],
        best_move_score_diff_category_b0500=t_best_move_score_diff_categories_b[5],
        best_move_score_diff_category_b1000=t_best_move_score_diff_categories_b[6],
        best_move_score_diff_category_b2000=t_best_move_score_diff_categories_b[7],
        best_move_score_diff_category_b5000=t_best_move_score_diff_categories_b[8],
        best_move_score_diff_category_b10=t_best_move_score_diff_categories_b[9],
        best_move_score_diff_category_b20=t_best_move_score_diff_categories_b[10],
    )

    db_score = Score(
        score_a0010=scores_a[0],
        score_a0020=scores_a[1],
        score_a0050=scores_a[2],
        score_a0100=scores_a[3],
        score_a0200=scores_a[4],
        score_a0500=scores_a[5],
        score_a1000=scores_a[6],
        score_a2000=scores_a[7],
        score_a5000=scores_a[8],
        score_a10=scores_a[9],
        score_a20=scores_a[10],
        best_move_a0010=best_moves_a[0],
        best_move_a0020=best_moves_a[1],
        best_move_a0050=best_moves_a[2],
        best_move_a0100=best_moves_a[3],
        best_move_a0200=best_moves_a[4],
        best_move_a0500=best_moves_a[5],
        best_move_a1000=best_moves_a[6],
        best_move_a2000=best_moves_a[7],
        best_move_a5000=best_moves_a[8],
        best_move_a10=best_moves_a[9],
        best_move_a20=best_moves_a[10],
        best_move_score_a0010=best_move_scores_a[0],
        best_move_score_a0020=best_move_scores_a[1],
        best_move_score_a0050=best_move_scores_a[2],
        best_move_score_a0100=best_move_scores_a[3],
        best_move_score_a0200=best_move_scores_a[4],
        best_move_score_a0500=best_move_scores_a[5],
        best_move_score_a1000=best_move_scores_a[6],
        best_move_score_a2000=best_move_scores_a[7],
        best_move_score_a5000=best_move_scores_a[8],
        best_move_score_a10=best_move_scores_a[9],
        best_move_score_a20=best_move_scores_a[10],
        best_move_score_diff_a0010=best_move_score_diffs_a[0],
        best_move_score_diff_a0020=best_move_score_diffs_a[1],
        best_move_score_diff_a0050=best_move_score_diffs_a[2],
        best_move_score_diff_a0100=best_move_score_diffs_a[3],
        best_move_score_diff_a0200=best_move_score_diffs_a[4],
        best_move_score_diff_a0500=best_move_score_diffs_a[5],
        best_move_score_diff_a1000=best_move_score_diffs_a[6],
        best_move_score_diff_a2000=best_move_score_diffs_a[7],
        best_move_score_diff_a5000=best_move_score_diffs_a[8],
        best_move_score_diff_a10=best_move_score_diffs_a[9],
        best_move_score_diff_a20=best_move_score_diffs_a[10],
        best_move_score_diff_category_a0010=best_move_score_diff_categories_a[0],
        best_move_score_diff_category_a0020=best_move_score_diff_categories_a[1],
        best_move_score_diff_category_a0050=best_move_score_diff_categories_a[2],
        best_move_score_diff_category_a0100=best_move_score_diff_categories_a[3],
        best_move_score_diff_category_a0200=best_move_score_diff_categories_a[4],
        best_move_score_diff_category_a0500=best_move_score_diff_categories_a[5],
        best_move_score_diff_category_a1000=best_move_score_diff_categories_a[6],
        best_move_score_diff_category_a2000=best_move_score_diff_categories_a[7],
        best_move_score_diff_category_a5000=best_move_score_diff_categories_a[8],
        best_move_score_diff_category_a10=best_move_score_diff_categories_a[9],
        best_move_score_diff_category_a20=best_move_score_diff_categories_a[10],

        score_b0010=scores_b[0],
        score_b0020=scores_b[1],
        score_b0050=scores_b[2],
        score_b0100=scores_b[3],
        score_b0200=scores_b[4],
        score_b0500=scores_b[5],
        score_b1000=scores_b[6],
        score_b2000=scores_b[7],
        score_b5000=scores_b[8],
        score_b10=scores_b[9],
        score_b20=scores_b[10],
        best_move_b0010=best_moves_b[0],
        best_move_b0020=best_moves_b[1],
        best_move_b0050=best_moves_b[2],
        best_move_b0100=best_moves_b[3],
        best_move_b0200=best_moves_b[4],
        best_move_b0500=best_moves_b[5],
        best_move_b1000=best_moves_b[6],
        best_move_b2000=best_moves_b[7],
        best_move_b5000=best_moves_b[8],
        best_move_b10=best_moves_b[9],
        best_move_b20=best_moves_b[10],
        best_move_score_b0010=best_move_scores_b[0],
        best_move_score_b0020=best_move_scores_b[1],
        best_move_score_b0050=best_move_scores_b[2],
        best_move_score_b0100=best_move_scores_b[3],
        best_move_score_b0200=best_move_scores_b[4],
        best_move_score_b0500=best_move_scores_b[5],
        best_move_score_b1000=best_move_scores_b[6],
        best_move_score_b2000=best_move_scores_b[7],
        best_move_score_b5000=best_move_scores_b[8],
        best_move_score_b10=best_move_scores_b[9],
        best_move_score_b20=best_move_scores_b[10],
        best_move_score_diff_b0010=best_move_score_diffs_b[0],
        best_move_score_diff_b0020=best_move_score_diffs_b[1],
        best_move_score_diff_b0050=best_move_score_diffs_b[2],
        best_move_score_diff_b0100=best_move_score_diffs_b[3],
        best_move_score_diff_b0200=best_move_score_diffs_b[4],
        best_move_score_diff_b0500=best_move_score_diffs_b[5],
        best_move_score_diff_b1000=best_move_score_diffs_b[6],
        best_move_score_diff_b2000=best_move_score_diffs_b[7],
        best_move_score_diff_b5000=best_move_score_diffs_b[8],
        best_move_score_diff_b10=best_move_score_diffs_b[9],
        best_move_score_diff_b20=best_move_score_diffs_b[10],
        best_move_score_diff_category_b0010=best_move_score_diff_categories_b[0],
        best_move_score_diff_category_b0020=best_move_score_diff_categories_b[1],
        best_move_score_diff_category_b0050=best_move_score_diff_categories_b[2],
        best_move_score_diff_category_b0100=best_move_score_diff_categories_b[3],
        best_move_score_diff_category_b0200=best_move_score_diff_categories_b[4],
        best_move_score_diff_category_b0500=best_move_score_diff_categories_b[5],
        best_move_score_diff_category_b1000=best_move_score_diff_categories_b[6],
        best_move_score_diff_category_b2000=best_move_score_diff_categories_b[7],
        best_move_score_diff_category_b5000=best_move_score_diff_categories_b[8],
        best_move_score_diff_category_b10=best_move_score_diff_categories_b[9],
        best_move_score_diff_category_b20=best_move_score_diff_categories_b[10],
        timing_score=db_timing_score
    )

    db_timing = Timing(
        fullmove_number=t_fullmove_number,
        turn=t_turn,
        san=t_san,
        lan=t_lan,
        score=t_scores_a[3],
        score_shift=t_score_shift,
        score_shift_category=t_score_shift_category,
        move_count=t_move_count,
        best_move=t_best_moves_a[3],
        best_move_score=t_best_move_scores_a[3],
        best_move_score_diff=t_best_move_score_diffs_a[3],
        best_move_score_diff_category=t_best_move_score_diff_categories_a[3],
        is_check=t_is_check,
        is_capture=t_is_capture,
        is_castling=t_is_castling,
        possible_moves_count=t_possible_moves_count,
        captures=t_captures,
        is_capture_count=t_is_capture_count,
        attackers_white=t_attackers_white,
        attackers_count_white=t_attackers_count_white,
        threatened_pieces_white=t_threatened_pieces_white,
        threatened_pieces_count_white=t_threatened_pieces_count_white,
        guards_white=t_guards_white,
        guards_count_white=t_guards_count_white,
        guarded_pieces_white=t_guarded_pieces_white,
        guarded_pieces_count_white=t_guarded_pieces_count_white,
        threatened_guarded_pieces_white=t_threatened_guarded_pieces_white,
        threatened_guarded_pieces_count_white=t_threatened_guarded_pieces_count_white,
        unopposed_threats_white=t_unopposed_threats_white,
        unopposed_threats_count_white=t_unopposed_threats_count_white,
        attackers_black=t_attackers_black,
        attackers_count_black=t_attackers_count_black,
        threatened_pieces_black=t_threatened_pieces_black,
        threatened_pieces_count_black=t_threatened_pieces_count_black,
        guards_black=t_guards_black,
        guards_count_black=t_guards_count_black,
        guarded_pieces_black=t_guarded_pieces_black,
        guarded_pieces_count_black=t_guarded_pieces_count_black,
        threatened_guarded_pieces_black=t_threatened_guarded_pieces_black,
        threatened_guarded_pieces_count_black=t_threatened_guarded_pieces_count_black,
        unopposed_threats_black=t_unopposed_threats_black,
        unopposed_threats_count_black=t_unopposed_threats_count_black,
        threatened_pieces_centipawn_white=t_threatened_pieces_centipawn_white,
        attack_defense_relation1=t_attack_defense_relation1,
        attack_defense_relation2=t_attack_defense_relation2,
        pawn_ending=t_pawn_ending,
        rook_ending=t_rook_ending,
        time=move_runtime
    )

    db_mv = Move(
        fullmove_number=fullmove_number,
        ply_number=ply_number,
        turn=turn,
        san=san,
        lan=lan,
        score=scores_a[3],
        score_shift=score_shift,
        score_shift_category=score_shift_category,
        move_count=move_count,
        best_move=best_moves_a[3],
        best_move_score=best_move_scores_a[3],
        best_move_score_diff=best_move_score_diffs_a[3],
        best_move_score_diff_category=best_move_score_diff_categories_a[3],
        is_check=is_check,
        is_capture=is_capture,
        is_castling=is_castling,
        possible_moves_count=possible_moves_count,
        captures=', '.join(str(s) for s in chess_analysis.get_square_names(captures)),
        is_capture_count=is_capture_count,
        attackers_white=', '.join(str(s) for s in chess_analysis.get_square_names(attackers_white)),
        attackers_count_white=attackers_count_white,
        threatened_pieces_white=', '.join(str(s) for s in chess_analysis.get_square_names(threatened_pieces_white)),
        threatened_pieces_count_white=threatened_pieces_count_white,
        guards_white=', '.join(str(s) for s in chess_analysis.get_square_names(guards_white)),
        guards_count_white=guards_count_white,
        guarded_pieces_white=', '.join(str(s) for s in chess_analysis.get_square_names(guarded_pieces_white)),
        guarded_pieces_count_white=guarded_pieces_count_white,
        threatened_guarded_pieces_white=', '.join(str(s) for s in chess_analysis.get_square_names(threatened_guarded_pieces_white)),
        threatened_guarded_pieces_count_white=threatened_guarded_pieces_count_white,
        unopposed_threats_white=', '.join(str(s) for s in chess_analysis.get_square_names(unopposed_threats_white)),
        unopposed_threats_count_white=unopposed_threats_count_white,
        attackers_black=', '.join(str(s) for s in chess_analysis.get_square_names(attackers_black)),
        attackers_count_black=attackers_count_black,
        threatened_pieces_black=', '.join(str(s) for s in chess_analysis.get_square_names(threatened_pieces_black)),
        threatened_pieces_count_black=threatened_pieces_count_black,
        guards_black=', '.join(str(s) for s in chess_analysis.get_square_names(guards_black)),
        guards_count_black=guards_count_black,
        guarded_pieces_black=', '.join(str(s) for s in chess_analysis.get_square_names(guarded_pieces_black)),
        guarded_pieces_count_black=guarded_pieces_count_black,
        threatened_guarded_pieces_black=', '.join(str(s) for s in chess_analysis.get_square_names(threatened_guarded_pieces_black)),
        threatened_guarded_pieces_count_black=threatened_guarded_pieces_count_black,
        unopposed_threats_black=', '.join(str(s) for s in chess_analysis.get_square_names(unopposed_threats_black)),
        unopposed_threats_count_black=unopposed_threats_count_black,
        attackers_centipawn_white=attackers_centipawn_white,
        threatened_pieces_centipawn_white=threatened_pieces_centipawn_white,
        guards_centipawn_white=guards_centipawn_white,
        guarded_pieces_centipawn_white=guarded_pieces_centipawn_white,
        threatened_guarded_pieces_centipawn_white=threatened_guarded_pieces_centipawn_white,
        unopposed_threats_centipawn_white=unopposed_threats_centipawn_white,
        attackers_centipawn_black=attackers_centipawn_black,
        threatened_pieces_centipawn_black=threatened_pieces_centipawn_black,
        guards_centipawn_black=guards_centipawn_black,
        guarded_pieces_centipawn_black=guarded_pieces_centipawn_black,
        threatened_guarded_pieces_centipawn_black=threatened_guarded_pieces_centipawn_black,
        unopposed_threats_centipawn_black=unopposed_threats_centipawn_black,
        attackers_count_all=attackers_count_white+attackers_count_black,
        threatened_pieces_count_all=threatened_pieces_count_white+threatened_pieces_count_black,
        guards_count_all=guards_count_white+guards_count_black,
        guarded_pieces_count_all=guarded_pieces_count_white+guarded_pieces_count_black,
        threatened_guarded_pieces_count_all=threatened_guarded_pieces_count_white+threatened_guarded_pieces_count_black,
        unopposed_threats_count_all=unopposed_threats_count_white+unopposed_threats_count_black,
        threatened_pieces_centipawn_all=threatened_pieces_centipawn_white+threatened_pieces_centipawn_black,
        guarded_pieces_centipawn_all=guarded_pieces_centipawn_white+guarded_pieces_centipawn_black,
        threatened_guarded_pieces_centipawn_all=threatened_guarded_pieces_centipawn_white+threatened_guarded_pieces_centipawn_black,
        unopposed_threats_centipawn_all=unopposed_threats_centipawn_white+unopposed_threats_centipawn_black,
        attack_defense_relation1=attack_defense_relation1,
        attack_defense_relation2=attack_defense_relation2,
        pawn_ending=pawn_ending,
        rook_ending=rook_ending,
        scores=db_score,
        timing=db_timing
    )

    return db_mv, next_best_moves_b


def compute_move_optimized(engine, board, mv, ply_number, time, prev_score, best_move):

    start = monotonic()
    fullmove_number = board.fullmove_number
    t_fullmove_number = monotonic() - start

    start = monotonic()
    turn = board.turn
    t_turn = monotonic() - start

    start = monotonic()
    san = board.san(mv)
    t_san = monotonic() - start

    start = monotonic()
    lan = board.lan(mv)
    t_lan = monotonic() - start

    start = monotonic()
    move_count = chess_analysis.compute_move_count(board)
    t_move_count = monotonic() - start

    start = monotonic()
    is_capture = board.is_capture(mv)
    t_is_capture = monotonic() - start

    start = monotonic()
    is_castling = board.is_castling(mv)
    t_is_castling = monotonic() - start

    if best_move is None: # calculate best move for first turn
        start = monotonic()
        not_needed, best_move = chess_analysis.compute_score_alternative(engine, board, time)
        t_best_move = monotonic() - start

    start = monotonic()
    board.push(mv)
    score, next_best_move = chess_analysis.compute_score_alternative(engine, board, time)
    board.pop()
    t_score = monotonic() - start
    t_best_move = t_score

    start = monotonic()
    score_shift = chess_analysis.compute_score_shift(prev_score, score)
    t_score_shift = monotonic() - start

    start = monotonic()
    score_shift_category = chess_analysis.compute_score_shift_category(score_shift)
    t_score_shift_category = monotonic() - start

    start = monotonic()
    best_move_score = chess_analysis.compute_best_move_score_alternative(engine, board, best_move, time)
    t_best_move_score = monotonic() - start

    start = monotonic()
    best_move_score_diff = abs(best_move_score - score)
    t_best_move_score_diff = monotonic() - start

    start = monotonic()
    best_move = board.san(best_move)
    t_best_move = t_best_move + monotonic() - start

    start = monotonic()
    best_move_score_diff_category = chess_analysis.categorize_best_move_score_diff(best_move_score_diff,
                                                                                   best_move, san)
    t_best_move_score_diff_category = monotonic() - start

    # apply move
    board.push(mv)

    start = monotonic()
    is_check = board.is_check()
    t_is_check = monotonic() - start

    start = monotonic()
    possible_moves_count = chess_analysis.compute_move_count(board)
    t_possible_moves_count = monotonic() - start

    start = monotonic()
    captures = chess_analysis.compute_possible_captures(board)
    captures = chess_analysis.compute_to_square_pieces(captures)
    t_captures = monotonic() - start

    start = monotonic()
    is_capture_count = len(captures)
    t_is_capture_count = monotonic() - start

    #White player
    start = monotonic()
    attack_moves_white = chess_analysis.compute_attack_moves(board, chess.BLACK)
    attackers_white = chess_analysis.compute_from_square_pieces(attack_moves_white)
    t_attackers_white = monotonic() - start

    start = monotonic()
    attackers_count_white = len(attackers_white)
    t_attackers_count_white = monotonic() - start

    start = monotonic()
    threatened_pieces_white = chess_analysis.compute_to_square_pieces(attack_moves_white)
    t_threatened_pieces_white = monotonic() - start

    start = monotonic()
    threatened_pieces_count_white = len(threatened_pieces_white)
    t_threatened_pieces_count_white = monotonic() - start

    start = monotonic()
    guard_moves_white = chess_analysis.compute_guard_moves_alt(board, chess.WHITE)
    guards_white = chess_analysis.compute_from_square_pieces(guard_moves_white)
    t_guards_white = monotonic() - start

    start = monotonic()
    guards_count_white = len(guards_white)
    t_guards_count_white = monotonic() - start

    start = monotonic()
    guarded_pieces_white = chess_analysis.compute_to_square_pieces(guard_moves_white)
    t_guarded_pieces_white = monotonic() - start

    start = monotonic()
    guarded_pieces_count_white = len(guarded_pieces_white)
    t_guarded_pieces_count_white = monotonic() - start

    start = monotonic()
    threatened_guarded_pieces_white = chess_analysis.compute_threatened_guarded_pieces(attack_moves_white, guard_moves_white)
    t_threatened_guarded_pieces_white = monotonic() - start

    start = monotonic()
    threatened_guarded_pieces_count_white = len(threatened_guarded_pieces_white)
    t_threatened_guarded_pieces_count_white = monotonic() - start

    start = monotonic()
    unopposed_threats_white = chess_analysis.compute_unopposed_threats(threatened_pieces_white, guarded_pieces_white)
    t_unopposed_threats_white = monotonic() - start

    start = monotonic()
    unopposed_threats_count_white = len(unopposed_threats_white)
    t_unopposed_threats_count_white = monotonic() - start

    # Black player
    start = monotonic()
    attack_moves_black = chess_analysis.compute_attack_moves(board, chess.WHITE)
    attackers_black = chess_analysis.compute_from_square_pieces(attack_moves_black)
    t_attackers_black = monotonic() - start

    start = monotonic()
    attackers_count_black = len(attackers_black)
    t_attackers_count_black = monotonic() - start

    start = monotonic()
    threatened_pieces_black = chess_analysis.compute_to_square_pieces(attack_moves_black)
    t_threatened_pieces_black = monotonic() - start

    start = monotonic()
    threatened_pieces_count_black = len(threatened_pieces_black)
    t_threatened_pieces_count_black = monotonic() - start

    start = monotonic()
    guard_moves_black = chess_analysis.compute_guard_moves_alt(board, chess.BLACK)
    guards_black = chess_analysis.compute_from_square_pieces(guard_moves_black)
    t_guards_black = monotonic() - start

    start = monotonic()
    guards_count_black = len(guards_black)
    t_guards_count_black = monotonic() - start

    start = monotonic()
    guarded_pieces_black = chess_analysis.compute_to_square_pieces(guard_moves_black)
    t_guarded_pieces_black = monotonic() - start

    start = monotonic()
    guarded_pieces_count_black = len(guarded_pieces_black)
    t_guarded_pieces_count_black = monotonic() - start

    start = monotonic()
    threatened_guarded_pieces_black = chess_analysis.compute_threatened_guarded_pieces(attack_moves_black, guard_moves_black)
    t_threatened_guarded_pieces_black = monotonic() - start

    start = monotonic()
    threatened_guarded_pieces_count_black = len(threatened_guarded_pieces_black)
    t_threatened_guarded_pieces_count_black = monotonic() - start

    start = monotonic()
    unopposed_threats_black = chess_analysis.compute_unopposed_threats(threatened_pieces_black, guarded_pieces_black)
    t_unopposed_threats_black = monotonic() - start

    start = monotonic()
    unopposed_threats_count_black = len(unopposed_threats_black)
    t_unopposed_threats_count_black = monotonic() - start

    attackers_centipawn_white = chess_analysis.compute_pieces_centipawn_sum(board, attackers_white)
    start = monotonic()
    threatened_pieces_centipawn_white = chess_analysis.compute_pieces_centipawn_sum(board, threatened_pieces_white)
    t_threatened_pieces_centipawn_white = monotonic() - start
    guards_centipawn_white = chess_analysis.compute_pieces_centipawn_sum(board, guards_white)
    guarded_pieces_centipawn_white = chess_analysis.compute_pieces_centipawn_sum(board, guarded_pieces_white)
    threatened_guarded_pieces_centipawn_white = chess_analysis.compute_pieces_centipawn_sum(board,
                                                                                            threatened_guarded_pieces_white)
    unopposed_threats_centipawn_white = chess_analysis.compute_pieces_centipawn_sum(board, unopposed_threats_white)
    attackers_centipawn_black = chess_analysis.compute_pieces_centipawn_sum(board, attackers_black)
    threatened_pieces_centipawn_black = chess_analysis.compute_pieces_centipawn_sum(board, threatened_pieces_black)
    guards_centipawn_black = chess_analysis.compute_pieces_centipawn_sum(board, guards_black)
    guarded_pieces_centipawn_black = chess_analysis.compute_pieces_centipawn_sum(board, guarded_pieces_black)
    threatened_guarded_pieces_centipawn_black = chess_analysis.compute_pieces_centipawn_sum(board,
                                                                                            threatened_guarded_pieces_black)
    unopposed_threats_centipawn_black = chess_analysis.compute_pieces_centipawn_sum(board, unopposed_threats_black)

    start = monotonic()
    attack_defense_relation1 = chess_analysis.compute_attack_defense_relation_centipawn1(board)
    t_attack_defense_relation1 = monotonic() - start

    start = monotonic()
    attack_defense_relation2 = chess_analysis.compute_attack_defense_relation_centipawn2(guards_centipawn_white,
                                                                                         guarded_pieces_centipawn_white,
                                                                                         threatened_pieces_centipawn_white,
                                                                                         attackers_centipawn_white,
                                                                                         guards_centipawn_black,
                                                                                         guarded_pieces_centipawn_black,
                                                                                         threatened_pieces_centipawn_black,
                                                                                         attackers_centipawn_black)
    t_attack_defense_relation2 = monotonic() - start
    start = monotonic()
    pawn_ending = chess_analysis.pawn_ending(board.fen())
    t_pawn_ending = monotonic() - start

    start = monotonic()
    rook_ending = chess_analysis.rook_ending(board.fen())
    t_rook_ending = monotonic() - start

    board.pop()

    db_timing = Timing(
        fullmove_number=t_fullmove_number,
        turn=t_turn,
        san=t_san,
        lan=t_lan,
        score=t_score,
        score_shift=t_score_shift,
        score_shift_category=t_score_shift_category,
        move_count=t_move_count,
        best_move=t_best_move,
        best_move_score=t_best_move_score,
        best_move_score_diff=t_best_move_score_diff,
        best_move_score_diff_category=t_best_move_score_diff_category,
        is_check=t_is_check,
        is_capture=t_is_capture,
        is_castling=t_is_castling,
        possible_moves_count=t_possible_moves_count,
        captures=t_captures,
        is_capture_count=t_is_capture_count,
        attackers_white=t_attackers_white,
        attackers_count_white=t_attackers_count_white,
        threatened_pieces_white=t_threatened_pieces_white,
        threatened_pieces_count_white=t_threatened_pieces_count_white,
        guards_white=t_guards_white,
        guards_count_white=t_guards_count_white,
        guarded_pieces_white=t_guarded_pieces_white,
        guarded_pieces_count_white=t_guarded_pieces_count_white,
        threatened_guarded_pieces_white=t_threatened_guarded_pieces_white,
        threatened_guarded_pieces_count_white=t_threatened_guarded_pieces_count_white,
        unopposed_threats_white=t_unopposed_threats_white,
        unopposed_threats_count_white=t_unopposed_threats_count_white,
        attackers_black=t_attackers_black,
        attackers_count_black=t_attackers_count_black,
        threatened_pieces_black=t_threatened_pieces_black,
        threatened_pieces_count_black=t_threatened_pieces_count_black,
        guards_black=t_guards_black,
        guards_count_black=t_guards_count_black,
        guarded_pieces_black=t_guarded_pieces_black,
        guarded_pieces_count_black=t_guarded_pieces_count_black,
        threatened_guarded_pieces_black=t_threatened_guarded_pieces_black,
        threatened_guarded_pieces_count_black=t_threatened_guarded_pieces_count_black,
        unopposed_threats_black=t_unopposed_threats_black,
        unopposed_threats_count_black=t_unopposed_threats_count_black,
        threatened_pieces_centipawn_white=t_threatened_pieces_centipawn_white,
        attack_defense_relation1=t_attack_defense_relation1,
        attack_defense_relation2=t_attack_defense_relation2,
        pawn_ending=t_pawn_ending,
        rook_ending=t_rook_ending,
    )

    db_mv = Move(
        fullmove_number=fullmove_number,
        ply_number=ply_number,
        turn=turn,
        san=san,
        lan=lan,
        score=score,
        score_shift=score_shift,
        score_shift_category=score_shift_category,
        move_count=move_count,
        best_move=best_move,
        best_move_score=best_move_score,
        best_move_score_diff=best_move_score_diff,
        best_move_score_diff_category=best_move_score_diff_category,
        is_check=is_check,
        is_capture=is_capture,
        is_castling=is_castling,
        possible_moves_count=possible_moves_count,
        captures=', '.join(str(s) for s in chess_analysis.get_square_names(captures)),
        is_capture_count=is_capture_count,
        attackers_white=', '.join(str(s) for s in chess_analysis.get_square_names(attackers_white)),
        attackers_count_white=attackers_count_white,
        threatened_pieces_white=', '.join(str(s) for s in chess_analysis.get_square_names(threatened_pieces_white)),
        threatened_pieces_count_white=threatened_pieces_count_white,
        guards_white=', '.join(str(s) for s in chess_analysis.get_square_names(guards_white)),
        guards_count_white=guards_count_white,
        guarded_pieces_white=', '.join(str(s) for s in chess_analysis.get_square_names(guarded_pieces_white)),
        guarded_pieces_count_white=guarded_pieces_count_white,
        threatened_guarded_pieces_white=', '.join(str(s) for s in chess_analysis.get_square_names(threatened_guarded_pieces_white)),
        threatened_guarded_pieces_count_white=threatened_guarded_pieces_count_white,
        unopposed_threats_white=', '.join(str(s) for s in chess_analysis.get_square_names(unopposed_threats_white)),
        unopposed_threats_count_white=unopposed_threats_count_white,
        attackers_black=', '.join(str(s) for s in chess_analysis.get_square_names(attackers_black)),
        attackers_count_black=attackers_count_black,
        threatened_pieces_black=', '.join(str(s) for s in chess_analysis.get_square_names(threatened_pieces_black)),
        threatened_pieces_count_black=threatened_pieces_count_black,
        guards_black=', '.join(str(s) for s in chess_analysis.get_square_names(guards_black)),
        guards_count_black=guards_count_black,
        guarded_pieces_black=', '.join(str(s) for s in chess_analysis.get_square_names(guarded_pieces_black)),
        guarded_pieces_count_black=guarded_pieces_count_black,
        threatened_guarded_pieces_black=', '.join(str(s) for s in chess_analysis.get_square_names(threatened_guarded_pieces_black)),
        threatened_guarded_pieces_count_black=threatened_guarded_pieces_count_black,
        unopposed_threats_black=', '.join(str(s) for s in chess_analysis.get_square_names(unopposed_threats_black)),
        unopposed_threats_count_black=unopposed_threats_count_black,
        attackers_centipawn_white=attackers_centipawn_white,
        threatened_pieces_centipawn_white=threatened_pieces_centipawn_white,
        guards_centipawn_white=guards_centipawn_white,
        guarded_pieces_centipawn_white=guarded_pieces_centipawn_white,
        threatened_guarded_pieces_centipawn_white=threatened_guarded_pieces_centipawn_white,
        unopposed_threats_centipawn_white=unopposed_threats_centipawn_white,
        attackers_centipawn_black=attackers_centipawn_black,
        threatened_pieces_centipawn_black=threatened_pieces_centipawn_black,
        guards_centipawn_black=guards_centipawn_black,
        guarded_pieces_centipawn_black=guarded_pieces_centipawn_black,
        threatened_guarded_pieces_centipawn_black=threatened_guarded_pieces_centipawn_black,
        unopposed_threats_centipawn_black=unopposed_threats_centipawn_black,
        attackers_count_all=attackers_count_white + attackers_count_black,
        threatened_pieces_count_all=threatened_pieces_count_white + threatened_pieces_count_black,
        guards_count_all=guards_count_white + guards_count_black,
        guarded_pieces_count_all=guarded_pieces_count_white + guarded_pieces_count_black,
        threatened_guarded_pieces_count_all=threatened_guarded_pieces_count_white + threatened_guarded_pieces_count_black,
        unopposed_threats_count_all=unopposed_threats_count_white + unopposed_threats_count_black,
        threatened_pieces_centipawn_all=threatened_pieces_centipawn_white + threatened_pieces_centipawn_black,
        guarded_pieces_centipawn_all=guarded_pieces_centipawn_white + guarded_pieces_centipawn_black,
        threatened_guarded_pieces_centipawn_all=threatened_guarded_pieces_centipawn_white + threatened_guarded_pieces_centipawn_black,
        unopposed_threats_centipawn_all=unopposed_threats_centipawn_white + unopposed_threats_centipawn_black,
        attack_defense_relation1=attack_defense_relation1,
        attack_defense_relation2=attack_defense_relation2,
        pawn_ending=pawn_ending,
        rook_ending=rook_ending,
        timing=db_timing
    )

    return db_mv, next_best_move

