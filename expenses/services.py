from decimal import Decimal, ROUND_HALF_UP

from django.core.exceptions import ValidationError

from .models import ExpenseSplit


def build_splits(expense, split_type, participant_ids, raw_values):
    if not participant_ids:
        raise ValidationError("Select at least one participant.")

    amount = expense.amount
    splits = []

    if split_type == 'equal':
        n = len(participant_ids)
        share = (amount / n).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        allocated = Decimal('0.00')
        for i, user_id in enumerate(participant_ids):
            owed = share if i < n - 1 else (amount - allocated)
            allocated += owed
            splits.append(ExpenseSplit(user_id=user_id, amount_owed=owed))

    elif split_type == 'custom':
        total = Decimal('0.00')
        for user_id in participant_ids:
            value = Decimal(str(raw_values.get(str(user_id), '0') or '0'))
            total += value
            splits.append(ExpenseSplit(user_id=user_id, amount_owed=value))
        if total != amount:
            raise ValidationError(f"Custom amounts must add up to {amount} (got {total}).")

    elif split_type == 'percentage':
        n = len(participant_ids)
        total_pct = Decimal('0.00')
        allocated = Decimal('0.00')
        for i, user_id in enumerate(participant_ids):
            pct = Decimal(str(raw_values.get(str(user_id), '0') or '0'))
            total_pct += pct
            owed = (amount * pct / Decimal('100')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            if i == n - 1:
                owed = amount - allocated
            allocated += owed
            splits.append(ExpenseSplit(user_id=user_id, amount_owed=owed, share_value=pct))
        if total_pct != Decimal('100'):
            raise ValidationError(f"Percentages must add up to 100 (got {total_pct}).")

    elif split_type == 'share':
        n = len(participant_ids)
        shares = {}
        total_shares = Decimal('0.00')
        for user_id in participant_ids:
            s = Decimal(str(raw_values.get(str(user_id), '0') or '0'))
            if s <= 0:
                raise ValidationError("Each participant's share must be greater than zero.")
            shares[user_id] = s
            total_shares += s

        allocated = Decimal('0.00')
        for i, user_id in enumerate(participant_ids):
            owed = (amount * shares[user_id] / total_shares).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            if i == n - 1:
                owed = amount - allocated
            allocated += owed
            splits.append(ExpenseSplit(user_id=user_id, amount_owed=owed, share_value=shares[user_id]))

    else:
        raise ValidationError("Unknown split type.")

    return splits