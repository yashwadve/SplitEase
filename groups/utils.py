from django.core.exceptions import PermissionDenied

from .models import GroupMembership


def get_membership(user, group):
    return GroupMembership.objects.filter(group=group, user=user).first()


def require_group_member(user, group):
    membership = get_membership(user, group)
    if membership is None:
        raise PermissionDenied("You are not a member of this group.")
    return membership


def require_group_admin(user, group):
    membership = require_group_member(user, group)
    if not membership.is_admin:
        raise PermissionDenied("Only group admins can perform this action.")
    return membership