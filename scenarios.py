
"""
Scenarios File

This file holds the different scenarios that can be applied to the model.
The user can opt for:

    1) Arbitrary scenario to test the model functionality.
"""


class BaseScenario:
    """
    Base class for scenarios. Defines shared parameters and methods.
    """
    def __init__(self, name):
        self.name = name

    def get_parameters(self):
        """
        Returns the parameters for the scenario. To be overridden by subclasses.
        """
        raise NotImplementedError("Subclasses must implement get_parameters.")

    def print_summary(self):
        """
        Print a summary of the scenario.
        """
        print(f"Scenario: {self.name}")


class Scenario1(BaseScenario):
    """ 
    Class for scenario 1. This scenario is fictional and serves 
    """
    def __init__(self, name):
        super().__init__(name)
    
    def get_parameters(self):
        """ Gets the parameters. """

        aircraft_data = {
            "aircraft": [1, 2, 3],              # Set of all aircraft (P)
            "departures": [1, 2],               # Set of departure aircraft (D)
            "arrivals": [3],                    # Set of arrival aircraft (A)
            "origin": {1: 1, 2: 2, 3: 3},       # Origin node (oi) for each aircraft
            "destination": {1: 5, 2: 5, 3: 5},  # Destination node (di) for each aircraft
            "PBT": {1: 10, 2: 15},              # Push-back time (PBTi) for departures
            "ETD": {3: 30},                     # Estimated touchdown time (ETDi) for arrivals
            "Vi_j": {(1, 2): 30, (2, 1): 30},   # Minimum time separation (Vij) between aircraft i and j
        }

        graph_data = {
            "nodes": [1, 2, 3, 4, 5],                                           # Nodes in the airport graph
            "edges": [(1, 2), (2, 3), (3, 4), (4, 5)],                          # Directed edges in the airport graph
            "length": {(1, 2): 100, (2, 3): 150, (3, 4): 200, (4, 5): 250},     # Length of each edge (luv)
            "Smax": {(1, 2): 15, (2, 3): 15, (3, 4): 15, (4, 5): 15},           # Maximum velocity (Smax) for each edge
            "Smin": {(1, 2): 5, (2, 3): 5, (3, 4): 5, (4, 5): 5},               # Minimum velocity (Smin) for each edge
            "runway_edges": [(4, 5)],                                           # Runway edges
            "Sep": 5,                                                           # Minimum spatial separation (Sep) on taxiways
        }

        route_data = {
            # All routes for each aircraft (R_i)
            "routes": {
                1: [  # Routes for aircraft 1
                    {"nodes": [1, 2, 3, 5], "edges": [(1, 2), (2, 3), (3, 5)]}, # First route
                    {"nodes": [1, 4, 3, 5], "edges": [(1, 4), (4, 3), (3, 5)]}, # Second route
                ],
                2: [  # Routes for aircraft 2
                    {"nodes": [2, 3, 5], "edges": [(2, 3), (3, 5)]},            # First route
                ],
                3: [  # Routes for aircraft 3
                    {"nodes": [3, 4, 5], "edges": [(3, 4), (4, 5)]},            # First route
                    {"nodes": [3, 2, 5], "edges": [(3, 2), (2, 5)]},            # Second route
                ],
            },

            # Ordered edges  across all routes for each aircraft
            "all_edges_per_aircraft": {
                1: [(1, 2), (2, 3), (3, 5), (1, 4), (4, 3)],                    # All edges across all routes for aircraft 1
                2: [(2, 3), (3, 5)],                                            # All edges across all routes for aircraft 2
                3: [(3, 4), (4, 5), (3, 2), (2, 5)],                            # All edges across all routes for aircraft 3
            },
        }


        return {
            "aircraft_data": aircraft_data,
            "graph_data": graph_data,
            "route_data": route_data
        }

