JAP_Increase_Agricultural_Financial_Crisis = {
	if = {
		limit = {
			has_idea = JAP_Agricultural_Financial_Crisis_1_idea
		}
		swap_ideas = {
			remove_idea = JAP_Agricultural_Financial_Crisis_1_idea
			add_idea = JAP_Agricultural_Financial_Crisis_2_idea
		}
	}
	else_if = {
		limit = {
			has_idea = JAP_Agricultural_Financial_Crisis_2_idea
		}
		swap_ideas = {
			remove_idea = JAP_Agricultural_Financial_Crisis_2_idea
			add_idea = JAP_Agricultural_Financial_Crisis_3_idea
		}
	}
	else_if = {
		limit = {
			has_idea = JAP_Agricultural_Financial_Crisis_3_idea
		}
		swap_ideas = {
			remove_idea = JAP_Agricultural_Financial_Crisis_3_idea
			add_idea = JAP_Agricultural_Financial_Crisis_4_idea
		}
	}
}

JAP_Decrease_Agricultural_Financial_Crisis = {
	if = {
		limit = {
			has_idea = JAP_Agricultural_Financial_Crisis_1_idea
		}
		remove_ideas = JAP_Agricultural_Financial_Crisis_1_idea
	}
	else_if = {
		limit = {
			has_idea = JAP_Agricultural_Financial_Crisis_2_idea
		}
		swap_ideas = {
			remove_idea = JAP_Agricultural_Financial_Crisis_2_idea
			add_idea = JAP_Agricultural_Financial_Crisis_1_idea
		}
	}
	else_if = {
		limit = {
			has_idea = JAP_Agricultural_Financial_Crisis_3_idea
		}
		swap_ideas = {
			remove_idea = JAP_Agricultural_Financial_Crisis_3_idea
			add_idea = JAP_Agricultural_Financial_Crisis_2_idea
		}
	}
	else_if = {
		limit = {
			has_idea = JAP_Agricultural_Financial_Crisis_4_idea
		}
		swap_ideas = {
			remove_idea = JAP_Agricultural_Financial_Crisis_4_idea
			add_idea = JAP_Agricultural_Financial_Crisis_3_idea
		}
	}
}