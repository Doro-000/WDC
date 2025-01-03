import unittest
import requests
from src.Datacube import Datacube
from src.QueryBuilder import QueryBuilder
from src.DatabaseConnection import DatabaseConnection

from parameterized import parameterized
import pytest


class TestDatacube(unittest.TestCase):

    def setUp(self):
        # create a mock DatabaseConnection object for testing
        self.db_connection = DatabaseConnection()
        self.dataCube = Datacube(self.db_connection, "AvgLandTemp")

    def test_initialization(self):
        # test if Datacube is initialized correctly
        coverage_id = "AvgLandTemp"
        datacube = Datacube(self.db_connection, coverage_id)
        self.assertEqual(datacube.dbc, self.db_connection)
        self.assertEqual(datacube.coverage, coverage_id)

    def test_get_query_builder(self):
        # test the getQueryBuilder method
        coverage_id = "AvgLandTemp"
        datacube = Datacube(self.db_connection, coverage_id)
        query_builder = datacube.getQueryBuilder()
        self.assertIsInstance(query_builder, QueryBuilder)
        self.assertEqual(query_builder.coverageId, coverage_id)

    def test_execute_query(self):
        # test the execute_query method
        coverage_id = "AvgLandTemp"
        datacube = Datacube(self.db_connection, coverage_id)
        query_builder = datacube.getQueryBuilder(debug=True)
        query_builder.subset(
            lat=53.08, long=8.80, startDate="2014-01", endDate="2014-12"
        )
        query_res = datacube.execute_query(query_builder)

        # check if the query result is a dictionary (indicating error response)
        self.assertIsInstance(query_res, dict)

        if "ExceptionText" in query_res:
            self.assertIn("InvalidRequest", query_res["ExceptionText"])
        else:
            self.assertIn(b"InvalidRequest", query_res.get("errorDetails", b""))

    def test_slice(self):
        """
        Test slice method.
        """
        query = QueryBuilder(self.dataCube)
        self.assertEqual(
            repr(query.subset(lat=1, long=2, startDate="2014-07")),
            """$c[Lat(1),Long(2),ansi("2014-07")]""",
        )

    @parameterized.expand(
        [
            ("ADD", "+"),
            ("SUB", "-"),
            ("PROD", "*"),
            ("DIV", "/"),
            ("MOD", "%"),
        ],
    )
    def test_binaryStaticArthimeticOps(self, op, sign):
        """
        Test staticArthimetic method for arithmetic operations
        """
        query = QueryBuilder(self.dataCube)
        self.assertEqual(repr(query.arthimetic(op, 1)), f"""$c {sign} 1""")

    @parameterized.expand(
        [
            "ABS",
            "ROUND",
            "FLOOR",
            "CEIL",
        ]
    )
    def test_unaryStaticArthimeticOps(self, operation):
        """
        Test staticArthimetic method for arithmetic operations that are unary operators
        """
        query = QueryBuilder(self.dataCube)
        self.assertEqual(
            repr(query.arthimetic(operation)), f"""{operation.lower()}($c)"""
        )

    @parameterized.expand(
        [
            "EXP",
            "LOG",
            "LN",
            "SQRT",
        ]
    )
    def test_exponentialFunctions(self, operation):
        """
        Test expFuncs method for exponential operations
        """
        query = QueryBuilder(self.dataCube)
        self.assertEqual(
            repr(query.expFuncs(operation)), f"""{operation.lower()}($c)"""
        )

    @parameterized.expand(
        [
            ("GTE", ">="),
            ("LTE", "<="),
            ("NE", "!="),
            ("EQ", "="),
            ("LT", "<"),
            ("GT", ">"),
        ],
    )
    def test_comparisionFunctions(self, operation, sign):
        """
        Test compareFuncs method for comparison operators
        """
        query = QueryBuilder(self.dataCube)
        self.assertEqual(repr(query.compareFuncs(operation, 1)), f"""$c {sign} 1""")

    @parameterized.expand(
        [
            "SIN",
            "COS",
            "TAN",
            "SINH",
            "COSH",
            "TANH",
            "ARCSIN",
            "ARCCOS",
            "ARCTAN",
        ]
    )
    def test_trignometricFunctions(self, operation):
        """
        Test trigFuncs method for trignometric operations
        """
        query = QueryBuilder(self.dataCube)
        self.assertEqual(
            repr(query.trigFuncs(operation)), f"""{operation.lower()}($c)"""
        )

    @parameterized.expand(["COUNT", "MIN", "MAX", "AVG", "SUM", "SOME", "ALL"])
    def test_aggregationFunctions(self, operation):
        """
        Test Aggregation functions
        """
        query = QueryBuilder(self.dataCube)
        self.assertEqual(
            repr(query.aggregationFuncs(operation)), f"""{operation.lower()}($c)"""
        )

    def test_clipFunction(self):
        """
        Test clipping function
        """
        polygon = [
            [
                (-20.4270, 131.6931),
                (-28.4204, 124.1895),
                (-27.9944, 139.4604),
                (-26.3919, 129.0015),
            ],
            [
                (-20.4270, 131.6931),
                (-19.9527, 142.4268),
                (-27.9944, 139.4604),
                (-21.8819, 140.5151),
            ],
        ]
        query = QueryBuilder(self.dataCube)
        clipQuery = query.clip(clipType="Multipolygon", clippingValue=polygon)
        expectedStr = """clip($c, Multipolygon(((-20.427 131.6931,-28.4204 124.1895,-27.9944 139.4604,-26.3919 129.0015)),((-20.427 131.6931,-19.9527 142.4268,-27.9944 139.4604,-21.8819 140.5151))))"""
        self.assertEqual(repr(clipQuery), expectedStr)

    def test_scaleFunction(self):
        """
        Test scalar scaling function
        """
        query = QueryBuilder(self.dataCube)
        scaleQuery = query.scale(3)
        self.assertEqual(repr(scaleQuery), "scale($c, 3)")

    def test_composedQuery(self):
        """
        Test composed query.
        """
        query = self.dataCube.getQueryBuilder()
        query.subset(
            lat=53.08, long=8.80, startDate="2014-01", endDate="2014-12"
        ).arthimetic("ADD", 273.15).scale(5)

        composed_query = query.composeQueryFromOPS(encodingFormat="CSV")

        expected_query = """for $c in (AvgLandTemp) return encode(scale($c[Lat(53.08),Long(8.8),ansi("2014-01":"2014-12")] + 273.15, 5), "text/csv")"""
        self.assertEqual(composed_query, expected_query)

    @pytest.mark.slow
    def test_ReturnValueForQuery(self):
        """
        Test temperature above 15 degrees.
        """
        query_string = """for $c in (AvgLandTemp) return count($c[Lat(53.08), Long(8.80), ansi("2014-01":"2014-12")]> 15)"""
        direct_request_result = requests.post(
            "https://ows.rasdaman.org/rasdaman/ows", params={"query": query_string}
        ).content.decode("utf-8")

        query = self.dataCube.getQueryBuilder()
        query.subset(
            lat=53.08, long=8.80, startDate="2014-01", endDate="2014-12"
        ).compareFuncs("GT", 15).aggregationFuncs("COUNT")

        libraryRequestRes = self.dataCube.execute_query(query)

        self.assertEqual(direct_request_result, libraryRequestRes)

    @pytest.mark.slow
    def test_ReturnValueForQuery2(self):
        """
        Test average temp
        """
        query_string = """for $c in (AvgLandTemp) return avg($c[Lat(53.08), Long(8.80), ansi("2014-01":"2014-12")])"""
        direct_request_result = requests.post(
            "https://ows.rasdaman.org/rasdaman/ows", params={"query": query_string}
        ).content.decode("utf-8")

        query = self.dataCube.getQueryBuilder()
        query.subset(
            lat=53.08, long=8.80, startDate="2014-01", endDate="2014-12"
        ).aggregationFuncs("AVG")

        libraryRequestRes = self.dataCube.execute_query(query)

        self.assertEqual(direct_request_result, libraryRequestRes)

    @pytest.mark.slow
    def test_ReturnValueForQuery3(self):
        """
        Test average temp
        """
        query_string = """for $c in ( AvgLandTemp ) return encode($c[ansi("2014-07")], "image/png")"""
        direct_request_result = requests.post(
            "https://ows.rasdaman.org/rasdaman/ows", params={"query": query_string}
        ).content

        query = self.dataCube.getQueryBuilder()
        query.subset(startDate="2014-07")

        libraryRequestRes = self.dataCube.execute_query(
            query, encodingFormat="PNG", raw=True
        )

        self.assertEqual(direct_request_result, libraryRequestRes)


if __name__ == "__main__":
    unittest.main()
