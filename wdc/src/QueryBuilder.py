from .helpers.types import (
    SubsetType,
    ArithmeticOperationTypes,
    ExponentialOperationTypes,
    ComparisonOperationTypes,
    TrigonometricOperationTypes,
    AggregationOperationTypes,
    ClippingTypes,
    PolygonType,
    MultipolygonType,
    LinestringType,
    ReturnTypes,
)
from .helpers.utils import getSubset

from .helpers.constants import (
    BinaryOperations,
    UnaryOperations,
    VALID_RETURN_TYPES,
)

from .helpers.expressionComposers import (
    composeBinaryOperations,
    composeClipOperation,
    composeSwitchCase,
    composeUnaryOperations,
)

from typing import Unpack, Optional, Union, Self


class QueryBuilder:
    """A class representing the query for a WCPS server

    Parameters:
        dco (DataCubeObject): The associated datacube which the query is going to be executed upon
        debug (bool): If true every query sent to the server will be printed out
    """

    def __init__(self, coverageId: str, debug: bool = False):
        self.coverageId = coverageId
        self.debug = debug

        self.__operations = []
        self.__coverageVar = "$c"

    def __repr__(self):
        """String representation of the current query

        Returns:
            stringQuery (str): an incomplete query string
        """
        composedOps = ""

        for operation in self.__operations:
            op = operation["OP"]

            if op == "SLICE":
                composedOps = (composedOps or self.__coverageVar) + getSubset(
                    **operation["args"]
                )
            elif op in BinaryOperations:
                composedOps = composeBinaryOperations(
                    op,
                    operation["args"]["value"],
                    composedOps or self.__coverageVar,
                    self.__coverageVar,
                )

            elif op in UnaryOperations:
                composedOps = composeUnaryOperations(
                    op, composedOps or self.__coverageVar, self.__coverageVar
                )

            elif op in {"POW", "SCALE"}:
                composedOps = f"{op.lower()}({composedOps or self.__coverageVar}, {operation['args']['value']})"

            elif op == "CLIP":
                composedOps = composeClipOperation(
                    operation, composedOps or self.__coverageVar, self.__coverageVar
                )

            elif op == "SWITCH_CASE":
                composedOps = composeSwitchCase(operation)

            else:
                raise NotImplementedError(f"Operation: {op} is not implemented!")

        return composedOps

    def composeQueryFromOPS(self, encodingFormat: Optional[ReturnTypes] = None):
        """Composes final query string from the given operations

        Parameters:
            encodingFormat (str): The desired encoding format of our query result

        Returns:
            finalQuery (str): An executable WCPS query string
        """
        if encodingFormat and encodingFormat not in VALID_RETURN_TYPES:
            raise ValueError(
                f"Invalid return type. Valid types are: {list(VALID_RETURN_TYPES.keys())}"
            )

        composedOps = repr(self)

        if encodingFormat:
            composedOps = f'encode({composedOps or self.__coverageVar}, "{VALID_RETURN_TYPES[encodingFormat]}")'

        finalQuery = f"for $c in ({self.coverageId}) return {composedOps}"

        ## Print composed query if debug mode is on
        if self.debug:
            print(finalQuery)

        return finalQuery

    def pop(self):
        """Removes last operation from operation list"""
        self.__operations.pop()

    def reset(self):
        """Resets operation stack to reuse instance for another query"""
        self.__operations = []

    # Operations
    def subset(self, **kwargs: Unpack[SubsetType]):
        """Slice Operation on the data cube
        ex: $c[Lat(53.08),ansi("2014-07")]

        Parameters:
            lat optional(float | tuple(int, int)): Latitude information
            long optional(float | tuple(int, int)): Longitude information
            startDate (str): Date information
            endDate optional(str): End Date information

        Returns:
            self: current query for chaining more operations
        """
        self.__operations.append(
            {
                "OP": "SLICE",
                "args": kwargs,
            }
        )
        return self

    def arthimetic(
        self,
        operation: ArithmeticOperationTypes,
        value: Optional[Union[float, str, int, bool, Self]] = None,
    ):
        """Artihmetic Operations
        ex: $c[Lat(53.08), Long(8.80), ansi("2014-01":"2014-12")] + 273.15

        Parameters:
            operation OneOf("ADD"| "SUB" | "PROD" | "DIV" | "ABS" | "ROUND" | "MOD" | "FLOOR" | "CEIL"): Desired Operator
            value float | str | int | QueryBuilder: Optional Right hand side static value, defaults to zero

        Returns:
            self: current query for chaining more operations
        """
        if operation in {"ADD", "SUB", "PROD", "DIV", "MOD"} and value == None:
            raise ValueError(f"Value required for operation: {operation}")

        self.__operations.append({"OP": operation, "args": {"value": value}})
        return self

    def expFuncs(
        self,
        operation: ExponentialOperationTypes,
        value: Optional[Union[float, str, int, bool, Self]] = None,
    ):
        """Exponential Operations
        ex: pow($c[Lat(53.08), Long(8.80), ansi("2014-01":"2014-12")] + 273.15, 2)

        Parameters:
            operation OneOf("EXP", "LOG", "LN", "POW", "SQRT"): Desired Operator
            value float | str | int | QueryBuilder: Only required for POW, determines the exponent

        Returns:
            self: current query for chaining more operations
        """
        if operation == "POW" and value == None:
            raise ValueError(f"Value required for operation: {operation}")

        self.__operations.append({"OP": operation, "args": {"value": value}})
        return self

    def compareFuncs(
        self,
        operation: ComparisonOperationTypes,
        value: Union[float, str, int, bool, Self],
    ):
        """Comparision Operations
        ex: $c[Lat(53.08), Long(8.80), ansi("2014-01":"2014-12")] < 23

        Parameters:
            operation OneOf("GTE", "LTE", "GT", "LT", "EQ", "NE"): Desired Operator
            value float | str | int | QueryBuilder: value to compare against

        Returns:
            self: current query for chaining more operations
        """

        self.__operations.append({"OP": operation, "args": {"value": value}})
        return self

    def trigFuncs(self, operation: TrigonometricOperationTypes):
        """Trignometric Operations
        ex: sin([coverageExpression]), cos($c[Lat(53.08), Long(8.80), ansi("2014-01":"2014-12")])

        Parameters:
            operation OneOf("SIN", "COS", "TAN", "SINH", "COSH", "TANH", "ARCSIN", "ARCCOS", "ARCTAN"): Desired Operator

        Returns:
            self: current query for chaining more operations
        """

        self.__operations.append({"OP": operation})
        return self

    def aggregationFuncs(self, operation: AggregationOperationTypes):
        """Aggregation Operations
        ex: count($c[Lat(53.08), Long(8.80), ansi("2014-01":"2014-12")])

        Parameters:
            operation OneOf("COUNT", "MIN", "MAX", "AVG", "SUM", "SOME", "ALL"): Desired Operator

        Returns:
            self: current query for chaining more operations
        """
        self.__operations.append({"OP": operation})
        return self

    def clip(
        self,
        clipType: ClippingTypes,
        clippingValue: Union[PolygonType, MultipolygonType, LinestringType],
        crsValue: Optional[str] = None,
    ):
        """Clipping Operation
        ex: clip(c,
                POLYGON((
                           -12.3829 132.0117, -33.4314 120.4102, -18.8127 148.5352,
                           -22.7559 118.4766, -36.3151 143.7891
                       ))
                )

        Parameters:
            clipType OneOf("Polygon", "Multipolygon", "LineString"):
            clippingValue OneOf[PolygonType, MultipolygonType, LinestringType]: An array of tuples, where each entry represents a coordinate
            crsValue: Optional Crs URL or string

        Returns:
            self: current query for chaining more operations
        """

        self.__operations.append(
            {
                "OP": "CLIP",
                "args": {
                    "clipType": clipType,
                    "clippingValue": clippingValue,
                    "crs": crsValue,
                },
            }
        )
        return self

    def conditionalReturn(self, conditions, returnType="RGB"):
        """Switch Case operation

        Parameters:
            conditions list[tuple[QueryBuilder, tuple[int, int, int]]]:
                A list of QueryBuilder instances and RGB return values.

                The QueryBuilder instances represent each case of the condition

                The last list entry will be used as the default condition.

                The conditions list has to have more than one element

            returnType: return type for each condition, currently only supports "RGB" for color return values
        Returns:
            self: current query for chaining more operations
        """
        self.__operations.append(
            {
                "OP": "SWITCH_CASE",
                "args": {"returnType": returnType, "conditions": conditions},
            }
        )
        return self

    def scale(self, scalarValue: float | int):
        """Scaling Operation
        ex: scale( covExpr, number )

        Parameters:
            value float | int: static value to scale the coverage expression with

        Returns:
            self: current query for chaining more operations
        """
        self.__operations.append({"OP": "SCALE", "args": {"value": scalarValue}})
        return self
