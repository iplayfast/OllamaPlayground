import unittest
from unittest.mock import patch, MagicMock
from rag_ollama.rag_engine import RAGEngine, load_config

class TestRAGEngine(unittest.TestCase):
    def setUp(self):
        self.config = {
            "embedding_model": "nomic-embed-text",
            "response_model": "llama2"
        }
        self.rag_engine = RAGEngine(self.config)
        
        # Create a dummy data file for testing
        with open("test_data.txt", "w") as f:
            f.write("This is some test content for the RAG engine.")

    def tearDown(self):
        import os
        if os.path.exists("test_data.txt"):
            os.remove("test_data.txt")

    @patch('ollama.embeddings')
    @patch('ollama.generate')
    def test_query(self, mock_generate, mock_embeddings):
        # Mock embeddings response
        mock_embeddings.return_value = {
            'embedding': [0.1] * 1024  # Assuming 1024-dimensional embeddings
        }
        
        # Mock generate response
        mock_generate.return_value = {
            'response': 'This is a test response about test content.'
        }

        # First, index the documents
        self.rag_engine.load_and_index_documents("test_data.txt")

        # Test basic query
        response = self.rag_engine.query("What is this about?")
        self.assertIn("test", response["result"].lower())
        
        # Test query with system prompt
        response_with_system_prompt = self.rag_engine.query(
            "Tell me about the content.", 
            system_prompt="Be brief."
        )
        self.assertIsInstance(response_with_system_prompt["result"], str)
        self.assertTrue(len(response_with_system_prompt["result"]) > 0)

        # Verify the mock calls
        mock_embeddings.assert_called()
        mock_generate.assert_called()

if __name__ == '__main__':
    unittest.main()
