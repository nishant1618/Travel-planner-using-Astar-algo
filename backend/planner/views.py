from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Place, Route, RoutePlace
from .serializers import PlaceSerializer, RouteSerializer

class PlaceViewSet(viewsets.ModelViewSet):
    queryset = Place.objects.all()
    serializer_class = PlaceSerializer
    
    def get_queryset(self):
        queryset = Place.objects.all()
        state = self.request.query_params.get('state', None)
        if state:
            queryset = queryset.filter(state=state)
        return queryset

class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    
    @action(detail=False, methods=['post'])
    def calculate(self, request):
        place_ids = request.data.get('places', [])
        places = Place.objects.filter(id__in=place_ids)
        
        if len(places) < 2:
            return Response(
                {"error": "At least 2 places are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from .utils import find_shortest_path
        optimal_path, total_distance = find_shortest_path(list(places))
        
        # Create route
        route = Route.objects.create(total_distance=total_distance)
        
        # Create route places
        for index, place in enumerate(optimal_path):
            RoutePlace.objects.create(
                route=route,
                place=place,
                order=index
            )
        
        return Response(RouteSerializer(route).data)
