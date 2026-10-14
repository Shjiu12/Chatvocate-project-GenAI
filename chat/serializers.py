
from rest_framework import serializers


class ChatMessageSerializer(serializers.Serializer):
    role = serializers.ChoiceField(
        choices=["user", "assistant"],
        required=True,
    )

    content = serializers.CharField(
        required=True,
        allow_blank=False,
        trim_whitespace=True,
    )


class ChatQuestionSerializer(serializers.Serializer):
    question = serializers.CharField(
        required=True,
        allow_blank=False,
        trim_whitespace=True,
    )

    history = ChatMessageSerializer(
        many=True,
        required=False,
        default=list,
    )

    def validate_history(self, value):
        if len(value) > 20:
            raise serializers.ValidationError(
                "A maximum of 20 previous messages is allowed."
            )

        return value