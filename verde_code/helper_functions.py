""" Verde Voyage: ALL computation and helper fucntions for a green flight path result

Module Descriptions
==================
This module is designed as the core of the computation and the behind the scences of our VerdeVoyage platform.
In this module, we create functions that provide a flight score based on given parameters, return optimal flight routes,
create various graphs, provide educational tips, and further includes our run_voyage()
function that takes the user through a vacation planning journey.

Copyright and Usage Information
===============================
This file is provided exclusively for the use and benefit of customers of VerdeVoyage. Any form of
distribution, reproduction, or modification of this code outside of its intended use within the VerdeVoyage
platform is strictly prohibited. All rights reserved.

This file is Copyright (c) 2024 Verde Voyage

"""
import csv
import random
import data_classes
import flight_visualization


def run_voyage() -> None:
    """
    This is a function that runs our entire program through the python console. Solely running this function will
    show the culmulative results of our project.
    """
    # Load in important details from our dataset regarding travel destinations, and airport locations
    print('Welcome to Verde Voyage! This is your ultimate eco-conscious dream vacation planner! \n')
    home_airports, _, dest_airports, dest_countries = countries_and_airports('CSV Files/flight_data.csv')
    airport_coords = get_airport_coordinates()

    home_airport = input('What is your home airport? (Enter airport code) ').strip().upper()
    while home_airport not in home_airports:
        print('We are sorry! We do not have enough information on this airport. We are constantly trying '
              'to expand our reach. Please try a different airport.')

        home_airport = input('What is your home airport? (Enter airport code) ').strip().upper()

    # Display the graph from home_airport to all connecting airports.
    print("\nHere are all the connecting airports from your home airport.\n")
    graph = create_graph(home_airport=home_airport, airport_coords=airport_coords)
    flight_visualization.visualize_new_graph(graph, home_airport=home_airport, airport_coords=airport_coords)

    # Ask the user if they would like personalized travel suggestions
    questionare = input('Would you like to answer a few questions to get suggestions for travel destinations '
                        'that are perfect for you? (Y/N) ').strip().upper()
    questionare_bool = False
    matching_countries = None
    while questionare == 'Y':
        questionare_bool = True
        matching_countries = data_classes.run_country_matchmaker('CSV Files/country_traits.csv')
        if matching_countries is None:
            print("There are no countries that match with those specific traits.")
        else:
            print(f"The following countries match your prefereances {matching_countries}")
        questionare = input('Would you like to take the questionare again? (Y/N) ').strip().upper()
    print()
    if questionare_bool and len(matching_countries) > 1:
        print("\nHere are all the matching countries to your preferences from your home airport. ")
        graph = create_graph(home_airport=home_airport, dest_countries=matching_countries,
                             airport_coords=airport_coords)
        flight_visualization.visualize_new_graph(graph, home_airport=home_airport, airport_coords=airport_coords)

    print()
    dest_country = input('Which country would you like to fly to? ').strip().lower()
    while dest_country not in dest_countries:
        print('We are sorry! We do not have enough information on this country. We are constantly trying '
              'to expand our reach. Please try a different country.')

        dest_country = input('Which country would you like to fly to? ').strip().lower()

    # Display the graph from home_airport to all airports in dest_country.
    print("\nHere are all the connecting airports in your chosen destination country from "
          "your home airport.\n")
    graph = create_graph(home_airport=home_airport, dest_countries=[dest_country], airport_coords=airport_coords)
    flight_visualization.visualize_new_graph(graph, home_airport=home_airport, airport_coords=airport_coords)

    dest_airport = input('Which airport would you like to fly to? (Enter airport code) ').strip().upper()
    while dest_airport not in dest_airports:
        print('We are sorry! We do not have enough information on this airport. We are constantly trying '
              'to expand our reach. Please try a different airport.')

        dest_airport = input('Which airport would you like to fly to? (Enter airport code) ').strip().upper()

    # Display the graph from home_airport to dest_airport with at least 5 flights highlighted.
    print("\nHere are a few flight routes for travelling from your home country to your chosen "
          "destination country.\n")
    graph = create_graph(home_airport=home_airport, dest_airport=dest_airport, airport_coords=airport_coords)
    flight_visualization.visualize_new_graph(graph,
                                             home_airport=home_airport, dest_airport=dest_airport,
                                             airport_coords=airport_coords)

    print()
    emissions_weight = float(input('How important to you is lowering your carbon footprint on a scale of 5 - 10: '))
    while emissions_weight < 5 or emissions_weight > 10:
        print('Invalid input. The value must be between 5 and 10.')
        emissions_weight = float(input('How important to you is lowering your carbon footprint on a scale of 5 - 10: '))

    price_weight = float(input('How important to you is having the lowest ticket price from a scale of 0 - 5:  '))
    while price_weight < 0 or price_weight > 5:
        print('Invalid input. The value must be between 0 and 5.')
        price_weight = float(input('How important to you is having the lowest ticket price from a scale of 0 - 5:  '))

    stops_weight = float(input('Rate the importance of having a minimal number of stops on your flight '
                               'from a scale of 0 - 5:  '))
    while stops_weight < 0 or stops_weight > 5:
        print('Invalid input. The value must be between 0 and 5.')
        stops_weight = float(input('Rate the importance of having a minimal number of stops on your flight '
                                   'from a scale of 0 - 5:  '))

    # Creating normalized values for each input
    total_weight = emissions_weight + price_weight + stops_weight
    weights = (price_weight / total_weight), (stops_weight / total_weight), (emissions_weight / total_weight)

    # Calculate and display the most optimal routes based on what is the most important to the user
    routes = optimal_routes(graph, home_airport, dest_airport, weights)

    print('\nHere are the most optimal flight packages from your home airport to your chosen destination airport: ')
    print()
    for i in range(len(routes)):
        route = routes[i]
        print('Flight Package', i + 1)
        print(f"Airline: {route[0][0]}")
        print(f"Aircrafts: {route[0][1]}")
        print(f"Price: ${route[1]} USD")
        print(f"Number of stops: {route[2]}")
        print(f"Carbon Emissions: {route[3]}g")
        print()

    chosen_route_num = int(input(f'Which flight package would you like to choose? (1 - {len(routes)}) '))
    while chosen_route_num > len(routes) or chosen_route_num < 1:
        print('Invalid input.')
        chosen_route_num = int(input(f'Which flight package would you like to choose? (1 - {len(routes)}) '))
    chosen_route = routes[chosen_route_num - 1]
    offset = graph.get_vertex(home_airport).max_emissions(dest_airport) - chosen_route[3]

    # Providing a final summary to the user of their choices, and how to book this flight in real life.
    print()
    print("How your decision has made a difference: ")
    co2_stats = carbon_statistics(offset)
    print(random.choice(list(co2_stats)))
    print()
    print("Now, to book your flight, kindly follow these steps: ")
    print(f'Step 1: Go on to the website of {routes[chosen_route_num - 1][0][0]}.')
    print(f'Step 2: Search for flights from {home_airport} to {dest_airport}.')
    print('Step 3: Look for flights with the same sequence of aircrafts as provided by the flight package.')
    print()
    print("With these simple steps, you have chosen an eco-friendly flight path to your destination!")
    print()
    print('To assist with your travels, here are 3 travel tips to help reduce environmental impact:')
    random_tip1 = random.choice(TRAVEL_TIPS)
    TRAVEL_TIPS.remove(random_tip1)
    random_tip2 = random.choice(TRAVEL_TIPS)
    TRAVEL_TIPS.remove(random_tip2)
    random_tip3 = random.choice(TRAVEL_TIPS)
    print(f'Tip 1: {random_tip1}')
    print(f'Tip 2: {random_tip2}')
    print(f'Tip 3: {random_tip3}')
    print()
    print('Thank you for flying with VerdeVoyage!')


