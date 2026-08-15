from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.shortcuts import get_object_or_404, redirect, render

from groups.models import Group
from groups.utils import get_membership, require_group_member

from .forms import ExpenseForm
from .models import Expense, ExpenseSplit
from .services import build_splits

import json

def _can_modify(user, expense):
    membership = get_membership(user, expense.group)
    return membership is not None and (expense.created_by_id == user.id or membership.is_admin)


@login_required
def expense_create(request, group_id):
    group = get_object_or_404(Group, pk=group_id)
    require_group_member(request.user, group)
    member_ids = set(group.members.values_list('id', flat=True))
    selected_participants = list(member_ids)

    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES, group=group)
        participant_ids = [int(uid) for uid in request.POST.getlist('participants')]
        selected_participants = participant_ids
        raw_values = {
            key.replace('split_', ''): value
            for key, value in request.POST.items() if key.startswith('split_')
        }

        if form.is_valid():
            if not set(participant_ids).issubset(member_ids):
                form.add_error(None, "Participants must be group members.")
            else:
                expense = form.save(commit=False)
                expense.group = group
                expense.created_by = request.user
                try:
                    splits = build_splits(expense, form.cleaned_data['split_type'], participant_ids, raw_values)
                except ValidationError as exc:
                    form.add_error(None, str(exc.message) if hasattr(exc, 'message') else str(exc))
                else:
                    expense.save()
                    for split in splits:
                        split.expense = expense
                    ExpenseSplit.objects.bulk_create(splits)
                    messages.success(request, f'Expense "{expense.title}" added.')
                    return redirect('groups:group_detail', pk=group.pk)
    else:
        form = ExpenseForm(group=group)

    return render(request, 'expenses/expense_form.html', {
        'form': form, 'group': group, 'members': group.members.all(),
        'is_create': True, 'selected_participants': selected_participants,
    })


@login_required
def expense_detail(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    require_group_member(request.user, expense.group)
    splits = expense.splits.select_related('user').all()
    return render(request, 'expenses/expense_detail.html', {
        'expense': expense, 'splits': splits, 'can_modify': _can_modify(request.user, expense),
    })


@login_required
def expense_edit(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    require_group_member(request.user, expense.group)
    if not _can_modify(request.user, expense):
        raise PermissionDenied("Only the person who added this expense or a group admin can edit it.")

    group = expense.group
    member_ids = set(group.members.values_list('id', flat=True))
    selected_participants = list(expense.splits.values_list('user_id', flat=True))

    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES, instance=expense, group=group)
        participant_ids = [int(uid) for uid in request.POST.getlist('participants')]
        selected_participants = participant_ids
        raw_values = {
            key.replace('split_', ''): value
            for key, value in request.POST.items() if key.startswith('split_')
        }

        if form.is_valid():
            if not set(participant_ids).issubset(member_ids):
                form.add_error(None, "Participants must be group members.")
            else:
                updated_expense = form.save(commit=False)
                try:
                    splits = build_splits(updated_expense, form.cleaned_data['split_type'], participant_ids, raw_values)
                except ValidationError as exc:
                    form.add_error(None, str(exc.message) if hasattr(exc, 'message') else str(exc))
                else:
                    updated_expense.save()
                    expense.splits.all().delete()
                    for split in splits:
                        split.expense = updated_expense
                    ExpenseSplit.objects.bulk_create(splits)
                    messages.success(request, 'Expense updated.')
                    return redirect('expenses:expense_detail', pk=updated_expense.pk)
    else:
        form = ExpenseForm(instance=expense, group=group)

    import json
    existing_splits = {
        s.user_id: str(s.share_value if expense.split_type in ('percentage', 'share') else s.amount_owed)
        for s in expense.splits.all()
    }

    return render(request, 'expenses/expense_form.html', {
        'form': form, 'group': group, 'members': group.members.all(),
        'is_create': False, 'expense': expense, 'selected_participants': selected_participants,
        'existing_splits_json': json.dumps(existing_splits),
    })


@login_required
def expense_delete(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    require_group_member(request.user, expense.group)
    if not _can_modify(request.user, expense):
        raise PermissionDenied("Only the person who added this expense or a group admin can delete it.")

    group_id = expense.group_id
    if request.method == 'POST':
        expense.delete()
        messages.success(request, 'Expense deleted.')
        return redirect('groups:group_detail', pk=group_id)
    return render(request, 'expenses/expense_confirm_delete.html', {'expense': expense})

