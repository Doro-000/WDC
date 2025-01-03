from typing import Union, Tuple
from .DatabaseConnection import DatabaseConnection
from .Datacube import Datacube


def temperature_above_threshold(coverageId: str, threshold: Union[int, float]):
    """
    prepare a query to compute the data points in a coverage above a certain temprature
    Args:
        coverageId (str): coverage to execute query against
        threshold (float): Temperature threshold to compare against.
    """
    conn = DatabaseConnection()
    cube = Datacube(conn, coverageId)
    query = cube.getQueryBuilder(debug=True)

    query.subset(
        lat=53.08, long=8.80, startDate="2014-01", endDate="2014-12"
    ).compareFuncs("GT", threshold).aggregationFuncs("COUNT")

    queryRes = cube.execute_query(query)
    return queryRes


def mean_air_summer_temp_cube():
    """
    Configure the cube to calculate the average air temperature for the summer months.
    """
    conn = DatabaseConnection()
    cube = Datacube(conn, "AvgLandTemp")
    query = cube.getQueryBuilder(debug=True)

    query.subset(startDate="2014-06", endDate="2014-08").aggregationFuncs("AVG")

    queryRes = cube.execute_query(query)
    return queryRes


def time_series_analysis(lat, long, time_period: Tuple[str, str]):
    """
    Perform time series analysis on the datacube for the specified period.
    Args:
        time_period (str): The time period for the analysis.
    """
    conn = DatabaseConnection()
    cube = Datacube(conn, "AvgLandTemp")
    query = cube.getQueryBuilder(debug=True)

    query.subset(lat=lat, long=long, startDate=time_period[0], endDate=time_period[1])

    queryRes = cube.execute_query(query, encodingFormat="CSV")
    return queryRes


def spatial_query(latitude, longitude, startDate):
    """
    Perform a spatial query around a specific location
        latitude (float): Latitude of the data point.
        longitude (float): Longitude of the data point.
        startDate (str): timestamp of the data point
    """
    conn = DatabaseConnection()
    cube = Datacube(conn, "AvgLandTemp")
    query = cube.getQueryBuilder(debug=True)

    query.subset(lat=latitude, long=longitude, startDate=startDate)

    return cube.execute_query(query, raw=True)


if __name__ == "__main__":
    tempQuery = temperature_above_threshold("AvgLandTemp", 15)
    print(tempQuery, "\n\n")

    meanQuery = mean_air_summer_temp_cube()
    print(meanQuery, "\n\n")

    timeSeriesQuery = time_series_analysis(53.08, 8.80, ("2014-01", "2015-01"))
    print(timeSeriesQuery, "\n\n")

    spatialQuery = spatial_query(53.08, 8.80, "2014-07")
    print(spatialQuery, "\n\n")
