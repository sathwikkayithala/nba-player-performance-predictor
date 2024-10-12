from rest_framework import serializers

class PredictionSerializer(serializers.Serializer):
    Player = serializers.CharField(max_length=100)
    Season = serializers.IntegerField()
    Age = serializers.IntegerField()
    Pos = serializers.CharField(max_length=10)
    PTS = serializers.FloatField()
    AST = serializers.FloatField()
    TRB = serializers.FloatField()
    STL = serializers.FloatField()
    BLK = serializers.FloatField()