def create_graph(airport_coords: dict[str, tuple[float, float]], home_airport: str = None, dest_airport: str = None,
                 dest_countries: list[str] = None) -> data_classes.Graph:
    """
    Return a graph containing home_airport and dest_airport as vertices, if given, and the flights between the airports
    as the edges connecting the two vertices.

    If home_airport and/or dest_airport is not given, return the appropriate graph.

    Preconditions:
        - dest_airport is None or home_airport is not None
    """
    graph = data_classes.Graph()
    with open('CSV Files/flight_data.csv') as file:
        reader = csv.reader(file)
        next(reader, None)  # skip the header

        for row in reader:

            # If any of the values are missing, then move to the next row
            if row[4] == '' or row[12] == '' or row[14] == '':
                continue

            # Depending on what is given, generate the appropriate graph
            if home_airport is None:
                create_graph_helper(graph, row, airport_coords)

            elif home_airport is not None and dest_airport is not None:
                if row[0] == home_airport and row[2] == dest_airport:
                    create_graph_helper(graph, row, airport_coords)

            elif home_airport is not None and dest_countries is not None:
                lower_set = {country.lower() for country in dest_countries}
                if row[0] == home_airport and row[3].lower() in lower_set:
                    create_graph_helper(graph, row, airport_coords)

            else:  # home_airport is not None and both dest_airport and dest_country are None
                if row[0] == home_airport:
                    create_graph_helper(graph, row, airport_coords)

    return graph


