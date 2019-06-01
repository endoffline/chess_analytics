SELECT score_a0100, score_b0100, best_move_score_a0100, min(best_move_score_a0100), max(best_move_score_a0100), best_move_score_b0100, min(best_move_score_b0100), max(best_move_score_b0100) FROM timing_score;
SELECT COUNT(*) FROM score WHERE best_move_a0100 == best_move_b0100;
SELECT COUNT(*) FROM score WHERE best_move_a1000 == best_move_b1000;
SELECT COUNT(*) FROM score WHERE best_move_a5000 == best_move_b5000;
SELECT COUNT(*) FROM score WHERE best_move_score_a5000 == best_move_score_b5000;
SELECT avg(score_a5000), avg(score_b5000), avg(best_move_score_a5000), min(best_move_score_a5000), max(best_move_score_a5000), avg(best_move_score_b5000), min(best_move_score_b5000), max(best_move_score_b5000) FROM timing_score;
SELECT avg(abs(best_move_score_a0100 - best_move_score_b0100)), avg(abs(best_move_score_a1000 - best_move_score_b1000)), avg(abs(best_move_score_a5000 - best_move_score_b5000)) FROM score;
SELECT COUNT(*) FROM score;

SELECT fullmove_number, turn, san, lan, score, move_count, best_move, best_move_score, best_move_score_diff, best_move_score_diff_category, is_check, is_capture, is_castling, possible_moves_count, is_capture_count, attackers, attackers_count, threatened_pieces, threatened_pieces_count, guards, guards_count, guarded_pieces, guarded_pieces_count, threatened_guarded_pieces, threatened_guarded_pieces_count, unopposed_threats, unopposed_threats_count FROM move WHERE game_id = 1;