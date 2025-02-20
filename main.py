from budget_calculator import calculate_dynamic_weekly_budget
from savings_suggestions import suggest_savings
from data_handler import load_data, save_data
from datetime import datetime

# Load persistent data
data = load_data()
monthly_budget = data["monthly_budget"]
weekly_outings = data["weekly_outings"]
weekly_spending = data["weekly_spending"]

def log_charge_ui():
    """Log a charge for the current week."""
    week = get_current_week()
    print(f"Logging charge for Week {week + 1} (based on today's date).")
    charge_name = input("Enter the name of the charge: ")
    charge_amount = float(input(f"Enter the price for {charge_name}: $"))
    log_charge(data, week, charge_name, charge_amount)

    # Calculate weekly budgets dynamically with planned outings
    weekly_budgets = calculate_dynamic_weekly_budget(data["monthly_budget"], data["weekly_outings"])
    remaining_budget = weekly_budgets[week]
    print(f"Remaining budget for Week {week + 1}: ${remaining_budget:.2f}")

def view_weekly_budgets(data):
    """Display total spent and remaining budgets for each week."""
    weekly_budgets = calculate_dynamic_weekly_budget(data["monthly_budget"], data["weekly_outings"])
    print("\nWeekly Budgets:")
    for week in range(4):
        total_spent = data["weekly_spending"][week]
        remaining_budget = weekly_budgets[week] - total_spent
        print(f"Week {week + 1}:")
        print(f"  Total Spent: ${total_spent:.2f}")
        print(f"  Remaining Budget: ${remaining_budget:.2f}")



def get_current_week():
    """Determine the current week of the month."""
    today = datetime.today()
    day_of_month = today.day
    return (day_of_month - 1) // 7  # Week starts at 0

def log_charge(data, week, charge_name, charge_amount):
    """Log a charge for a specific week with rollover-aware budgets."""
    current_date = datetime.today().strftime("%Y-%m-%d")

    # Append the charge to the week's charges
    data["charges"][week].append({
        "name": charge_name,
        "amount": charge_amount,
        "date": current_date
    })

    # Update weekly spending
    data["weekly_spending"][week] += charge_amount
    save_data(data)

    # Calculate and log the new remaining budget
    weekly_budgets = calculate_weekly_budgets_with_outing_rollover(data)
    remaining_budget = weekly_budgets[week] - data["weekly_spending"][week]
    print(f"Remaining budget for Week {week + 1}: ${remaining_budget:.2f}")

def calculate_weekly_budgets_with_outing_rollover(data):
    """Calculate weekly budgets with outing-based allocation and conditional rollovers."""
    current_week = get_current_week()
    total_outings = sum(data["weekly_outings"])
    if total_outings == 0:
        # Prevent division by zero; distribute equally
        base_weekly_budgets = [data["monthly_budget"] / 4] * 4
    else:
        # Proportionally allocate budget based on outings
        base_weekly_budgets = [
            (data["weekly_outings"][week] / total_outings) * data["monthly_budget"]
            for week in range(4)
        ]

    # Start with base weekly budgets
    weekly_budgets = base_weekly_budgets[:]
    rollover = 0

    for week in range(4):
        if week < current_week:
            # Completed weeks adjust for rollover
            weekly_budgets[week] += rollover
            spent = data["weekly_spending"][week]
            remaining = weekly_budgets[week] - spent
            rollover = max(remaining, 0)  # Carry forward remaining funds
        elif week == current_week:
            # Current week adjusts for rollover but doesn't affect the next
            weekly_budgets[week] += rollover
            rollover = 0  # Do not carry over until the week is complete
        else:
            # Future weeks remain static
            break

    return weekly_budgets


def calculate_monthly_stats(data):
    """Calculate total spending, savings, and remaining budget for the month."""
    total_spent = sum(data["weekly_spending"])
    total_budget = data["monthly_budget"]
    total_savings = total_budget - total_spent
    return {
        "total_spent": total_spent,
        "total_savings": total_savings,
        "remaining_budget": total_budget - total_spent
    }

def edit_outings_ui():
    """Edit outings for a specific week."""
    while True:
        week = int(input("Enter the week number to edit outings (1-4, or 0 to go back): ")) - 1
        if week == -1:
            break  # Exit editing
        if 0 <= week < 4:
            new_outings = int(input(f"Enter the new number of outings for Week {week + 1}: "))
            data["weekly_outings"][week] = new_outings
            save_data(data)
            print(f"Week {week + 1} outings updated to {new_outings}.")
        else:
            print("Invalid week number. Please try again.")

def edit_spending_ui():
    """Edit spending by showing all purchases for the month and removing one."""
    # Combine all purchases into a single list with week info
    all_purchases = []
    for week in range(4):
        for charge in data["charges"][week]:
            all_purchases.append({
                "name": charge["name"],
                "amount": charge["amount"],
                "date": charge["date"],
                "week": week
            })

    # If no purchases exist, notify the user
    if not all_purchases:
        print("No purchases logged for this month.")
        return

    # Display all purchases
    print("Purchases for the Month:")
    for i, purchase in enumerate(all_purchases):
        print(f"{i + 1}. {purchase['name']} - ${purchase['amount']:.2f} (Date: {purchase['date']}, Week {purchase['week'] + 1})")

    # Ask the user to select a purchase to remove
    purchase_index = int(input("Enter the number of the purchase to remove: ")) - 1
    if 0 <= purchase_index < len(all_purchases):
        # Retrieve the selected purchase
        selected_purchase = all_purchases[purchase_index]
        week = selected_purchase["week"]
        refund_amount = selected_purchase["amount"]

        # Remove the purchase from the corresponding week
        data["charges"][week] = [
            charge for charge in data["charges"][week]
            if not (
                charge["name"] == selected_purchase["name"] and
                charge["amount"] == refund_amount and
                charge["date"] == selected_purchase["date"]
            )
        ]

        # Subtract the amount from the weekly spending for the corresponding week
        data["weekly_spending"][week] -= refund_amount

        # Refund the money to the current week
        current_week = get_current_week()
        if week == current_week:
            print("Refunding to the same week.")
        else:
            print(f"Refunding ${refund_amount:.2f} to Week {current_week + 1}.")
            data["weekly_spending"][current_week] -= refund_amount

        # Save updated data
        save_data(data)
        print(f"Removed '{selected_purchase['name']}' for ${refund_amount:.2f}. Spending and budget updated.")
    else:
        print("Invalid purchase number.")


def view_monthly_stats(data):
    """Display total stats for the month."""
    stats = calculate_monthly_stats(data)
    print("\nMonthly Statistics:")
    print(f"  Total Spent: ${stats['total_spent']:.2f}")
    print(f"  Total Saved: ${stats['total_savings']:.2f}")
    print(f"  Remaining Budget: ${stats['remaining_budget']:.2f}")

def main():
    """Main program loop."""
    while True:
        print("\nMenu:")
        print("1. Log a charge (current week).")
        print("2. Edit outings.")
        print("3. Edit spending for previous weeks.")
        print("4. View weekly budgets and suggestions.")
        print("5. View monthly statistics.")
        print("6. Exit.")

        choice = input("Choose an option: ")

        if choice == "1":
            log_charge_ui()
        elif choice == "2":
            edit_outings_ui()
        elif choice == "3":
            edit_spending_ui()
        elif choice == "4":
            view_weekly_budgets(data)
        elif choice == "5":
            view_monthly_stats(data)
        elif choice == "6":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