def calculate_flight_scores(flights: dict[tuple[str, tuple[str, ...]], list[float | int]],
                            weights: tuple[float, float, float] = (0.1, 0.1, 0.8)) -> dict[tuple[str, tuple], float]:
    """
    Given a dictionary of flight packages, calculate a score for each flight package in flights
    based on the given weights for price, stops, and carbon emissions.

    Return a mapping between each flight and its score.

    The input weights has the following format: (price, stops, emissions)
    """
    weight_price, weight_stops, weight_emissions = weights
    max_price = max(flights[flight_l][0] for flight_l in flights)
    max_stops = max(flights[flight_l][1] for flight_l in flights)
    max_emissions = max(flights[flight_l][2] for flight_l in flights)

    flight_scores = {}

    for flight in flights:
        flight_info = flights[flight]
        price, stops, emissions = flight_info[0], flight_info[1], flight_info[2]

        # Normalize the values (puts the values between 0 and 1)
        norm_price = price / max_price
        norm_stops = stops / max_stops
        norm_emissions = emissions / max_emissions

        flight_scores[
            flight] = norm_price * weight_price + norm_stops * weight_stops + norm_emissions * weight_emissions

    return flight_scores


def optimal_routes(graph: data_classes.Graph, home_airport: str, dest_airport: str,
                   weights: tuple[float, float, float] = (0.1, 0.1, 0.8)) -> list[tuple]:
    """
    Return upto five most optimal flight packages between home_airport and dest_airport.

    The input weights has the following format: (price, stops, emissions).
    The returned tuple has the following format: ((airline, (aircraft)), price, stops, emissions, flight_score).
    """
    # Retrieve the appropriate Vertex objects
    home_vertex = graph.get_vertex(home_airport)
    destination_vertex = graph.get_vertex(dest_airport)

    if home_vertex not in graph.all_verticies() or destination_vertex not in graph.all_verticies():
        raise ValueError

    if destination_vertex not in home_vertex.neighbours:
        return []

    # Find all the flight packages from home airport to destination airport
    flights = home_vertex.neighbours[destination_vertex]
    flight_scores = calculate_flight_scores(flights, weights)

    # Sort the flights based on the returned score
    sorted_flights = sorted(flight_scores.items(), key=lambda item: item[1])

    all_flights = [(flight[0], flights[flight[0]][0], flights[flight[0]][1], flights[flight[0]][2],
                    round(flight[1], 5)) for flight in sorted_flights]
    return all_flights[:5]


def countries_and_airports(flight_path_file: str) -> tuple[set[str], set[str], set[str], set[str]]:
    """
    Returns a tuple of home countries, dest countries, home airports, and dest airports in the flight dataset.
    """

    home_countries, home_airports = set(), set()
    dest_countries, dest_airports = set(), set()

    with open(flight_path_file, mode='r') as flight_paths:
        reader = csv.reader(flight_paths)
        next(flight_paths)
        for row in reader:
            home_airports.add(row[0])
            dest_airports.add(row[2])
            home_countries.add(row[1].lower())
            dest_countries.add(row[3].lower())

    return home_airports, home_countries, dest_airports, dest_countries


