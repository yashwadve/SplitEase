from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from groups.models import Group


class Settlement(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        COMPLETED = 'completed', 'Completed'

    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='settlements')
    paid_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='settlements_paid',
    )
    paid_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='settlements_received',
    )
    amount = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
    )
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    settled_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(paid_by=models.F('paid_to')),
                name='settlement_payer_and_payee_differ',
            ),
        ]

    def __str__(self):
        return f"{self.paid_by} -> {self.paid_to}: {self.amount} ({self.status})"

    def mark_completed(self):
        from django.utils import timezone
        self.status = self.Status.COMPLETED
        self.settled_at = timezone.now()
        self.save(update_fields=['status', 'settled_at'])