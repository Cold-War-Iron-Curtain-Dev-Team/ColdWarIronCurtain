
	if = {
		limit = { check_variable = { xiangqi_Government_Chariot_piece_alive = 1 } }
		hidden_effect = { xiangqi_clear_legal_moves = yes }

		# Cache origin
		set_variable = { xiangqi_tmp_origin_row = ROOT.xiangqi_Government_Chariot_piece_row }
		set_variable = { xiangqi_tmp_origin_col = ROOT.xiangqi_Government_Chariot_piece_col }

		# =====================
		# RIGHT (row + 1, +2, ...)
		# =====================
		set_variable = { xiangqi_tmp_iter = 1 }

		while_loop_effect = {
			limit = {
				check_variable = { xiangqi_tmp_iter < 10 } # safety cap
			}

			# Compute target square
			set_variable = { xiangqi_tmp_target_row = ROOT.xiangqi_tmp_origin_row }
			add_to_variable = { xiangqi_tmp_target_row = ROOT.xiangqi_tmp_iter }
			set_variable = { xiangqi_tmp_target_col = ROOT.xiangqi_tmp_origin_col }

			# Stop if off board
			if = {
				limit = {
					OR = {
						check_variable = { xiangqi_tmp_target_row < 1 }
						check_variable = { xiangqi_tmp_target_row > 9 }
					}
				}
				break = yes
			}

			# Set square to check
			set_variable = { xiangqi_tmp_check_row = ROOT.xiangqi_tmp_target_row }
			set_variable = { xiangqi_tmp_check_col = ROOT.xiangqi_tmp_target_col }

			# Legal move if not friendly-occupied
			if = {
				limit = {
					NOT = { xiangqi_is_square_occupied_by_friendly_government = yes }
				}
				hidden_effect = { xiangqi_add_legal_move = yes }
			}

			# Stop ray if ANY piece blocks
			if = {
				limit = { xiangqi_is_square_occupied = yes }
				break = yes
			}

			# Next square
			add_to_variable = { xiangqi_tmp_iter = 1 }
		}
		# =====================
		# LEFT (row -1, -2, ...)
		# =====================
		set_variable = { xiangqi_tmp_iter = 1 }

		while_loop_effect = {
			limit = {
				check_variable = { xiangqi_tmp_iter > 0 } # safety cap
			}

			# Compute target square
			set_variable = { xiangqi_tmp_target_row = ROOT.xiangqi_tmp_origin_row }
			add_to_variable = { xiangqi_tmp_target_row = ROOT.xiangqi_tmp_iter }
			set_variable = { xiangqi_tmp_target_col = ROOT.xiangqi_tmp_origin_col }

			# Stop if off board
			if = {
				limit = {
					OR = {
						check_variable = { xiangqi_tmp_target_row < 1 }
						check_variable = { xiangqi_tmp_target_row > 9 }
					}
				}
				break = yes
			}

			# Set square to check
			set_variable = { xiangqi_tmp_check_row = ROOT.xiangqi_tmp_target_row }
			set_variable = { xiangqi_tmp_check_col = ROOT.xiangqi_tmp_target_col }

			# Legal move if not friendly-occupied
			if = {
				limit = {
					NOT = { xiangqi_is_square_occupied_by_friendly_government = yes }
				}
				hidden_effect = { xiangqi_add_legal_move = yes }
			}

			# Stop ray if ANY piece blocks
			if = {
				limit = { xiangqi_is_square_occupied = yes }
				break = yes
			}

			# Next square
			add_to_variable = { xiangqi_tmp_iter = 1 }
		}

	}
