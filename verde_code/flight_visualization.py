"""
Module Description
==================
This module contains the functions used to visualize graphs in our project.

Copyright and Usage Information
===============================
This file is provided exclusively for the use and benefit of customers of VerdeVoyage. Any form of
distribution, reproduction, or modification of this code outside of its intended use within the VerdeVoyage
platform is strictly prohibited. All rights reserved.

This file is Copyright (c) 2024 VerdeVoyage
"""

import plotly.graph_objects as go
import numpy as np
import data_classes


def visualize_new_graph(graph: data_classes.Graph, airport_coords: dict[str, tuple[float, float]],
                        home_airport: str = None, dest_airport: str = None) -> None:
    """
    Visualize the given graph using plotly.

    Preconditions:
        - home_airport in airport_coords and dest_airport in airport_coords
        - dest_airport is None or home_airport is not None
        - The given graph is created based on the given specifications for home_airport and dest_airport.
    """
    graph_figure = go.Figure()

    ocean_color = "rgb(33, 158, 188)"  # blue for ocean
    land_color = "rgb(128, 237, 153)"  # green for land
    path_color = "rgb(242, 188, 49)"  # Gold for flight paths
    marker_color = "rgb(229, 56, 59)"  # Red for markers
    text_color = "rgb(85, 166, 48)"  # Green for Text

    # If dest_airport is given, by the preconditions, home_airport must also be given.
    # If this is the case, then visualize at most 5 edges between home_airport and dest_airport.
    if dest_airport is not None:
        lat1, lon1 = airport_coords[home_airport]
        lat2, lon2 = airport_coords[dest_airport]
        v1 = graph.get_vertex(home_airport)
        v2 = graph.get_vertex(dest_airport)
        flights = list(v1.neighbours[v2].keys())

        # Visualize at most 5 paths between home_airport and dest_airport
        for i in range(min(5, len(flights))):
            lon_array, lat_array = create_curve_path(lon1, lat1, lon2, lat2, curve_height=((-1) ** i) * (0.05 * i))
            flight = flights[i]
            flight_name = f"{flight[0]}: {flight[1]}"

            # Add a line between home airport and dest_airport
            graph_figure.add_trace(go.Scattergeo(
                lon=lon_array,
                lat=lat_array,
                mode='lines',
                line={"width": 2, "color": path_color},
                name=flight_name                                 # Set the name for the flight path
            ))

        # Add a marker to each airport, showing its coordinates and airport code.
        for airport in [home_airport, dest_airport]:
            graph_figure.add_trace(go.Scattergeo(
                lon=[airport_coords[airport][1]],
                lat=[airport_coords[airport][0]],
                mode='markers',
                marker={"size": 5, "color": marker_color},
                name=airport
            ))

    # If only home_airport is given, then visualize the connections between home_airport and its neighbours.
    elif home_airport is not None:
        visited = set()
        v1 = graph.get_vertex(home_airport)
        lat1, lon1 = airport_coords[home_airport]
        visited.add(v1)

        # Add a line from home_airport to each of its neighbours.
        for v2 in v1.neighbours:
            if v2 not in visited:
                lat2, lon2 = airport_coords[v2.airport_code]
                flight_name = f"{home_airport} to {v2.country_name}"

                graph_figure.add_trace(go.Scattergeo(
                    lon=[lon1, lon2],
                    lat=[lat1, lat2],
                    mode='lines',
                    line={"width": 2, "color": path_color},
                    name=flight_name
                ))

                visited.add(v2)

        # Add a marker to each airport, showing its coordinates and airport code.
        for v in visited:
            lat, lon = airport_coords[v.airport_code]
            graph_figure.add_trace(go.Scattergeo(
                lon=[lon],
                lat=[lat],
                mode='markers',
                marker={"size": 5, "color": marker_color},
                name=v.airport_code
            ))

    # If home_airport is not given, then visualize all connections between all the vertices in the graph.
    else:
        # Go through every neighbour of every vertex in the graph, and add a line connecting the
        # neighbour to the vertex.
        visited = set()
        for v1 in graph.all_verticies():                    # graph.all_vertices() returns a set of all vertex objects
            lat1, lon1 = airport_coords[v1.airport_code]
            for v2 in v1.neighbours:
                if (v1, v2) not in visited and (v2, v1) not in visited:
                    lat2, lon2 = airport_coords[v2.airport_code]
                    flight_name = f"{v1.airport_code} to {v2.country_name}"

                    graph_figure.add_trace(go.Scattergeo(
                        lon=[lon1, lon2],
                        lat=[lat1, lat2],
                        mode='lines',
                        line={"width": 2, "color": path_color},
                        name=flight_name
                    ))

                    visited.add((v1, v2))

            # Add a marker to the vertex, showing its coordinates and airport code.
            graph_figure.add_trace(go.Scattergeo(
                lon=[lon1],
                lat=[lat1],
                mode='markers',
                marker={"size": 5, "color": marker_color},
                name=v1.airport_code
            ))

    # Add the following properties to the plot.
    graph_figure.update_layout(
        title_text='<b>VerdeVoyage: Fly the Dream, Keep it Green </b>',
        title_font={"size": 24, "color": text_color},
        showlegend=True,
        legend_title_text='Flight Paths',
        legend_title_font={"color": text_color},
        legend_font={"color": text_color},
        geo={"projection_type": 'orthographic',
             "showland": True,
             "landcolor": land_color,
             "countrycolor": text_color,
             "oceancolor": ocean_color,
             "lakecolor": ocean_color,
             "showocean": True
             }
    )

    graph_figure.show()


def create_curve_path(lon1: float, lat1: float, lon2: float, lat2: float,
                      num_points: int = 100, curve_height: float = 0) -> tuple[np.array, np.array]:
    """
    Rwturn a curved path between (lat1, lon1) and (lat2, lon2) based on the given curve_height.
    """

    # Convert the values to radians because numpy functions work with radian values.
    lon1, lat1, lon2, lat2 = np.radians(lon1), np.radians(lat1), np.radians(lon2), np.radians(lat2)

    # Create the given number of points between lat1 and lat2, and between lon1 and lon2
    lat_array = np.linspace(lat1, lat2, num_points)
    lon_array = np.linspace(lon1, lon2, num_points)

    # To add curvature, we will use the sin function.
    # We create given number of points between 0 and pi, and apply sin to it.
    # This will create a sin graph between 0 and pi, which is naturally a curve.
    # Then, we multiply by curve_height to stretch or compress the graph,
    # giving us distinguishable paths between 0 and pi.
    modifier = np.sin(np.linspace(0, np.pi, num_points)) * curve_height

    # If the latitude distance between the endpoints is greater than the longitude distance,
    # then we add the modifier to the line between lon1 and lon2.
    # Otherwise, we add the modifier to the line between lat1 and lat2.
    # Notice that the endpoints (lat1, lon1) and (lat2, lon2) are not changed because
    # at the endpoints on the sin graph (0 and pi), the value is 0.
    if abs(lat1 - lat2) > abs(lon1 - lon2):
        lon_array = lon_array + modifier
    else:
        lat_array = lat_array + modifier

    # Convert back to degrees and return.
    return np.degrees(lon_array), np.degrees(lat_array)


if __name__ == '__main__':
    # import python_ta.contracts
    # python_ta.contracts.check_all_contracts()
    import python_ta

    python_ta.check_all(config={
        'max-line-length': 170,
        'disable': ['E1136', 'W0221', 'R0913'],
        'extra-imports': ['plotly.graph_objects', 'data_classes', 'numpy'],
        'max-nested-blocks': 4,
        'max-locals': 30,
        'max-statements': 80
    })
