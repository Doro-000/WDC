from .types import NetworkRequestResult, SubsetType
from typing import Unpack

from PIL import Image
from io import BytesIO, StringIO
from pandas import DataFrame, read_csv


def getSubset(**kwargs: Unpack[SubsetType]):
    """
    A convenience function to format slice operations.

    Args:
        **kwargs: Keyword arguments representing subset parameters.

    Returns:
        str: Formatted subset string.

    Raises:
        ValueError: If start date is not specified.
    """
    lat, long, startDate, endDate = [
        kwargs.get(key, None) for key in ["lat", "long", "startDate", "endDate"]
    ]

    filters = []
    if lat:
        if type(lat) is tuple:
            filters.append(f"Lat({lat[0]}:{lat[1]})")
        else:
            filters.append(f"Lat({lat})")

    if long:
        if type(long) is tuple:
            filters.append(f"Long({long[0]}:{long[1]})")
        else:
            filters.append(f"Long({long})")

    if startDate and not endDate:
        filters.append(f'ansi("{startDate}")')
    elif startDate and endDate:
        filters.append(f'ansi("{startDate}":"{endDate}")')
    else:
        raise ValueError("Start Date has to be specified!")

    return f'[{",".join(filters)}]'


def decodeImage(requestRes: NetworkRequestResult) -> Image.Image:
    """
    Decode image from a NetworkRequestResult.

    Args:
        requestRes (NetworkRequestResult): Network request result containing image data.

    Returns:
        Image: Decoded image object.

    Raises:
        ValueError: If the provided request is not successful.
    """
    if requestRes.get("success", False):
        img = Image.open(BytesIO(requestRes.get("result", None)))
        return img
    else:
        raise ValueError("Provided request is not successful")


def decodeText(requestRes: NetworkRequestResult) -> str:
    """
    Decode text from a NetworkRequestResult.

    Args:
        requestRes (NetworkRequestResult): Network request result containing text data.

    Returns:
        str: Decoded text string.

    Raises:
        ValueError: If the provided request is not successful.
    """
    if requestRes["success"]:
        return requestRes.get("result", b"").decode("utf-8")
    else:
        raise ValueError("Provided request is not successful")


def decodeCsv(requestRes: NetworkRequestResult) -> DataFrame:
    """
    Decode CSV data from a NetworkRequestResult.

    Args:
        requestRes (NetworkRequestResult): Network request result containing CSV data.

    Returns:
        DataFrame: Decoded CSV data as a pandas DataFrame.

    Raises:
        ValueError: If the provided request is not successful.
    """
    if requestRes["success"]:
        return read_csv(StringIO(decodeText(requestRes)), header=None).transpose()
    else:
        raise ValueError("Provided request is not successful")