def get_airport_coordinates() -> dict[str, tuple[float, float]]:
    """
    Return a mapping between airport codes and their latitude and longitude coordinates.
    """
    airport_coords = {}
    with open('CSV Files/78_airport_info.csv', 'r') as file:
        reader = csv.reader(file)
        next(reader, None)  # skip the header
        for row in reader:
            airport_coords[row[0]] = (float(row[1]), float(row[2]))  # (latitude, longitude)

    return airport_coords


def create_graph_helper(graph: data_classes.Graph, row: list[str],
                        airport_coords: dict[str, tuple[float, float]]) -> None:
    """
    Store the flight information in the given row in the graph.
    """
    graph.add_vertex(row[0], row[1], airport_coords[row[0]])
    graph.add_vertex(row[2], row[3], airport_coords[row[2]])

    aircrafts = tuple(row[4].split('|'))
    airline = row[6].split('| ')[0].strip('[]')
    stops = int(row[11])
    price = float(row[12])
    emissions = int(row[14])

    flight_package = (airline, aircrafts)
    flight_info = [price, stops, emissions]
    graph.add_edge(row[0], row[2], (flight_package, flight_info))


def carbon_statistics(offset: int) -> set[str]:
    """
    Return a set of statistics based on how much carbon emissions the user saved by choosing
    a flight package suggested by our program.
    """
    # All stats have been sourced from clevercarbon.io
    all_stats = set()
    avg_c02_percentage_person = round((offset / 4000000) * 100, 2)
    car_km = round(offset / 192, 2)
    plastic_bottles = round(offset / 83)
    light_bulb = round(offset / 42)
    coffee_cups = round(offset / 50)
    all_stats.add(
        f"Over {coffee_cups} cups! Thats how many coffee cups you saved by flying with VerdeVoyage. "
        f"Our planet thanks you! ")
    all_stats.add(
        f"{light_bulb} hours. That is how many hours of having a light bulb turned on you have saved by flying with "
        f"VerdeVoyage.")
    all_stats.add(
        f"{plastic_bottles} bottles. That is how many plastic bottles you saved by choosing the most greenflight "
        f"to your destination!")
    all_stats.add(
        f"Choosing this flight over the others, you have saved the equivalent of not driving for {car_km} kilometers.")
    all_stats.add(
        f"By flying with VerdeVoyage, you have saved {avg_c02_percentage_person}% of an individuals "
        f"annual carbon usage.")
    return all_stats


# A list of informative travel tips to be eco-conscious while travelling
TRAVEL_TIPS = [
    "Select Low-Impact Accommodations: Opt for certified green hotels that focus on sustainable practices.",
    "Use Public Transport or Bike: Explore by public transit, walking, or biking instead of car rentals or taxis."
    "Eat Local and Seasonal: Choose places serving local, seasonal dishes to support agriculture and cut emissions.",
    "Carry Reusable Items: Pack a reusable water bottle, shopping bags, and utensils to minimize plastic waste.",
    "Conserve Resources: Save energy and water in hotels: turn off lights, reuse towels, and take shorter showers.",
    "Respect Natural Environments: Follow guidelines when visiting natural sites to minimize your impact on wildlife.",
    "Understand Local Cultures: Learn and respect local cultures for positive interactions and minimal cultural clash.",
    "Choose Sustainable Activities: Opt for eco-tourism to support conservation and local communities.",
    "Reduce, Reuse, Recycle: Reduce waste, reuse, and recycle during travels whenever possible.",
    "Support Eco-friendly Businesses: Support businesses with sustainable practices, from tours to shops."]

if __name__ == '__main__':
    # import python_ta.contracts
    # python_ta.contracts.check_all_contracts()
    import python_ta

    python_ta.check_all(config={
        'max-line-length': 170,
        'disable': ['E1136', 'W0221', 'E9969'],
        'extra-imports': ['csv', 'random', 'data_classes', 'flight_visualization'],
        'allowed-io': ['run_voyage', 'get_airport_coordinates', 'countries_and_airports', 'optimal_routes',
                       'create_graph'],
        'max-nested-blocks': 4,
        'max-locals': 35,
        'max-statements': 90
    })