class Dusseldorf(BaseScenario):
    """ 
    Class for Dusseldorf inspired taxi schedule. This scenario is fictional and serves 
    """
    def __init__(self, name):
        super().__init__(name)
    
    def get_parameters(self):
        """ Gets the parameters. """

        aircraft_data = {
            "aircraft": [1, 2, 3],              # Set of all aircraft (P)
            "departures": [1, 2],               # Set of departure aircraft (D)
            "arrivals": [3],                    # Set of arrival aircraft (A)
            "origin": {1: 1, 2: 2, 3: 3},       # Origin node (oi) for each aircraft
            "destination": {1: 5, 2: 5, 3: 5},  # Destination node (di) for each aircraft
            "PBT": {1: 10, 2: 15},              # Push-back time (PBTi) for departures
            "ETD": {3: 30},                     # Estimated touchdown time (ETDi) for arrivals
            "Vi_j": {(1, 2): 30, (2, 1): 30},   # Minimum time separation (Vij) between aircraft i and j
        }

        graph_data = {
    "nodes": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33],
    "edges": [(1, 2), (2, 3), (3, 4), (4, 33), (1, 5), (2, 7), (3, 8), (4, 9), (33, 32), 
              (5, 6), (6, 7), (7, 8), (8, 9), (9, 32), (5, 10), (6, 11), (8, 16), (9, 16), (32, 31),
              (10, 11), (11, 12), (12, 13), (13, 14), (14, 15), (15, 16), (16, 31), (10, 17),
              (13, 20), (16, 23), (17, 18), (18, 19), (19, 20), (20, 21),
              (21, 22), (22, 23), (17, 24), (18, 25), (19, 26), (20, 27), (21, 28), (22, 29), (23, 30)],
    "length": {(1, 2): 500, (2, 3): 1500, (3, 4): 500, (4, 33): 500, (1, 5): 500, (2, 7): 500, 
               (3, 8): 500, (4, 9): 500, (33, 32): 500, (5, 6): 250, (6, 7): 250, (7, 8): 1500, 
               (8, 9): 500, (9, 32): 500, (5, 10): 500, (6, 11): 500, (8, 16): 500, (9, 16): 700, 
               (32, 31): 500, (10, 11): 250, (11, 12): 250, (12, 13): 250, (13, 14): 250, 
               (14, 15): 250, (15, 16): 250, (16, 31): 1000, (10, 17): 250, (13, 20): 250,
               (16, 23): 250, 
               (17, 18): 250, (18, 19): 250, (19, 20): 250, (20, 21): 250, (21, 22): 250, 
               (22, 23): 250, (17, 24): 100, (18, 25): 100, (19, 26): 100, (20, 27): 100, 
               (21, 28): 100, (22, 29): 100, (23, 30): 100},
    "Smax": {(1, 2): "X", (2, 3): "X", (3, 4): "X", (4, 33): "X", (1, 5): "X", (2, 7): "X", 
             (3, 8): "X", (4, 9): "X", (33, 32): "X", (5, 6): "X", (6, 7): "X", (7, 8): "X", 
             (8, 9): "X", (9, 32): "X", (5, 10): "X", (6, 11): "X", (8, 16): "X", (9, 16): "X", 
             (32, 31): "X", (10, 11): "X", (11, 12): "X", (12, 13): "X", (13, 14): "X", 
             (14, 15): "X", (15, 16): "X", (16, 31): "X", (10, 17): "X", (11, 18): "X", 
             (12, 19): "X", (13, 20): "X", (14, 21): "X", (15, 22): "X", (16, 23): "X", 
             (17, 18): "X", (18, 19): "X", (19, 20): "X", (20, 21): "X", (21, 22): "X", 
             (22, 23): "X", (17, 24): "X", (18, 25): "X", (19, 26): "X", (20, 27): "X", 
             (21, 28): "X", (22, 29): "X", (23, 30): "X"},
    "Smin": {(1, 2): 21.5, (2, 3): 21.5, (3, 4): 21.5, (4, 33): 21.5, (1, 5): 21.5, (2, 7): 21.5, 
             (3, 8): 21.5, (4, 9): 21.5, (33, 32): 21.5, (5, 6): 21.5, (6, 7): 21.5, (7, 8): 21.5, 
             (8, 9): 21.5, (9, 32): 21.5, (5, 10): 21.5, (6, 11): 21.5, (8, 16): 21.5, (9, 16): 21.5, 
             (32, 31): 21.5, (10, 11): 21.5, (11, 12): 21.5, (12, 13): 21.5, (13, 14): 21.5, 
             (14, 15): 21.5, (15, 16): 21.5, (16, 31): 21.5, (10, 17): 21.5, (11, 18): 21.5, 
             (12, 19): 21.5, (13, 20): 21.5, (14, 21): 21.5, (15, 22): 21.5, (16, 23): 21.5, 
             (17, 18): 21.5, (18, 19): 21.5, (19, 20): 21.5, (20, 21): 21.5, (21, 22): 21.5, 
             (22, 23): 21.5, (17, 24): 21.5, (18, 25): 21.5, (19, 26): 21.5, (20, 27): 21.5, 
             (21, 28): 21.5, (22, 29): 21.5, (23, 30): 21.5},
    "runway_edges": [],
    "Sep": "X"}

        route_data = {
            # All routes for each aircraft (R_i)
            "routes": {
                1: [  # Routes for aircraft 1
                    {"nodes": [1, 2, 3, 5], "edges": [(1, 2), (2, 3), (3, 5)]}, # First route
                    {"nodes": [1, 4, 3, 5], "edges": [(1, 4), (4, 3), (3, 5)]}, # Second route
                ],
                2: [  # Routes for aircraft 2
                    {"nodes": [2, 3, 5], "edges": [(2, 3), (3, 5)]},            # First route
                ],
                3: [  # Routes for aircraft 3
                    {"nodes": [3, 4, 5], "edges": [(3, 4), (4, 5)]},            # First route
                    {"nodes": [3, 2, 5], "edges": [(3, 2), (2, 5)]},            # Second route
                ],
            },

            # Ordered edges  across all routes for each aircraft
            "all_edges_per_aircraft": {
                1: [(1, 2), (2, 3), (3, 5), (1, 4), (4, 3)],                    # All edges across all routes for aircraft 1
                2: [(2, 3), (3, 5)],                                            # All edges across all routes for aircraft 2
                3: [(3, 4), (4, 5), (3, 2), (2, 5)],                            # All edges across all routes for aircraft 3
            },
        }


        return {
            "aircraft_data": aircraft_data,
            "graph_data": graph_data,
            "route_data": route_data
        }



def get_scenario(name):
    scenarios = {
        "scenario_1": Scenario1("scenario_1")
    }
    if name not in scenarios:
        return None
    return scenarios[name].get_parameters()       
