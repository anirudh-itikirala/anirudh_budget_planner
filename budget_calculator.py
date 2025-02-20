def calculate_dynamic_weekly_budget(monthly_budget, planned_outings):
    """Calculate weekly budgets dynamically based on planned outings."""
    total_outings = sum(planned_outings)
    if total_outings == 0:
        # Prevent division by zero; distribute equally
        return [monthly_budget / 4] * 4
    return [
        (monthly_budget * outings / total_outings) if outings > 0 else 0
        for outings in planned_outings
    ]


def adjust_budget_for_charge(weekly_budgets, week, charge):
    """Adjusts the budget for a specific week by subtracting the charge."""
    if 0 <= week < len(weekly_budgets):
        weekly_budgets[week] -= charge
    return weekly_budgets
