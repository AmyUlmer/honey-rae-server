"""View module for handling requests for employee data"""
from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers, status
from repairsapi.models import ServiceTicket, Employee, Customer


class ServiceTicketView(ViewSet):
    """Honey Rae API employees view"""

    def list(self, request):
        """Handle GET requests to get all employees
        Returns:
            Response -- JSON serialized list of employees
        """
        service_tickets = []

        #employee can view all tix. customers requesting own tix.
        if request.auth.user.is_staff:
            service_tickets = ServiceTicket.objects.all()
        else: 
            service_tickets = ServiceTicket.objects.filter(customer__user=request.auth.user)

        serialized = ServiceTicketSerializer(service_tickets, many=True)
        return Response(serialized.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        """Handle GET requests for single service ticket
        Returns:
            Response -- JSON serialized service ticket record
        """

        service_ticket = ServiceTicket.objects.get(pk=pk)
        serialized = ServiceTicketSerializer(service_ticket, context={'request': request})
        return Response(serialized.data, status=status.HTTP_200_OK)
    
    def create(self, request):
        """Handle POST requests for service tickets

        Returns:
            Response: JSON serialized representation of newly created service ticket
        """
        new_ticket = ServiceTicket()
        new_ticket.customer = Customer.objects.get(user=request.auth.user)
        new_ticket.description = request.data['description']
        new_ticket.emergency = request.data['emergency']
        new_ticket.save()

        serialized = ServiceTicketSerializer(new_ticket, many=False)

        return Response(serialized.data, status=status.HTTP_201_CREATED)

#create serializer for 'employee' field

class TicketEmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ('id', 'specialty', 'full_name', )

class ServiceTicketSerializer(serializers.ModelSerializer):
    """JSON serializer for tickets"""

    #how you want employee to be serialized
    #for the employee field I want to use the TicketEmployee Serializer
    employee = TicketEmployeeSerializer(many=False)


    class Meta:
        model = ServiceTicket
        fields = ('id', 'customer', 'employee', 'description', 'emergency', 'date_completed')
        depth = 2 #expands foreign keys (customer,employee)

