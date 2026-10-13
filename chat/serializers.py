
from rest_framework import serializers


class ChatQuestionSerializer(serializers.Serializer):
    question = serializers.CharField(
        required=True,
        allow_blank=False,
        trim_whitespace=True
    )