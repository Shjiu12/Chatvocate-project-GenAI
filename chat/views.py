
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .serializers import ChatQuestionSerializer
from .search_documents import search_legal_documents
from .ai_service import generate_legal_answer


@api_view(["POST"])
def chat_question(request):
    # 1. Validate the question and conversation history.
    serializer = ChatQuestionSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    question = serializer.validated_data["question"]
    history = serializer.validated_data.get("history", [])

    try:
        # 2. Retrieve relevant legal passages from ChromaDB.
        matches = search_legal_documents(
            question,
            number_of_results=3,
        )

        # 3. Prepare the source information for the frontend.
        sources = []

        for match in matches:
            sources.append(
                {
                    "text": match["text"],
                    "source": match["source"],
                    "page": match.get("page"),
                }
            )

        # 4. Generate an answer using retrieved passages
        #    and previous conversation messages.
        answer = generate_legal_answer(
            question=question,
            matches=matches,
            history=history,
        )

        # 5. Return the answer and sources.
        return Response(
            {
                "question": question,
                "answer": answer,
                "sources": sources,
            },
            status=status.HTTP_200_OK,
        )

    except Exception:
        # Log the actual exception on the backend during debugging.
        import logging

        logging.getLogger(__name__).exception(
            "Error while processing the legal question."
        )

        return Response(
            {
                "error": (
                    "An error occurred while searching "
                    "the legal document or generating an answer."
                )
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )