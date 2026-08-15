from collections import defaultdict
from decimal import Decimal


def calculate_group_balances(group):
    balances = defaultdict(lambda: Decimal('0.00'))

    expenses = group.expenses.select_related('paid_by').prefetch_related('splits__user')
    for expense in expenses:
        balances[expense.paid_by] += expense.amount
        for split in expense.splits.all():
            balances[split.user] -= split.amount_owed

    completed_settlements = group.settlements.filter(status='completed').select_related('paid_by', 'paid_to')
    for settlement in completed_settlements:
        balances[settlement.paid_by] += settlement.amount
        balances[settlement.paid_to] -= settlement.amount

    return dict(balances)


def simplify_debts(balances):
    creditors = []  # [amount, user] — amount > 0, they're owed money
    debtors = []    # [amount, user] — amount > 0, they owe money

    for user, amount in balances.items():
        amount = amount.quantize(Decimal('0.01'))
        if amount > 0:
            creditors.append([amount, user])
        elif amount < 0:
            debtors.append([-amount, user])

    creditors.sort(key=lambda pair: pair[0], reverse=True)
    debtors.sort(key=lambda pair: pair[0], reverse=True)

    transactions = []
    i, j = 0, 0
    while i < len(debtors) and j < len(creditors):
        debt_amount, debtor = debtors[i]
        credit_amount, creditor = creditors[j]
        settle_amount = min(debt_amount, credit_amount)

        if settle_amount > 0:
            transactions.append((debtor, creditor, settle_amount))

        debtors[i][0] -= settle_amount
        creditors[j][0] -= settle_amount

        if debtors[i][0] == 0:
            i += 1
        if creditors[j][0] == 0:
            j += 1

    return transactions


def count_naive_transactions(group):
    count = 0
    expenses = group.expenses.prefetch_related('splits')
    for expense in expenses:
        for split in expense.splits.all():
            if split.user_id != expense.paid_by_id and split.amount_owed > 0:
                count += 1
    return count


def get_user_overall_balance(user):
    from groups.models import Group

    groups = Group.objects.filter(members=user)
    total_owed = Decimal('0.00')
    total_to_receive = Decimal('0.00')
    group_balances = {}

    for group in groups:
        balances = calculate_group_balances(group)
        net = balances.get(user, Decimal('0.00'))
        group_balances[group] = net
        if net > 0:
            total_to_receive += net
        elif net < 0:
            total_owed += -net

    return total_owed, total_to_receive, group_balances