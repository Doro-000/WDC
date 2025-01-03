from .helpers.utils import decodeCsv, decodeImage, decodeText
from .DatabaseConnection import DatabaseConnection
from .QueryBuilder import QueryBuilder
from .helpers.types import ReturnTypes
from typing import Optional


class Datacube:
    """
    Manages operations on a datacube such as querying data through the DatabaseConnection.
    """

    def __init__(self, dbc: DatabaseConnection, coverageId: str):
        """
        Initialize the Datacube instance with a DatabaseConnection.
        """
        self.dbc = dbc
        self.coverage = coverageId

    def getQueryBuilder(self, debug: bool = False):
        return QueryBuilder(coverageId=self.coverage, debug=debug)

    def execute_query(
        self,
        queryObject: QueryBuilder,
        encodingFormat: Optional[ReturnTypes] = None,
        raw: bool = False,
    ):
        """
        Executes the provided query using the DatabaseConnection.

        Returns:
            if raw is true: Bytes object directly from the network request
            else: decoded image (PNG, JPEG), pandas dataframe (CSV), or decoded text
        """
        query = queryObject.composeQueryFromOPS(encodingFormat)
        response = self.dbc.send_request(query)

        if response.get("result", None):
            if raw:
                return response.get("result", None)
            else:
                if encodingFormat == "CSV":
                    return decodeCsv(response)
                elif encodingFormat in {"JPEG", "PNG"}:
                    return decodeImage(response)
                else:
                    return decodeText(response)
        else:
            return response
