import chess
import chess_analysis
from models.move import Move
from models.score import Score
from models.timing import Timing
from models.timing_score import TimingScore
from time import monotonic

# time = 0.100
# times = [0.010, 0.020, 0.050, 0.100, 0.200, 0.500, 1.000, 2.000, 5.000]
times = [0.010, 0.020, 0.050, 0.100, 0.001, 0.001, 0.001, 0.001, 0.001]
times = [0.001, 0.001, 0.001, 0.100, 0.001, 0.001, 0.001, 0.001, 0.001]


def compute_move(engine, board, mv):
    scores_a, best_moves_a, best_move_scores_a, best_move_score_diffs_a, best_move_score_diff_categories_a = [], [], [], [], []
    scores_b, best_moves_b, best_move_scores_b, best_move_score_diffs_b, best_move_score_diff_categories_b = [], [], [], [], []
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

    start = monotonic()
    is_check = board.is_check()
    t_is_check = monotonic() - start

    start = monotonic()
    pawn_ending = chess_analysis.pawn_ending(board.fen())
    t_pawn_ending = monotonic() - start

    start = monotonic()
    rook_ending = chess_analysis.rook_ending(board.fen())
    t_rook_ending = monotonic() - start

    start = monotonic()
    attack_moves = chess_analysis.compute_attack_moves(board, chess.BLACK)
    attackers = chess_analysis.compute_from_square_pieces(attack_moves)
    t_attackers = monotonic() - start

    start = monotonic()
    attackers_count = len(attackers)
    t_attackers_count = monotonic() - start

    start = monotonic()
    threatened_pieces = chess_analysis.compute_to_square_pieces(attack_moves)
    t_threatened_pieces = monotonic() - start

    start = monotonic()
    threatened_pieces_count = len(threatened_pieces)
    t_threatened_pieces_count = monotonic() - start

    start = monotonic()
    captures = chess_analysis.compute_captures(board)
    t_captures = monotonic() - start

    start = monotonic()
    is_capture_count = len(captures)
    t_is_capture_count = monotonic() - start

    start = monotonic()
    guard_moves = chess_analysis.compute_guard_moves(board, chess.WHITE)
    guards = chess_analysis.compute_from_square_pieces(guard_moves)
    t_guards = monotonic() - start

    start = monotonic()
    guards_count = len(guards)
    t_guards_count = monotonic() - start

    start = monotonic()
    guarded_pieces = chess_analysis.compute_to_square_pieces(guard_moves)
    t_guarded_pieces = monotonic() - start

    start = monotonic()
    guarded_pieces_count = len(guarded_pieces)
    t_guarded_pieces_count = monotonic() - start

    start = monotonic()
    threatened_guarded_pieces = chess_analysis.compute_threatened_guarded_pieces(attack_moves, guard_moves)
    t_threatened_guarded_pieces = monotonic() - start

    start = monotonic()
    threatened_guarded_pieces_count = len(threatened_guarded_pieces)
    t_threatened_guarded_pieces_count = monotonic() - start

    start = monotonic()
    unopposed_threats = chess_analysis.compute_unopposed_threats(threatened_pieces, guarded_pieces)
    t_unopposed_threats = monotonic() - start

    start = monotonic()
    unopposed_threats_count = len(unopposed_threats)
    t_unopposed_threats_count = monotonic() - start

    start = monotonic()
    possible_moves_count = chess_analysis.compute_move_count(board)
    t_possible_moves_count = monotonic() - start

    board.pop()

    for time in times:
        print("Time: %d", time)
        start = monotonic()
        best_move_scores = chess_analysis.compute_best_move(engine, board, time)

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

        start = monotonic()
        score_b, best_move_b = chess_analysis.compute_score_alternative(engine, board, time)
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
        best_moves_b.append(best_move_b)
        best_move_scores_b.append(best_move_score_b)
        best_move_score_diffs_b.append(best_move_score_diff_b)
        best_move_score_diff_categories_b.append(best_move_score_diff_category_b)
        t_scores_b.append(t_score_b)
        t_best_moves_b.append(t_best_move_b)
        t_best_move_scores_b.append(t_best_move_score_b)
        t_best_move_score_diffs_b.append(t_best_move_score_diff_b)
        t_best_move_score_diff_categories_b.append(t_best_move_score_diff_category_b)

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
        best_move_a0010=t_best_moves_a[0],
        best_move_a0020=t_best_moves_a[1],
        best_move_a0050=t_best_moves_a[2],
        best_move_a0100=t_best_moves_a[3],
        best_move_a0200=t_best_moves_a[4],
        best_move_a0500=t_best_moves_a[5],
        best_move_a1000=t_best_moves_a[6],
        best_move_a2000=t_best_moves_a[7],
        best_move_a5000=t_best_moves_a[8],
        best_move_score_a0010=t_best_move_scores_a[0],
        best_move_score_a0020=t_best_move_scores_a[1],
        best_move_score_a0050=t_best_move_scores_a[2],
        best_move_score_a0100=t_best_move_scores_a[3],
        best_move_score_a0200=t_best_move_scores_a[4],
        best_move_score_a0500=t_best_move_scores_a[5],
        best_move_score_a1000=t_best_move_scores_a[6],
        best_move_score_a2000=t_best_move_scores_a[7],
        best_move_score_a5000=t_best_move_scores_a[8],
        best_move_score_diff_a0010=t_best_move_score_diffs_a[0],
        best_move_score_diff_a0020=t_best_move_score_diffs_a[1],
        best_move_score_diff_a0050=t_best_move_score_diffs_a[2],
        best_move_score_diff_a0100=t_best_move_score_diffs_a[3],
        best_move_score_diff_a0200=t_best_move_score_diffs_a[4],
        best_move_score_diff_a0500=t_best_move_score_diffs_a[5],
        best_move_score_diff_a1000=t_best_move_score_diffs_a[6],
        best_move_score_diff_a2000=t_best_move_score_diffs_a[7],
        best_move_score_diff_a5000=t_best_move_score_diffs_a[8],
        best_move_score_diff_category_a0010=t_best_move_score_diff_categories_a[0],
        best_move_score_diff_category_a0020=t_best_move_score_diff_categories_a[1],
        best_move_score_diff_category_a0050=t_best_move_score_diff_categories_a[2],
        best_move_score_diff_category_a0100=t_best_move_score_diff_categories_a[3],
        best_move_score_diff_category_a0200=t_best_move_score_diff_categories_a[4],
        best_move_score_diff_category_a0500=t_best_move_score_diff_categories_a[5],
        best_move_score_diff_category_a1000=t_best_move_score_diff_categories_a[6],
        best_move_score_diff_category_a2000=t_best_move_score_diff_categories_a[7],
        best_move_score_diff_category_a5000=t_best_move_score_diff_categories_a[8],

        score_b0010=t_scores_b[0],
        score_b0020=t_scores_b[1],
        score_b0050=t_scores_b[2],
        score_b0100=t_scores_b[3],
        score_b0200=t_scores_b[4],
        score_b0500=t_scores_b[5],
        score_b1000=t_scores_b[6],
        score_b2000=t_scores_b[7],
        score_b5000=t_scores_b[8],
        best_move_b0010=t_best_moves_b[0],
        best_move_b0020=t_best_moves_b[1],
        best_move_b0050=t_best_moves_b[2],
        best_move_b0100=t_best_moves_b[3],
        best_move_b0200=t_best_moves_b[4],
        best_move_b0500=t_best_moves_b[5],
        best_move_b1000=t_best_moves_b[6],
        best_move_b2000=t_best_moves_b[7],
        best_move_b5000=t_best_moves_b[8],
        best_move_score_b0010=t_best_move_scores_b[0],
        best_move_score_b0020=t_best_move_scores_b[1],
        best_move_score_b0050=t_best_move_scores_b[2],
        best_move_score_b0100=t_best_move_scores_b[3],
        best_move_score_b0200=t_best_move_scores_b[4],
        best_move_score_b0500=t_best_move_scores_b[5],
        best_move_score_b1000=t_best_move_scores_b[6],
        best_move_score_b2000=t_best_move_scores_b[7],
        best_move_score_b5000=t_best_move_scores_b[8],
        best_move_score_diff_b0010=t_best_move_score_diffs_b[0],
        best_move_score_diff_b0020=t_best_move_score_diffs_b[1],
        best_move_score_diff_b0050=t_best_move_score_diffs_b[2],
        best_move_score_diff_b0100=t_best_move_score_diffs_b[3],
        best_move_score_diff_b0200=t_best_move_score_diffs_b[4],
        best_move_score_diff_b0500=t_best_move_score_diffs_b[5],
        best_move_score_diff_b1000=t_best_move_score_diffs_b[6],
        best_move_score_diff_b2000=t_best_move_score_diffs_b[7],
        best_move_score_diff_b5000=t_best_move_score_diffs_b[8],
        best_move_score_diff_category_b0010=t_best_move_score_diff_categories_b[0],
        best_move_score_diff_category_b0020=t_best_move_score_diff_categories_b[1],
        best_move_score_diff_category_b0050=t_best_move_score_diff_categories_b[2],
        best_move_score_diff_category_b0100=t_best_move_score_diff_categories_b[3],
        best_move_score_diff_category_b0200=t_best_move_score_diff_categories_b[4],
        best_move_score_diff_category_b0500=t_best_move_score_diff_categories_b[5],
        best_move_score_diff_category_b1000=t_best_move_score_diff_categories_b[6],
        best_move_score_diff_category_b2000=t_best_move_score_diff_categories_b[7],
        best_move_score_diff_category_b5000=t_best_move_score_diff_categories_b[8],
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
        best_move_a0010=best_moves_a[0],
        best_move_a0020=best_moves_a[1],
        best_move_a0050=best_moves_a[2],
        best_move_a0100=best_moves_a[3],
        best_move_a0200=best_moves_a[4],
        best_move_a0500=best_moves_a[5],
        best_move_a1000=best_moves_a[6],
        best_move_a2000=best_moves_a[7],
        best_move_a5000=best_moves_a[8],
        best_move_score_a0010=best_move_scores_a[0],
        best_move_score_a0020=best_move_scores_a[1],
        best_move_score_a0050=best_move_scores_a[2],
        best_move_score_a0100=best_move_scores_a[3],
        best_move_score_a0200=best_move_scores_a[4],
        best_move_score_a0500=best_move_scores_a[5],
        best_move_score_a1000=best_move_scores_a[6],
        best_move_score_a2000=best_move_scores_a[7],
        best_move_score_a5000=best_move_scores_a[8],
        best_move_score_diff_a0010=best_move_score_diffs_a[0],
        best_move_score_diff_a0020=best_move_score_diffs_a[1],
        best_move_score_diff_a0050=best_move_score_diffs_a[2],
        best_move_score_diff_a0100=best_move_score_diffs_a[3],
        best_move_score_diff_a0200=best_move_score_diffs_a[4],
        best_move_score_diff_a0500=best_move_score_diffs_a[5],
        best_move_score_diff_a1000=best_move_score_diffs_a[6],
        best_move_score_diff_a2000=best_move_score_diffs_a[7],
        best_move_score_diff_a5000=best_move_score_diffs_a[8],
        best_move_score_diff_category_a0010=best_move_score_diff_categories_a[0],
        best_move_score_diff_category_a0020=best_move_score_diff_categories_a[1],
        best_move_score_diff_category_a0050=best_move_score_diff_categories_a[2],
        best_move_score_diff_category_a0100=best_move_score_diff_categories_a[3],
        best_move_score_diff_category_a0200=best_move_score_diff_categories_a[4],
        best_move_score_diff_category_a0500=best_move_score_diff_categories_a[5],
        best_move_score_diff_category_a1000=best_move_score_diff_categories_a[6],
        best_move_score_diff_category_a2000=best_move_score_diff_categories_a[7],
        best_move_score_diff_category_a5000=best_move_score_diff_categories_a[8],

        score_b0010=scores_b[0],
        score_b0020=scores_b[1],
        score_b0050=scores_b[2],
        score_b0100=scores_b[3],
        score_b0200=scores_b[4],
        score_b0500=scores_b[5],
        score_b1000=scores_b[6],
        score_b2000=scores_b[7],
        score_b5000=scores_b[8],
        best_move_b0010=best_moves_b[0],
        best_move_b0020=best_moves_b[1],
        best_move_b0050=best_moves_b[2],
        best_move_b0100=best_moves_b[3],
        best_move_b0200=best_moves_b[4],
        best_move_b0500=best_moves_b[5],
        best_move_b1000=best_moves_b[6],
        best_move_b2000=best_moves_b[7],
        best_move_b5000=best_moves_b[8],
        best_move_score_b0010=best_move_scores_b[0],
        best_move_score_b0020=best_move_scores_b[1],
        best_move_score_b0050=best_move_scores_b[2],
        best_move_score_b0100=best_move_scores_b[3],
        best_move_score_b0200=best_move_scores_b[4],
        best_move_score_b0500=best_move_scores_b[5],
        best_move_score_b1000=best_move_scores_b[6],
        best_move_score_b2000=best_move_scores_b[7],
        best_move_score_b5000=best_move_scores_b[8],
        best_move_score_diff_b0010=best_move_score_diffs_b[0],
        best_move_score_diff_b0020=best_move_score_diffs_b[1],
        best_move_score_diff_b0050=best_move_score_diffs_b[2],
        best_move_score_diff_b0100=best_move_score_diffs_b[3],
        best_move_score_diff_b0200=best_move_score_diffs_b[4],
        best_move_score_diff_b0500=best_move_score_diffs_b[5],
        best_move_score_diff_b1000=best_move_score_diffs_b[6],
        best_move_score_diff_b2000=best_move_score_diffs_b[7],
        best_move_score_diff_b5000=best_move_score_diffs_b[8],
        best_move_score_diff_category_b0010=best_move_score_diff_categories_b[0],
        best_move_score_diff_category_b0020=best_move_score_diff_categories_b[1],
        best_move_score_diff_category_b0050=best_move_score_diff_categories_b[2],
        best_move_score_diff_category_b0100=best_move_score_diff_categories_b[3],
        best_move_score_diff_category_b0200=best_move_score_diff_categories_b[4],
        best_move_score_diff_category_b0500=best_move_score_diff_categories_b[5],
        best_move_score_diff_category_b1000=best_move_score_diff_categories_b[6],
        best_move_score_diff_category_b2000=best_move_score_diff_categories_b[7],
        best_move_score_diff_category_b5000=best_move_score_diff_categories_b[8],
        timing_score=db_timing_score
    )

    db_timing = Timing(
        fullmove_number=t_fullmove_number,
        turn=t_turn,
        san=t_san,
        lan=t_lan,
        score=t_scores_a[3],
        move_count=t_move_count,
        best_move=t_best_moves_a[3],
        best_move_score=t_best_move_scores_a[3],
        best_move_score_diff=t_best_move_score_diffs_a[3],
        best_move_score_diff_category=t_best_move_score_diff_categories_a[3],
        is_check=t_is_check,
        is_capture=t_is_capture,
        is_castling=t_is_castling,
        possible_moves_count=t_possible_moves_count,
        is_capture_count=t_is_capture_count,
        attackers=t_attackers,
        attackers_count=t_attackers_count,
        threatened_pieces=t_threatened_pieces,
        threatened_pieces_count=t_threatened_pieces_count,
        guards=t_guards,
        guards_count=t_guards_count,
        guarded_pieces=t_guarded_pieces,
        guarded_pieces_count=t_guarded_pieces_count,
        threatened_guarded_pieces=t_threatened_guarded_pieces,
        threatened_guarded_pieces_count=t_threatened_guarded_pieces_count,
        unopposed_threats=t_unopposed_threats,
        unopposed_threats_count=t_unopposed_threats_count,
        pawn_ending=t_pawn_ending,
        rook_ending=t_rook_ending,
    )

    db_mv = Move(
        fullmove_number=fullmove_number,
        turn=turn,
        san=san,
        lan=lan,
        score=scores_a[3],
        move_count=move_count,
        best_move=best_moves_a[3],
        best_move_score=best_move_scores_a[3],
        best_move_score_diff=best_move_score_diffs_a[3],
        best_move_score_diff_category=best_move_score_diff_categories_a[3],
        is_check=is_check,
        is_capture=is_capture,
        is_castling=is_castling,
        possible_moves_count=possible_moves_count,
        is_capture_count=is_capture_count,
        attackers=', '.join(str(s) for s in chess_analysis.get_square_names(attackers)),
        attackers_count=attackers_count,
        threatened_pieces=', '.join(str(s) for s in chess_analysis.get_square_names(threatened_pieces)),
        threatened_pieces_count=threatened_pieces_count,
        guards=', '.join(str(s) for s in chess_analysis.get_square_names(guards)),
        guards_count=guards_count,
        guarded_pieces=', '.join(str(s) for s in chess_analysis.get_square_names(guarded_pieces)),
        guarded_pieces_count=guarded_pieces_count,
        threatened_guarded_pieces=', '.join(str(s) for s in chess_analysis.get_square_names(threatened_guarded_pieces)),
        threatened_guarded_pieces_count=threatened_guarded_pieces_count,
        unopposed_threats=', '.join(str(s) for s in chess_analysis.get_square_names(unopposed_threats)),
        unopposed_threats_count=unopposed_threats_count,
        pawn_ending=pawn_ending,
        rook_ending=rook_ending,
        scores=db_score,
        timing=db_timing
    )

    return db_mv

