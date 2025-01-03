import requests
from requests.exceptions import HTTPError, Timeout, ConnectionError
from .helpers.types import NetworkRequestResult

class DatabaseConnection:
    """
    Handles HTTP connections to a database server for sending queries.
    """

    def __init__(self, endpoint_url="https://ows.rasdaman.org/rasdaman/ows"):
        """
        Initialize the connection with the URL of the database endpoint.
        Args:
            endpoint_url (str): The endpoint URL of the database server.
        """
        self.endpoint_url = endpoint_url

    def send_request(self, query) -> NetworkRequestResult:
        """
        Send a POST request to the database endpoint with the provided query.
        Args:
            query (str): The database query to send.
        Returns:
            requests.Response: The HTTP response returned by the server.
        """
        try:
            response = requests.post(self.endpoint_url, data={"query": query})
            response.raise_for_status()

            return {
                "success": True,
                "result": response.content,
                "httpCode": response.status_code,
            }
        except HTTPError as http_err:
            return {
                "success": False,
                "result": None,
                "httpCode": response.status_code,
                "httpError": str(http_err),
                "errorDetails": response.content,
            }
        except Timeout as timeout_err:
            return {
                "success": False,
                "result": None,
                "httpCode": None,
                "httpError": str(timeout_err),
                "errorDetails": None,
            }
        except ConnectionError as conn_err:
            return {
                "success": False,
                "result": None,
                "httpCode": None,
                "httpError": str(conn_err),
                "errorDetails": None,
            }
