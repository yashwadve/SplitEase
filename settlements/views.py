from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.models import User
from groups.models import Group
from groups.utils import require_group_member

from .models import Settlement
from .services import calculate_group_balances, count_naive_transactions, simplify_debts


@login_required
def balance_sheet(request, group_id):
    group = get_object_or_404(Group, pk=group_id)
    require_group_member(request.user, group)

    balances = calculate_group_balances(group)
    simplified_transactions = simplify_debts(balances)
    naive_count = count_naive_transactions(group)

    context = {
        'group': group,
        'balances': balances,
        'simplified_transactions': simplified_transactions,
        'naive_count': naive_count,
        'simplified_count': len(simplified_transactions),
    }
    return render(request, 'settlements/balance_sheet.html', context)


@login_required
def record_settlement(request, group_id):
    group = get_object_or_404(Group, pk=group_id)
    require_group_member(request.user, group)

    if request.method == 'POST':
        paid_by = get_object_or_404(User, pk=request.POST.get('paid_by'), groups_joined=group)
        paid_to = get_object_or_404(User, pk=request.POST.get('paid_to'), groups_joined=group)

        try:
            amount = Decimal(request.POST.get('amount', '0'))
        except InvalidOperation:
            messages.error(request, "Invalid amount.")
            return redirect('settlements:balance_sheet', group_id=group.id)

        if paid_by == paid_to or amount <= 0:
            messages.error(request, "Invalid settlement — payer/payee must differ and amount must be positive.")
            return redirect('settlements:balance_sheet', group_id=group.id)

        Settlement.objects.create(
            group=group, paid_by=paid_by, paid_to=paid_to, amount=amount,
            status=Settlement.Status.COMPLETED, settled_at=timezone.now(),
        )
        messages.success(request, f"Recorded: {paid_by.display_name()} paid {paid_to.display_name()} ₹{amount}")

    return redirect('settlements:balance_sheet', group_id=group.id)


@login_required
def settlement_history(request, group_id):
    group = get_object_or_404(Group, pk=group_id)
    require_group_member(request.user, group)
    settlements = group.settlements.select_related('paid_by', 'paid_to').all()
    return render(request, 'settlements/history.html', {'group': group, 'settlements': settlements})


@login_required
def mark_settlement_completed(request, pk):
    settlement = get_object_or_404(Settlement, pk=pk)
    require_group_member(request.user, settlement.group)
    if request.method == 'POST':
        settlement.mark_completed()
        messages.success(request, 'Settlement marked as completed.')
    return redirect('settlements:history', group_id=settlement.group_id)