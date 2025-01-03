# Datacube Query Library (WDC)

The Python code in the `wdc.py` file provides a library for querying a datacube, a multidimensional dataset, through HTTP connections to a database server. This README provides an overview of the code's functionality, usage, operations, error handling, and additional notes.

# File Structure

- wdc
  - src
    - \_\_init\_\_.py
    - DatabaseConnection.py
    - Datacube.py
    - exampleQueries.py
    - QueryBuilder.py
    - helpers
      - \_\_init\_\_.py
      - constants.py
      - expressionComposers.py
      - types.py
      - utils.py
  - test
    - test_DatabaseConnection.py
    - test_Datacube.py
- requirements.txt
- .gitignore
- demo.ipynb
- README.md

# DatabaseConnection Class

Handles HTTP connections to a database server for sending queries.

## Attributes

- `endpoint_url` (str): The endpoint URL of the database server.

## Methods

#### `__init__(endpoint_url: str = "https://ows.rasdaman.org/rasdaman/ows")`

Initialize the connection with the URL of the database endpoint.

- `endpoint_url` (str, optional): The endpoint URL of the database server. Defaults to `"https://ows.rasdaman.org/rasdaman/ows"`.

### `send_request(query: str) -> dict`

Send a POST request to the database endpoint with the provided query.

#### Parameters

- `query` (str): The database query to send.

#### Returns

A dictionary containing the result of the network request, with the following keys:

- `success` (bool): True if the request was successful, False otherwise.
- `result` (bytes or None): The content of the response body if the request was successful, None otherwise.
- `httpCode` (int or None): The HTTP status code of the response if available, None otherwise.
- `httpError` (str or None): The error message if an HTTP error occurred, None otherwise.
- `errorDetails` (bytes or None): The details of the error response if available, None otherwise.

# Datacube Class

Manages operations on a datacube such as querying data through the DatabaseConnection.

## Constructor

### `__init__(dbc: DatabaseConnection, coverageId: str)`

Initialize the Datacube instance with a DatabaseConnection.

#### Parameters

- `dbc` (DatabaseConnection): The DatabaseConnection instance to use for executing queries.
- `coverageId` (str): The identifier of the datacube coverage.

## Methods

### `getQueryBuilder(debug: bool = False) -> QueryBuilder`

Returns a QueryBuilder instance for composing queries on the datacube.

#### Parameters

- `debug` (bool, optional): If True, debug information will be included in the query. Defaults to False.

#### Returns

- `QueryBuilder`: An instance of QueryBuilder for composing queries.

### `execute_query(queryObject: QueryBuilder, encodingFormat: Optional[ReturnTypes] = None, raw: bool = False) -> Union[bytes, Any]`

Executes the provided query using the DatabaseConnection.

#### Parameters

- `queryObject` (QueryBuilder): The QueryBuilder instance representing the query to execute.
- `encodingFormat` (Optional[ReturnTypes], optional): The desired encoding format of the query result. Defaults to None.
- `raw` (bool, optional): If True, returns the raw bytes object directly from the network request. Defaults to False.

#### Returns

- Union[bytes, Any]: If raw is True, returns a bytes object representing the raw response from the network request. Otherwise, returns the decoded result, which could be an image (PNG, JPEG), a pandas DataFrame (CSV), or decoded text.

# QueryBuilder Class

A class representing the query for a WCPS server.

## Constructor

### `__init__(coverageId: str, debug: bool = False)`

Initialize a QueryBuilder instance with a coverage ID and debug mode.

#### Parameters

- `coverageId` (str): The identifier of the associated datacube coverage.
- `debug` (bool, optional): If True, every query sent to the server will be printed out. Defaults to False.

## Methods

### `composeQueryFromOPS(encodingFormat: Optional[ReturnTypes] = None) -> str`

Composes the final query string from the given operations.

#### Parameters

- `encodingFormat` (Optional[ReturnTypes], optional): The desired encoding format of the query result. Defaults to None.

#### Returns

- `str`: An executable WCPS query string.

### `pop()`

Removes the last operation from the operation list.

### `reset()`

Resets the operation stack to reuse the instance for another query.

### Operations

The following methods are used to construct various WCPS operations within the query:

- `subset(**kwargs: Unpack[SubsetType]) -> QueryBuilder`: Slice operation on the datacube.
- `arthimetic(operation: ArithmeticOperationTypes, value: Optional[Union[float, str, int, bool, Self]] = None) -> QueryBuilder`: Arithmetic operations.
- `expFuncs(operation: ExponentialOperationTypes, value: Optional[Union[float, str, int, bool, Self]] = None) -> QueryBuilder`: Exponential operations.
- `compareFuncs(operation: ComparisonOperationTypes, value: Union[float, str, int, bool, Self]) -> QueryBuilder`: Comparison operations.
- `trigFuncs(operation: TrigonometricOperationTypes) -> QueryBuilder`: Trigonometric operations.
- `aggregationFuncs(operation: AggregationOperationTypes) -> QueryBuilder`: Aggregation operations.
- `clip(clipType: ClippingTypes, clippingValue: Union[PolygonType, MultipolygonType, LinestringType], crsValue: Optional[str] = None) -> QueryBuilder`: Clipping operation.
- `conditionalReturn(conditions, returnType="RGB") -> QueryBuilder`: Switch case operation.
- `scale(scalarValue: float | int) -> QueryBuilder`: Scaling operation.

# Testing

For the testing of the library, we have used the 'pytest' package and the 'unittest' module. The tests are written in the `/wdc/test` folder. To run the tests, you can use the following command:

Make sure you are in the wdc folder

```bash
Sprint3_Pair12\Sprint_2\wdc> python -m pytest
```

The tests cover the following classes and methods:

### Unit tests for the DatabaseConnection class.

- `setUp()`: Set up necessary objects for testing.
- `test_send_request_success()`: Test the send_request method for a successful request.
- `test_send_request_http_error()`: Test the send_request method when an HTTP error occurs.
- `test_send_request_timeout_error()`: Test the send_request method when a timeout error occurs.
- `test_send_request_connection_error()`: Test the send_request method when a connection error occurs.
- `test_invalid_url()`: Test initializing DatabaseConnection with an invalid URL.
- `test_send_request_custom_url()`: Test the send_request method with a custom endpoint URL.

### TestDatacube

- `setUp()`: Create a mock DatabaseConnection object for testing.
- `test_initialization()`: Test if Datacube is initialized correctly.
- `test_get_query_builder()`: Test the getQueryBuilder method.
- `test_execute_query()`: Test the execute_query method.

For more information on the usage of the library, please refer to the`demo.ipynb` notebook in the root directory.
