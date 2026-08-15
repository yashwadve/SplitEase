from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from groups.models import Group


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    icon = models.CharField(
        max_length=50, blank=True,
        help_text="Optional icon identifier for the UI, e.g. a Bootstrap Icons class name.",
    )

    class Meta:
        verbose_name_plural = 'categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Expense(models.Model):
    class SplitType(models.TextChoices):
        EQUAL = 'equal', 'Equal'
        CUSTOM = 'custom', 'Custom amount'
        PERCENTAGE = 'percentage', 'Percentage'
        SHARE = 'share', 'Share-based'

    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='expenses')
    title = models.CharField(max_length=200)
    amount = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
    )
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='expenses',
    )
    paid_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='expenses_paid',
    )
    split_type = models.CharField(max_length=12, choices=SplitType.choices, default=SplitType.EQUAL)
    date = models.DateField()
    notes = models.TextField(blank=True)
    receipt_image = models.ImageField(upload_to='receipts/', blank=True, null=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='expenses_created',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.title} ({self.amount}) — {self.group}"


class ExpenseSplit(models.Model):
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE, related_name='splits')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='expense_splits',
    )
    amount_owed = models.DecimalField(max_digits=10, decimal_places=2)
    share_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        unique_together = ('expense', 'user')

    def __str__(self):
        return f"{self.user} owes {self.amount_owed} for {self.expense}"