import cohere
from typing import List, Dict
from cohere_config import co  # Ensure this import brings in the initialized Cohere client
import uuid
from documents import Documents


class CohereModel:
    def __init__(self, documents: Documents):
        self.conversation_id = str(uuid.uuid4())
        self.docs = documents
        self.preamble_override = "You are Winston, a museum tour guide at the Guggenheim in Bilbao"

    def chat(self, query: str):
        """
        Generates a response to the user's query using the Cohere API.

        Parameters:
        query (str): The user's query.
        singular (bool): When we're only interested in fetching one artwork title

        Yields:
        event: A response event generated by the Cohere chat.

        """
        response = co.chat(message=query, search_queries_only=True)
        if response.search_queries:
            print("Retrieving information...")
            # Here you would call a method to retrieve the document based on the search query.

            documents = self.retrieve_docs(response)

            # Continue the conversation with the retrieved document
            response = co.chat(
                message=query,
                preamble_override=self.preamble_override,
                documents=documents,  # Assuming retrieve_docs returns a document in the required format
                conversation_id=self.conversation_id,
                stream=True,
            )
        else:
            # If there's no search query, just continue the conversation
            response = co.chat(
                message=query,
                preamble_override=self.preamble_override,
                conversation_id=self.conversation_id,
                stream=True
            )
        for event in response:
            yield event

    def retrieve_painting(self, query: str):
        response = co.chat(message=query, search_queries_only=True)
        if response.search_queries:
            print("Retrieving artwork...")
            # Here you would call a method to retrieve the document based on the search query.

            documents = self.retrieve_docs(response, 1)
            titles = [item['title'] for item in documents]
            return titles[0]
        else:
            print("No artwork found")

    def retrieve_docs(self, response, k=None) -> List[Dict[str, str]]:
        """
        Retrieves documents based on the search queries in the response.

        Parameters:
        response: The response object containing search queries.

        Returns:
        List[Dict[str, str]]: A list of dictionaries representing the retrieved documents.

        """
        # Get the query(s)
        queries = []
        for search_query in response.search_queries:
            queries.append(search_query["text"])

        # Retrieve documents for each query
        retrieved_docs = []
        for query in queries:
            if k:
                retrieved_docs.extend(self.docs.retrieve(query, 1))
            else:
                retrieved_docs.extend(self.docs.retrieve(query))

        # # Uncomment this code block to display the chatbot's retrieved documents
        # print("DOCUMENTS RETRIEVED:")
        # for idx, doc in enumerate(retrieved_docs):
        #     print(f"doc_{idx}: {doc}")
        # print("\n")

        return retrieved_docs

# Example usage:
# cohere_model = CohereModel()
# for event in cohere_model.chat("What is the largest mammal?"):
#     print(event)
