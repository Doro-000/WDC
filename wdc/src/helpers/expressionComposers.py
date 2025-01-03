from .constants import ArthimeticToSignMap
from .types import ClippingTypes, PolygonType, MultipolygonType, LinestringType
from typing import Union


def composeBinaryOperations(op: str, value, composedOps: str, coverageVar: str):
    operationSign = ArthimeticToSignMap.get(op, None)

    if not operationSign:
        raise ValueError(f"Invalid operation: {op}")

    if not isinstance(value, (int, float, str)):
        value = repr(value)

    return (composedOps or coverageVar) + f" {operationSign} {value}"


def composeUnaryOperations(op: str, composedOps: str, coverageVar: str):
    return f"{op.lower()}({composedOps or coverageVar})"


def composeClipOperation(opObj: dict, composedOps: str, coverageVar: str):
    clipType: ClippingTypes = opObj["args"]["clipType"]
    clippingValue: Union[PolygonType, MultipolygonType, LinestringType] = opObj["args"][
        "clippingValue"
    ]
    formattedClippingValue = ""

    formatPoly = lambda polygon: [f"{vertice[0]} {vertice[1]}" for vertice in polygon]

    if clipType == "Polygon":
        polygonDefinition = formatPoly(clippingValue)
        polygonStr = ",".join(polygonDefinition)
        formattedClippingValue = f"POLYGON(({polygonStr}))"

    elif clipType == "Multipolygon":
        formattedPolys = []
        for poly in clippingValue:
            formattedPolys.append(f"""(({",".join(formatPoly(poly))}))""")
        formattedClippingValue = f"""Multipolygon({",".join(formattedPolys)})"""
    elif clipType == "LineString":
        formattedClippingValue = (
            f"""LineString({",".join(formatPoly(clippingValue))})"""
        )
    else:
        raise NotImplementedError(f"Clipping type {clipType} not supported!")

    crs = opObj["args"]["crs"]

    return f"clip({composedOps or coverageVar}, {formattedClippingValue}{',' + crs if crs else ''})"


def composeSwitchCase(opObj: dict):
    args = opObj["args"]
    conditions = args["conditions"]

    if len(conditions) == 1:
        raise ValueError("The number of the given conditions has to be greater than 1!")

    if args["returnType"] == "RGB":
        switchCaseWoDef = "\n".join(
            [
                f"case {repr(condition)} return {f'{{red: {returnValue[0]}; green: {returnValue[1]}; blue: {returnValue[2]}}}'}"
                for condition, returnValue in conditions[:-1]
            ]
        )

        defaultReturnVal = conditions[-1][1]

        return f"""(switch {switchCaseWoDef} \n {f"default return {f'{{red: {defaultReturnVal[0]}; green: {defaultReturnVal[1]}; blue: {defaultReturnVal[2]}}}'}"})"""
    else:
        raise NotImplementedError(
            "This feature currently only supports color return values!"
        )
