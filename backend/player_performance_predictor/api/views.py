from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import PredictionSerializer
from player_performance_predictor.build_model.predictions import load_predictions

def home(request):
    return JsonResponse({'message': 'Welcome to the Player Performance Predictor API!'})

class PlayerPredictionView(APIView):
    def get(self, request, req_season):
        print(f"Request season: {req_season}")
        predictions_df = load_predictions(req_season)
        predictions = predictions_df.to_dict(orient='records')
        serializer = PredictionSerializer(predictions, many=True)
        return Response(serializer.data)
