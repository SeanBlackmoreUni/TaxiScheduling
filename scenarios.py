
"""
Scenarios File

This file holds the different scenarios that can be applied to the model.
The user can opt for:

    1) Arbitrary scenario to test the model functionality.
"""

def find_paths(graph_data, start, end, path=[]):
        """
        Recursively find all paths from start node to end node in a graph.
        Args:
            graph_data (dict): Dictionary containing graph information (nodes and edges).
            start (int): Starting node.
            end (int): Target node.
            path (list): Current path (used in recursion).
        Returns:
            list: List of all paths from start to end.
        """
        path = path + [start]
        if start == end:
            return [path]
        if start not in graph_data["nodes"]:
            return []
        paths = []
        for edge in graph_data["edges"]:
            if edge[0] == start and edge[1] not in path:
                new_paths = find_paths(graph_data, edge[1], end, path)
                for new_path in new_paths:
                    paths.append(new_path)
            elif edge[1] == start and edge[0] not in path:
                new_paths = find_paths(graph_data, edge[0], end, path)
                for new_path in new_paths:
                    paths.append(new_path)
        return paths


def generate_route_data(aircraft_data, graph_data):
    """
    Generate route data for aircraft dynamically using provided graph_data.
    Args:
        aircraft_data (dict): Dictionary containing aircraft-related data.
        graph_data (dict): Dictionary containing graph structure (nodes, edges).
    Returns:
        dict: Generated route data including routes, unique edges, and nodes for each aircraft.
    """
    route_data = {
        "routes": {},
        "all_edges_per_aircraft": {},
        "all_nodes_per_aircraft": {}
    }

    for aircraft in aircraft_data["aircraft"]:
        origin = aircraft_data["origin"][aircraft]
        destination = aircraft_data["destination"][aircraft]

        # Find all possible paths from origin to destination
        paths = find_paths(graph_data, origin, destination)
        routes = []
        all_edges = []

        # Convert paths into routes with edges
        for path in paths:
            edges = [(path[i], path[i + 1]) for i in range(len(path) - 1)]
            routes.append({"nodes": path, "edges": edges})
            all_edges.extend(edges)

        # Add routes and unique edges for the aircraft
        route_data["routes"][aircraft] = routes
        route_data["all_edges_per_aircraft"][aircraft] = list(dict.fromkeys(all_edges))

        # Extract all unique nodes from edges for the aircraft
        all_nodes = set()
        for edge in route_data["all_edges_per_aircraft"][aircraft]:
            all_nodes.update(edge)  # Add both nodes in the edge to the set
        route_data["all_nodes_per_aircraft"][aircraft] = list(all_nodes)

    return route_data



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
            "nodes": [1, 2, 3, 4, 5],                                                       # Nodes in the airport graph
            "edges": [
                (1, 2), (2, 3), (3, 4), (4, 5), (1, 4), (4, 3), (3, 5), (3, 2), (2, 5)      # Edges from route_data
            ],
            "length": {
                (1, 2): 100, (2, 3): 150, (3, 4): 200, (4, 5): 250,             
                (1, 4): 180, (4, 3): 140, (3, 5): 220, (3, 2): 130, (2, 5): 210             # Lengths
            },
            "Smax": {
                (1, 2): 15, (2, 3): 15, (3, 4): 15, (4, 5): 15,                       
                (1, 4): 15, (4, 3): 15, (3, 5): 15, (3, 2): 15, (2, 5): 15                  # Max speeds
            },
            "Smin": {
                (1, 2): 5, (2, 3): 5, (3, 4): 5, (4, 5): 5,                     
                (1, 4): 5, (4, 3): 5, (3, 5): 5, (3, 2): 5, (2, 5): 5                       # Additional min speeds
            },
            "runway_edges": [(4, 5)],                                                       # Runway edges remain unchanged
            "Sep": 5,                                                                       # Minimum spatial separation
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
            "aircraft": [1, 5],# 2, 3, 4, 5, 6, 7],                  # Set of all aircraft (P)
            "departures": [1],# 2, 3, 4],                               # Set of departure aircraft (D)
            "arrivals": [5],# 6, 7],                                    # Set of arrival aircraft (A)
            "origin": {
                1: 37, 
                # 2: 25, 
                # 3: 26, 
                # 4: 27, 
                5: 3}, 
                # 6: 4, 
                # 7: 3},                       # Origin node (oi) for each aircraft
            "destination": {
                1: 11, 
                # 2: 6, 
                # 3: 7, 
                # 4: 8, 
                5: 41}, 
                # 6: 29, 
                # 7: 30},                  # Destination node (di) for each aircraft
            "PBT": {
                1: 0,  
                2: 40, 
                3: 70,  
                4: 100},  
            "ETD": {
                5: 0,
                6: 60,
                7: 100
            },                                     # Estimated touchdown time (ETDi) for arrivals
            "Vi_j": 61,                  # Here the assumption is made that all aircraft are large
            "T": 40
        }

        graph_data = {
            "nodes": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50],
            "edges": [
                (3, 48), (8, 48), (4, 49), (9, 49), (5, 50), (10, 50), (44, 50),
                (44, 45), (45, 46), (46, 47), (25, 47), (11, 17), (12, 18), (13, 19), 
                (14, 23), (15, 24), (16, 25), (17, 18), (18, 19), (20, 21), (21, 22),
                (22, 23), (23, 24), (24, 25), (25, 34), (33, 34), (32, 33), (31, 32),
                (30, 31), (29, 30), (28, 29), (27, 28), (26, 27), (17, 26), (18, 27),
                (19, 28), (20, 29), (21, 30), (22, 31), (23, 32), (24, 33), (26, 35),
                (27, 36), (28, 37), (29, 38), (30, 39), (31, 40), (32, 41), (33, 42),
                (34, 43), (48, 49), (49, 50), (8, 14), (9, 15), (10, 16), (15, 24)
            ],
            "length": {
                (3, 48): 125, (8, 48): 125, (4, 49): 125, (9, 49): 125, (5, 50): 125, (10, 50): 125, 
                (44, 50): 250, (44, 45): 125, (45, 46): 50, (46, 47): 250, (25, 47): 250, 
                (11, 17): 250, (12, 18): 250, (13, 19): 250, (14, 23): 250, (15, 24): 250, 
                (16, 25): 250, (17, 18): 125, (18, 19): 125, (20, 21): 125, (21, 22): 125, 
                (22, 23): 125, (23, 24): 125, (24, 25): 125, (25, 34): 125, (33, 34): 125, 
                (32, 33): 125, (31, 32): 125, (30, 31): 125, (29, 30): 125, (28, 29): 125, 
                (27, 28): 125, (26, 27): 125, (17, 26): 125, (18, 27): 125, (19, 28): 125, 
                (20, 29): 125, (21, 30): 125, (22, 31): 125, (23, 32): 125, (24, 33): 125, 
                (26, 35): 125, (27, 36): 125, (28, 37): 125, (29, 38): 125, (30, 39): 125, 
                (31, 40): 125, (32, 41): 125, (33, 42): 125, (34, 43): 125, (35, 44): 125, 
                (48, 49): 125, (49, 50): 125, (8, 14): 50, (9, 15): 50, (10, 16): 50, (15, 24): 50
            },
            "Smax": {
                (5, 44): 9.03, (44, 45): 9.03, (45, 46): 9.03, (46, 47): 9.03, (25, 47): 9.03,
                (11, 17): 9.03, (12, 18): 9.03, (13, 19): 9.03, (14, 23): 9.03, (15, 24): 9.03,
                (16, 25): 9.03, (17, 18): 9.03, (18, 19): 9.03, (20, 21): 9.03, (21, 22): 9.03,
                (22, 23): 9.03, (23, 24): 9.03, (24, 25): 9.03, (25, 34): 9.03, (33, 34): 9.03,
                (32, 33): 9.03, (31, 32): 9.03, (30, 31): 9.03, (29, 30): 9.03, (28, 29): 9.03,
                (27, 28): 9.03, (26, 27): 9.03, (17, 26): 9.03, (18, 27): 9.03, (19, 28): 9.03,
                (20, 29): 9.03, (21, 30): 9.03, (22, 31): 9.03, (23, 32): 9.03, (24, 33): 9.03,
                (26, 35): 9.03, (27, 36): 9.03, (28, 37): 9.03, (29, 38): 9.03, (30, 39): 9.03,
                (31, 40): 9.03, (32, 41): 9.03, (33, 42): 9.03, (34, 43): 9.03, (35, 44): 9.03,
                (8, 14): 9.03, (9, 15): 9.03, (10, 16): 9.03, (15, 24): 9.03, (3, 48): 9.03, (8, 48): 9.03,
                (4, 49): 9.03, (9, 49): 9.03, (5, 50): 9.03, (10, 50): 9.03, (44, 50): 9.03,
                (48, 49): 9.03, (49, 50): 9.03
            },
            "Smin": {
                (5, 44): 5.97, (44, 45): 5.97, (45, 46): 5.97, (46, 47): 5.97, (25, 47): 5.97,
                (11, 17): 5.97, (12, 18): 5.97, (13, 19): 5.97, (14, 23): 5.97, (15, 24): 5.97,
                (16, 25): 5.97, (17, 18): 5.97, (18, 19): 5.97, (20, 21): 5.97, (21, 22): 5.97,
                (22, 23): 5.97, (23, 24): 5.97, (24, 25): 5.97, (25, 34): 5.97, (33, 34): 5.97,
                (32, 33): 5.97, (31, 32): 5.97, (30, 31): 5.97, (29, 30): 5.97, (28, 29): 5.97,
                (27, 28): 5.97, (26, 27): 5.97, (17, 26): 5.97, (18, 27): 5.97, (19, 28): 5.97,
                (20, 29): 5.97, (21, 30): 5.97, (22, 31): 5.97, (23, 32): 5.97, (24, 33): 5.97,
                (26, 35): 5.97, (27, 36): 5.97, (28, 37): 5.97, (29, 38): 5.97, (30, 39): 5.97,
                (31, 40): 5.97, (32, 41): 5.97, (33, 42): 5.97, (34, 43): 5.97, (35, 44): 5.97,
                (8, 14): 5.97, (9, 15): 5.97, (10, 16): 5.97, (15, 24): 5.97, (3, 48): 5.97, (8, 48): 5.97,
                (4, 49): 5.97, (9, 49): 5.97, (5, 50): 5.97, (10, 50): 5.97, (44, 50): 5.97,
                (48, 49): 5.97, (49, 50): 5.97
            },
            "runway_exit_nodes": [8, 9, 10],
            "runway_entry_nodes": [14, 15, 16],
            "departing_nodes": [11, 12, 13],
            "Sep": 50,
            "exit_edges": [(3, 48), (4, 49), (5, 50)]
        }

        route_data = generate_route_data(aircraft_data, graph_data)

        return {
            "aircraft_data": aircraft_data,
            "graph_data": graph_data,
            "route_data": route_data
        }


def get_scenario(name):
    scenarios = {
        "scenario_1": Scenario1("scenario_1"),
        "scenario_2": Dusseldorf("scenario_2")
    }
    if name not in scenarios:
        return None
    return scenarios[name].get_parameters() 


scenario = get_scenario('scenario_2') 
print(scenario["route_data"]['routes'][1])    
