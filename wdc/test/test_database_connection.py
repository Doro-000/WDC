import unittest
from unittest.mock import patch, Mock
from requests.exceptions import HTTPError, Timeout, ConnectionError
from src.DatabaseConnection import DatabaseConnection


class TestDatabaseConnection(unittest.TestCase):
    """
    Unit tests for the DatabaseConnection class.
    """

    def setUp(self):
        """
        Set up necessary objects for testing.
        """
        self.default_url = "https://ows.rasdaman.org/rasdaman/ows"
        self.db_conn = DatabaseConnection(self.default_url)
        self.query = "SELECT * FROM some_table"

    @patch("requests.post")
    def test_send_request_success(self, mock_post):
        """
        Test send_request method for a successful request.
        """
        # Mock the response object
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"Some response content"
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        # Call the method
        result = self.db_conn.send_request(self.query)

        # Assertions
        self.assertTrue(result["success"])
        self.assertEqual(result["result"], b"Some response content")
        self.assertEqual(result["httpCode"], 200)
        self.assertNotIn("httpError", result)
        self.assertNotIn("errorDetails", result)

    @patch("requests.post")
    def test_send_request_http_error(self, mock_post):
        """
        Test send_request method when an HTTP error occurs.
        """
        # Mock the response object
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.content = b"Not Found"
        mock_response.raise_for_status.side_effect = HTTPError(
            "404 Client Error: Not Found for url"
        )

        mock_post.return_value = mock_response

        # Call the method
        result = self.db_conn.send_request(self.query)

        # Assertions
        self.assertFalse(result["success"])
        self.assertIsNone(result["result"])
        self.assertEqual(result["httpCode"], 404)
        self.assertIn("httpError", result)
        self.assertEqual(result["httpError"], "404 Client Error: Not Found for url")
        self.assertEqual(result["errorDetails"], b"Not Found")

    @patch("requests.post")
    def test_send_request_timeout_error(self, mock_post):
        """
        Test send_request method when a timeout error occurs.
        """
        # Mock the request to raise a Timeout exception
        mock_post.side_effect = Timeout("The request timed out")

        # Call the method
        result = self.db_conn.send_request(self.query)
        print("Result:", result)  # Debug print

        # Assertions
        self.assertFalse(result["success"])
        self.assertIsNone(result["result"])
        self.assertIn("httpError", result)
        self.assertEqual(result["httpError"], "The request timed out")
        self.assertIsNone(result.get("httpCode"))
        self.assertIsNone(result.get("errorDetails"))

    @patch("requests.post")
    def test_send_request_connection_error(self, mock_post):
        """
        Test send_request method when a connection error occurs.
        """
        # Mock the request to raise a ConnectionError exception
        mock_post.side_effect = ConnectionError("Failed to establish a new connection")

        # Call the method
        result = self.db_conn.send_request(self.query)
        print("Result:", result)  # Debug print

        # Assertions
        self.assertFalse(result["success"])
        self.assertIsNone(result["result"])
        self.assertIn("httpError", result)
        self.assertEqual(result["httpError"], "Failed to establish a new connection")
        self.assertIsNone(result.get("httpCode"))
        self.assertIsNone(result.get("errorDetails"))

    def test_invalid_url(self):
        """
        Test initializing DatabaseConnection with an invalid URL.
        """
        invalid_url = "http://invalid_url"
        db_conn = DatabaseConnection(invalid_url)
        self.assertEqual(db_conn.endpoint_url, invalid_url)

    @patch("requests.post")
    def test_send_request_custom_url(self, mock_post):
        """
        Test send_request method with a custom endpoint URL.
        """
        custom_url = "https://custom.endpoint.url"
        db_conn = DatabaseConnection(custom_url)

        # Mock the response object
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"Some response content"
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        # Call the method
        result = db_conn.send_request(self.query)

        # Assertions
        self.assertTrue(result["success"])
        self.assertEqual(result["result"], b"Some response content")
        self.assertEqual(result["httpCode"], 200)
        self.assertNotIn("httpError", result)
        self.assertNotIn("errorDetails", result)
        mock_post.assert_called_once_with(custom_url, data={"query": self.query})


if __name__ == "__main__":
    unittest.main()
