from .models import Payment, PaymentHistory, PaymentRefund, PaymentCharge
from rest_framework import serializers


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['transaction_id', 'amount', 'customer_name','email', 'status', 'created_at',
                  'updated_at', 'paid']
        read_only_fields = ['transaction_id', 'status', 'paid', 'created_at', 'updated_at']

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0")
        return value

    
    
            
class PaymentHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentHistory
        fields = ['transaction_id', 'amount','customer_name', 'email', 'status', 'created_at',
                  'updated_at', 'paid','original_payment', 'notes']
        read_only_fields = ['transaction_id', 'status', 'paid', 'created_at', 'updated_at']

    def validate(self, data):
        if 'original_payment' not in data:
            raise serializers.ValidationError("Original payment is required")
        return data


class PaymentRefundSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentRefund
        fields = ['transaction_id', 'amount', 'email','customer_name', 'status', 'created_at', 
                 'updated_at', 'paid', 'original_payment', 'refund_reason', 
                 'refund_transaction_id']
        read_only_fields = ['transaction_id', 'status', 'paid', 'created_at','updated_at', 'refund_transaction_id' ]

    
    def validate(self, data):
        if data['amount'] > data['original_payment'].amount:
            raise serializers.ValidationError(
                "Refund amount cannot be greater than original payment amount"
            )
        return data

class PaymentChargeSerializer(serializers.ModelSerializer):
    total_amount = serializers.FloatField(read_only=True)
    class Meta:
        model = PaymentCharge
        fields = ['transaction_id', 'amount', 'email','customer_name', 'status', 'created_at', 
                 'updated_at', 'paid', 'description', 'tax', 'total_amount']
        read_only_fields = ['transaction_id', 'status', 'paid', 'created_at', 'updated_at', 'total_amount']

    def validate_tax(self, value):
        if value < 0:
            raise serializers.ValidationError("Tax cannot be negative")
        return value
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['total_amount'] = instance.calculate_total()
        return representation

    
