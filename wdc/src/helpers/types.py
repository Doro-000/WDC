from typing import TypedDict, Literal, NotRequired, Union, Tuple, Any


class NetworkRequestResult(TypedDict):
    """
    Type representing the return value from a network request.

    Attributes:
        success (bool): Indicates whether the request was successful.
        result (any): The result of the network request.
        errorCode (Optional[ErrorCodeType]): Error code if the request was unsuccessful.
        errorDetails (Optional[any]): Details about the error if the request was unsuccessful.
    """

    success: bool
    result: NotRequired[Any]
    httpCode: int
    httpError: NotRequired[str]
    errorDetails: NotRequired[Any]


class SubsetType(TypedDict):
    """
    Type representing a datacube slice.

    Attributes:
        lat (Optional[Union[float, Tuple[int, int]]]): Latitude range or value.
        long (Optional[Union[float, Tuple[int, int]]]): Longitude range or value.
        startDate (str): Start date for the subset.
        endDate (Optional[str]): End date for the subset.
    """

    lat: NotRequired[Union[float, tuple[int, int]]]
    long: NotRequired[Union[float, tuple[int, int]]]
    startDate: str
    endDate: NotRequired[str]


# Define literal types for various arithmetic operations.
ArithmeticOperationTypes = Literal[
    "ADD", "SUB", "PROD", "DIV", "ABS", "ROUND", "MOD", "FLOOR", "CEIL"
]

# Define literal types for various exponential operations.
ExponentialOperationTypes = Literal["EXP", "LOG", "LN", "POW", "SQRT"]

# Define literal types for various trigonometric operations.
TrigonometricOperationTypes = Literal[
    "SIN", "COS", "TAN", "SINH", "COSH", "TANH", "ARCSIN", "ARCCOS", "ARCTAN"
]

# Define literal types for various comparison operations.
ComparisonOperationTypes = Literal["GTE", "LTE", "GT", "LT", "EQ", "NE"]

# Define literal types for various aggregation operations.
AggregationOperationTypes = Literal["COUNT", "MIN", "MAX", "AVG", "SUM", "SOME", "ALL"]

# Define literal types for different clipping types.
ClippingTypes = Literal["Polygon", "Multipolygon", "LineString"]

# Define types for geometric shapes.
PolygonType = list[Tuple[float, float]]
MultipolygonType = list[PolygonType]
LinestringType = PolygonType

# Define supported return types
ReturnTypes = Literal["CSV", "PNG", "JPEG"]
