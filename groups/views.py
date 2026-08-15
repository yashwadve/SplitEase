from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from notifications.services import notify

from .forms import AddMemberForm, GroupForm
from .models import Group, GroupMembership
from .utils import get_membership, require_group_admin, require_group_member


@login_required
def group_list(request):
    groups = Group.objects.filter(members=request.user).order_by('-created_at')
    return render(request, 'groups/group_list.html', {'groups': groups})


@login_required
def group_create(request):
    if request.method == 'POST':
        form = GroupForm(request.POST, request.FILES)
        if form.is_valid():
            group = form.save(commit=False)
            group.created_by = request.user
            group.save()
            GroupMembership.objects.create(
                group=group, user=request.user, role=GroupMembership.Role.ADMIN,
            )
            messages.success(request, f'Group "{group.name}" created.')
            return redirect('groups:group_detail', pk=group.pk)
    else:
        form = GroupForm()
    return render(request, 'groups/group_form.html', {'form': form, 'is_create': True})


@login_required
def group_detail(request, pk):
    group = get_object_or_404(Group, pk=pk)
    membership = require_group_member(request.user, group)
    memberships = group.memberships.select_related('user').all()
    expenses = group.expenses.select_related('paid_by', 'category')[:10]
    return render(request, 'groups/group_detail.html', {
        'group': group,
        'memberships': memberships,
        'expenses': expenses,
        'is_admin': membership.is_admin,
    })


@login_required
def group_edit(request, pk):
    group = get_object_or_404(Group, pk=pk)
    require_group_admin(request.user, group)
    if request.method == 'POST':
        form = GroupForm(request.POST, request.FILES, instance=group)
        if form.is_valid():
            form.save()
            messages.success(request, 'Group updated.')
            return redirect('groups:group_detail', pk=group.pk)
    else:
        form = GroupForm(instance=group)
    return render(request, 'groups/group_form.html', {'form': form, 'is_create': False, 'group': group})


@login_required
def group_delete(request, pk):
    group = get_object_or_404(Group, pk=pk)
    require_group_admin(request.user, group)
    if request.method == 'POST':
        group.delete()
        messages.success(request, 'Group deleted.')
        return redirect('groups:group_list')
    return render(request, 'groups/group_confirm_delete.html', {'group': group})


@login_required
def add_member(request, pk):
    group = get_object_or_404(Group, pk=pk)
    require_group_admin(request.user, group)

    if request.method == 'POST':
        form = AddMemberForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            _, created = GroupMembership.objects.get_or_create(
                group=group, user=user, defaults={'role': GroupMembership.Role.MEMBER},
            )
            if created:
                messages.success(request, f'{user.display_name()} added to the group.')
                notify(user, f'You were added to the group "{group.name}".')
            else:
                messages.info(request, f'{user.display_name()} is already a member.')
            return redirect('groups:group_detail', pk=group.pk)
    else:
        form = AddMemberForm()

    return render(request, 'groups/add_member.html', {'form': form, 'group': group})


@login_required
def remove_member(request, pk, user_id):
    group = get_object_or_404(Group, pk=pk)
    require_group_admin(request.user, group)
    membership = get_object_or_404(GroupMembership, group=group, user_id=user_id)

    if membership.user_id == group.created_by_id:
        messages.error(request, "The group creator can't be removed from the group.")
        return redirect('groups:group_detail', pk=group.pk)

    if request.method == 'POST':
        membership.delete()
        messages.success(request, 'Member removed.')
    return redirect('groups:group_detail', pk=group.pk)