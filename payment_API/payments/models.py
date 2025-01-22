from django.db import models
import logging

logger = logging.getLogger(__name__)
# Create your models here

class PaymentOperationError(Exception):
    """
    Custom exception for payment operations
    """
    pass

class BasePayment(models.Model):
    """
        Abstract model for payment operations
    """
    PAYMENT_STATUS = (
        ('PENDING', 'PENDING'),
        ('COMPLETED', 'COMPLETED'),
        ('FAILED', 'FAILED'),
    )

    transaction_id = models.AutoField(primary_key=True)
    customer_name = models.CharField(max_length=55)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    email = models.EmailField()
    status = models.CharField(max_length=10, choices=PAYMENT_STATUS, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False)
    

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.email} - {self.amount} - {self.status}"
    
    def clean(self):
        """
        Validates the payment data before saving
        Raises validation errors if the validation fails
        """
        if self.amount <= 0:
            raise ValueError("Amount must be greater than 0")
        if not self.email:
            raise ValueError("Email is required")
        if '@' not in self.email:
            raise ValueError("Invalid email format")

    def mark_as_paid(self):
        """
        Marks the payment as paid and sets the status to 'COMPLETED'
        Raises PaymentOperationError if the operation fails
        """
        try:

            self.paid = True
            self.status = 'COMPLETED'
            self.save()
            logger.info(f"Payment {self.transaction_id} marked as paid")
        except Exception as e:
            logger.error(f"Error marking payment as paid: {e}")
            raise PaymentOperationError("Error marking payment as paid")
        
    
    def mark_as_failed(self):
        """
        Marks the payment as failed and sets the status to 'FAILED'
        Raises PaymentOperationError if the operation fails
        """
        try:

            self.paid = False
            self.status = 'FAILED'
            self.save()
            logger.error(f"Payment {self.transaction_id} marked as failed")
        except Exception as e:
            logger.error(f"Error marking payment as failed: {e}")
            raise PaymentOperationError("Error marking payment as failed")
        
    

class Payment(BasePayment):
    """
    Main payment model for processing transactions
    Includes payment method, last four digits of the card, and card type
    """


    payment_reference = models.CharField(max_length=255, blank=True, null=True, unique=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(amount__gt=0), name='payment_positive_amount'),
        ]
        unique_together = ['transaction_id', 'email']

    def process_payment(self):
        """
        Processes the payment by marking it as paid
        Returns True if the payment is processed successfully
        Raises PaymentOperationError if the operation fails
        """
        try:
            self.mark_as_paid()
            logger.info(f"Payment {self.transaction_id} processed Successfully")
            return True
        except Exception as e:
            error_message = f"Payment {self.transaction_id} failed to process: {e}"
            logger.error(error_message)
            self.mark_as_failed(error_message)
            raise PaymentOperationError(error_message)
  

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class PaymentHistory(BasePayment):
    """
    Tracks the history of a payment, includes notes
    """
    original_payment = models.ForeignKey(Payment, on_delete=models.CASCADE)
    notes = models.TextField(blank=True, null=True)

    def add_note(self, note):
        """
        Adds a note to the payment history
        Raises PaymentOperationError if the operation fails
        """
        try:
            if self.notes:
                self.notes += f"\n{note}"
            else:
                self.notes = note
            self.save()
            logger.info(f"Note added to payment {self.transaction_id}")
        except Exception as e:
            logger.error(f"Error adding note to payment {self.transaction_id}: {e}")
            raise PaymentOperationError(f"Error adding note to payment {self.transaction_id}: {e}")

class PaymentRefund(BasePayment):
    """
    Handles refunds operations for existing payments
    """
    original_payment = models.ForeignKey(Payment, on_delete=models.CASCADE)
    refund_reason = models.TextField(blank=True, null=True)
    refund_transaction_id = models.CharField(max_length=255, blank=True, null=True)

    def clean(self):
        """
        Validates refund amount against original payment amount
        """
        super().clean()
        if self.amount > self.original_payment.amount:
            raise ValueError("Refund amount cannot be greater than original payment")


    def process_refund(self):
        """
        Process the refund and mark it as paid
        Returns True if the refund is processed successfully
        """
        try:
            self.full_clean()
            self.mark_as_paid()
            logger.info(f"Payment {self.transaction_id} refunded successfully")           
            return True
        except Exception as e:
            error_message = f"Payment {self.transaction_id} failed to process: {e}"
            logger.error(error_message)
            self.mark_as_failed(error_message)
            raise PaymentOperationError(error_message)
        
class PaymentCharge(BasePayment):
    """
    Handles additional chargers with tax calcuklation
    """
    description = models.CharField(max_length=255)
    tax = models.FloatField(default=0)

    class meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(tax__gte=0), name='payment_charge_positive_tax'),
        ]

    def calculate_total(self):
        """
        Calculates the total amount including tax
        """
        return self.amount + self.tax
    
    def validate_tax(self):
        """
        validates the tax amount before saving
        """
        if self.tax < 0:
            raise ValueError("Tax cannot be negative")
        
    def save(self, *args, **kwargs):
        self.validate_tax()
        super().save(*args, **kwargs)
        


