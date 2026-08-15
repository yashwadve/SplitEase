from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from expenses.models import Expense
from groups.models import Group
from settlements.services import get_user_overall_balance


def landing(request):
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    return render(request, 'core/landing.html')


@login_required
def dashboard(request):
    user = request.user
    groups = Group.objects.filter(members=user).order_by('-created_at')

    total_owed, total_to_receive, group_balances = get_user_overall_balance(user)

    recent_expenses = (
        Expense.objects.filter(group__in=groups)
        .select_related('group', 'paid_by', 'category')
        .order_by('-created_at')[:10]
    )

    context = {
        'groups': groups,
        'total_owed': total_owed,
        'total_to_receive': total_to_receive,
        'group_balances': group_balances,
        'recent_expenses': recent_expenses,
    }
    return render(request, 'core/dashboard.html', context)