""" 
Main File

This file holds the main flow of the model. It initialises the variables 
for a scenario, sets the constraints, and optimizes following the structure
of the taxi scheduling report.

"""

from gurobipy import Model,GRB, quicksum
from scenarios import get_scenario
from constraints import *


class TaxiSchedulingModel():
    """ 
    The model class for the taxi scheduling problem. 
    """
    def __init__(self, scenario):
        self.model = Model()
        self.scenario = scenario
    

    def scenario_setup(self):
        """ 
        Calls the specified scenario and loads it into the model.
        Returns all parameters and decision variables.
        """
        variables = get_scenario(scenario)

        aircraft_data = variables['aircraft_data']
        graph_data = variables['graph_data']
        route_data = variables['route_data']

        # Decision Variables
        decision_variables = {
            # Binary variable Z_{iju} indicating sequencing of aircraft i and j at node u
            "Z": model.addVars(
                [(i, j, u) for i in aircraft_data["aircraft"]
                        for j in aircraft_data["aircraft"]
                        if i != j
                        for u in graph_data["nodes"]],
                vtype=GRB.BINARY, name="Z"
            ),

            # Binary variable Gamma_{ir} indicating if aircraft i selects route r
            "Gamma": model.addVars(
                [(i, r) for i in aircraft_data["aircraft"]
                        for r in range(len(route_data["routes"][i]))],
                vtype=GRB.BINARY, name="Gamma"
            ),

            # Binary variable rho_{ij} indicating sequencing between aircraft i and j on runways
            "rho": model.addVars(
                [(i, j) for i in aircraft_data["aircraft"]
                        for j in aircraft_data["aircraft"]
                        if i != j],
                vtype=GRB.BINARY, name="rho"
            ),

            # Continuous variable t_{iu} indicating time aircraft i arrives at node u
            "t": model.addVars(
                [(i, u) for i in aircraft_data["aircraft"]
                        for u in graph_data["nodes"]],
                vtype=GRB.CONTINUOUS, name="t"
            ),
        }

        self.variables = aircraft_data | graph_data | route_data | decision_variables


    def constraints_setup(self):
        """ Sets up the constraints for the model. """
        constraint_classes = [
            Domain,
            Sequencing,
            # Overtaking,
            # Release,
            # Speed,
            # Separation,
            # RunwayOccupancy
        ]

        for constraint_class in constraint_classes:
            constraint = constraint_class(self.model, self.variables)
            constraint.add_constraints()


    def optimize_model(self):
        """ Optimizes the model in the two steps specified by the report. """
        # We will first solve for Objective function 2).
        S = model.addVar(vtype=GRB.CONTINUOUS, name="S")


    def visualize_results(self):
        """ Visualizes the results of the optimization. """
        pass


if __name__ == "__main__":
    scenario = "scenario_1"            
    model = TaxiSchedulingModel(scenario)
    model.scenario_setup()
    model.constraints_setup()
    model.optimize_model()
    model.visualize_results()
