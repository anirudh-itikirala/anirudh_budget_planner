def suggest_savings(adjusted_budget, weekly_spending, week):
    """Suggests savings based on how close spending is to the weekly budget."""
    budget = adjusted_budget[week]
    spent = weekly_spending[week]
    remaining_budget = budget - spent

    if remaining_budget < 10:
        return f"Warning: You're close to exceeding your budget for Week {week + 1}. Consider skipping an outing or choosing a cheaper option."
    elif remaining_budget < 0:
        return f"Week {week + 1}: You have exceeded your budget by ${abs(remaining_budget):.2f}. Adjust your spending for the coming weeks."
    return f"Week {week + 1}: You're on track with ${remaining_budget:.2f} remaining."
