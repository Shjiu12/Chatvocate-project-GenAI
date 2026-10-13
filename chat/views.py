
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .serializers import ChatQuestionSerializer
from .search_documents import search_legal_documents
from .ai_service import generate_legal_answer

@api_view(["POST"])
def chat_question(request):
    # 1. Validate the user's question
    serializer = ChatQuestionSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    question = serializer.validated_data["question"]

    try:
        # 2. Search the legal document using ChromaDB
        matches = search_legal_documents(
            question,
            number_of_results=3
        )

        # 3. Handle cases where no passages are available
        if not matches:
            return Response(
                {
                    "question": question,
                    "answer": (
                        "No matching legal passages were found "
                        "in the indexed document."
                    ),
                    "sources": []
                },
                status=status.HTTP_200_OK
            )

        # 4. Prepare the retrieved passages
        sources = []

        for match in matches:
            sources.append({
                "text": match["text"],
                "source": match["source"],
                # "page": match["page"]
            })

        # 5. Return the results to the user
        answer = generate_legal_answer(question, matches)

        return Response(
            {
                "question": question,
                "answer": answer,
                "sources": sources
            },
            status=status.HTTP_200_OK
        )

    except Exception:
        # Avoid exposing internal errors to API clients
        return Response(
            {
                "error": (
                    "An error occurred while searching "
                    "the legal document."
                )
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )