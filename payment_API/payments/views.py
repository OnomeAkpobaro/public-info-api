
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Payment, PaymentHistory, PaymentRefund, PaymentCharge
from .serializers import PaymentSerializer, PaymentHistorySerializer, PaymentRefundSerializer, PaymentChargeSerializer
from rest_framework.decorators import action
from .paystack import PaystackMixin
import json
import logging
from django.urls import reverse

# Create your views here.
logger = logging.getLogger(__name__)

class PaymentViewSet(PaystackMixin, viewsets.ModelViewSet):
    """
    Viewset for payment operations
    """
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    
    

    @action(detail=True, methods=['post'])
    def process(self, request, pk=None):
        payment = self.get_object()
        try:
            payment.process_payment()
            return Response({
                "message": "Payment processed successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    @action(detail=True, methods=['post'])
    def mark_failed(self, request, pk=None):
        payment = self.get_object()
        try:
            payment.mark_as_failed()
            return Response({
                "message": "Payment marked as failed"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    @action(detail=True, methods=['post'])
    def initiate_payment(self, request, pk=None):
        payment = self.get_object()
        callback_url = request.build_absolute_uri(reverse('payment-process', kwargs={'pk': str(payment.transaction_id)}))
        try:
            paystack_response = self.initialize_payment(amount=float(payment.amount), email=payment.email, callback_url=callback_url)

            payment.payment_reference = paystack_response['data']['reference']
            payment.save()

            return Response({
                "status": "success",
                "message": "Payment Link",
                "data": {
                    "authorization_url": paystack_response['data']['authorization_url'],
                    "reference": paystack_response['data']['reference']
                    }
            })
        except Exception as e:
            return Response({
                "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    @action(detail=True, methods=['post'])
    def verify_payment(self, request, pk=None):
        payment = self.get_object()
    
        reference = payment.payment_reference
        try:
            verification_response = self.verify_payment(reference)
            
            if verification_response['data']['status'] == "success":
                payment.mark_as_paid()
               
                return Response({
                    "message": "Payment verified successfully", 
                    "data": verification_response['data']
                    }, status=status.HTTP_200_OK)
            else:
                payment.mark_as_failed()
                return Response({
                    "message": "Payment failed", 
                    "data": verification_response['data']
                    }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error verifying payment: {str(e)}")
            return Response({
                "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
       

    
    @action(detail=False, methods=['post'])
    def paystack_webhook(self, request):
        #Verify the webhook signature
        paystack_signature = request.META.get('HTTP_X_PAYSTACK_SIGNATURE')
        if not paystack_signature:
            return Response({
                "error": "Paystack Signature not found"}, status=status.HTTP_400_BAD_REQUEST)
        if not self.verify_webhook_signature(request.body, paystack_signature):
            return Response({
                "error": "Invalid Paystack Signature"}, status=status.HTTP_400_BAD_REQUEST)
        #Process the webhook
        payload = json.loads(request.body)
        event = payload['event']
        data = payload['data']

        try:
            payment = Payment.objects.get(payment_reference=data['reference'])
            if event == 'charge.success':
                payment.mark_as_paid()
                payment.save()
            elif event == 'charge.failed':
                payment.mark_as_failed()
            return Response({
                "message": "Webhook processed successfully"}, status=status.HTTP_200_OK)
        except Payment.DoesNotExist:
            logger.error(f"Payment with reference {data['reference']} not found")
            return Response({
                "error": "Payment not found"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error processing webhook: {str(e)}")
            return Response({
                "error": "Error processing webhook"}, status=status.HTTP_400_BAD_REQUEST)

        
                
        

class PaymentHistoryViewSet(viewsets.ModelViewSet):
    """
    Viewset for payment history operations
    """
    queryset = PaymentHistory.objects.all()
    serializer_class = PaymentHistorySerializer

    @action(detail=True, methods=['post'])
    def add_note(self, request, pk=None):
        payment_history = self.get_object()
        note = request.data.get('note')

        if not note:
            return Response({
                "error": "Note is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            payment_history.add_note(note)
            return Response({
                "message": "Note added successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
class PaymentRefundViewSet(viewsets.ModelViewSet):
    """
    Viewset for payment refund operations
    """
    queryset = PaymentRefund.objects.all()
    serializer_class = PaymentRefundSerializer

    @action(detail=True, methods=['post'])
    def process_refund(self, request, pk=None):
        payment_refund = self.get_object()
        try:
            payment_refund.process_refund()
            return Response({
                "message": "Refund processed successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    
class PaymentChargeViewSet(viewsets.ModelViewSet):
    """
    Viewset for payment charge operations
    """
    queryset = PaymentCharge.objects.all()
    serializer_class = PaymentChargeSerializer

    @action(detail=True, methods=['get'])
    def calculate_total(self, request, pk=None):
        payment_charge = self.get_object()
        total = payment_charge.calculate_total()
        return Response({
            "total_amount": total}, status=status.HTTP_200_OK)
   
