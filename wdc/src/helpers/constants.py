VALID_RETURN_TYPES = {"CSV": "text/csv", "PNG": "image/png", "JPEG": "image/jpeg"}

# Supported Binary operations
BinaryOperations = {
    "ADD",
    "SUB",
    "PROD",
    "DIV",
    "MOD",
    "GTE",
    "LTE",
    "GT",
    "LT",
    "EQ",
    "NE",
}

# Supported Unary operations
UnaryOperations = {
    "COUNT",
    "ROUND",
    "ABS",
    "SUM",
    "SOME",
    "ALL",
    "MIN",
    "MAX",
    "AVG",
    "LN",
    "EXP",
    "LOG",
    "SQRT",
    "FLOOR",
    "CEIL",
    "SIN",
    "COS",
    "TAN",
    "SINH",
    "COSH",
    "TANH",
    "ARCSIN",
    "ARCCOS",
    "ARCTAN",
}

ArthimeticToSignMap = {
    "ADD": "+",
    "SUB": "-",
    "PROD": "*",
    "DIV": "/",
    "MOD": "%",
    "GTE": ">=",
    "GT": ">",
    "LTE": "<=",
    "LT": "<",
    "EQ": "=",
    "NE": "!=",
}
