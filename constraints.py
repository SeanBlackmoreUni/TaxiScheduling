"""
Constaint File

This file holds all the constraints for the Taxi Scheduling Problem.
"""

from gurobipy import quicksum, Model


class Constraints:
    def __init__(self, model: Model, variables: dict):
        """
        Base Constraints class for setting up model constraints.
        
        Parameters:
            model (Model): The Gurobi optimization model.
            variables (dict): Dictionary containing model variables.
        """
        self.model = model
        self.variables = variables

    def add_constraints(self):
        raise NotImplementedError("Subclasses should implement this method.")
    

class Domain(Constraints):
    def add_constraints(self):
        # Equation (1): Z_{iju} is binary
        for i in self.variables['aircraft']:
            for j in self.variables['aircraft']:
                for u in self.variables['nodes']:
                    if i != j:
                        self.model.addConstr(
                            self.variables['Z'][i, j, u] >= 0,
                            name=f"Z_binary_lower_{i}_{j}_{u}"
                        )
                        self.model.addConstr(
                            self.variables['Z'][i, j, u] <= 1,
                            name=f"Z_binary_upper_{i}_{j}_{u}"
                        )

        # Equation (2): Gamma_{ir} is binary
        for i in self.variables['aircraft']:
            for r in self.variables['routes']:
                self.model.addConstr(
                    self.variables['Gamma'][i, r] >= 0,
                    name=f"Gamma_binary_lower_{i}_{r}"
                )
                self.model.addConstr(
                    self.variables['Gamma'][i, r] <= 1,
                    name=f"Gamma_binary_upper_{i}_{r}"
                )

        # Equation (3): rho_{ij} is binary
        for i in self.variables['aircraft']:
            for j in self.variables['aircraft']:
                if i != j:
                    self.model.addConstr(
                        self.variables['rho'][i, j] >= 0,
                        name=f"rho_binary_lower_{i}_{j}"
                    )
                    self.model.addConstr(
                        self.variables['rho'][i, j] <= 1,
                        name=f"rho_binary_upper_{i}_{j}"
                    )

        # Equation (4): t_{iu} is non-negative
        for i in self.variables['aircraft']:
            for u in self.variables['nodes']:
                self.model.addConstr(
                    self.variables['t'][i, u] >= 0,
                    name=f"t_nonnegative_{i}_{u}"
                )

        # Equation (6): Each aircraft selects one route
        for i in self.variables['aircraft']:
            self.model.addConstr(
                quicksum(self.variables['Gamma'][i, r] for r in self.variables['routes']) == 1,
                name=f"route_selection_{i}"
            )

        # Equation (7): Z_{iju} logic constraint
        for i in self.variables['aircraft']:
            for j in self.variables['aircraft']:
                if i != j:
                    for u in self.variables['nodes']:
                        self.model.addConstr(
                            self.variables['Z'][i, j, u] <= quicksum(
                                self.variables['Gamma'][i, r]
                                for r in self.variables['routes'] if u in self.variables['routes'][r]
                            ),
                            name=f"Z_logic_1_{i}_{j}_{u}"
                        )

        # Equation (8): Z_{iju} logic constraint for j
        for i in self.variables['aircraft']:
            for j in self.variables['aircraft']:
                if i != j:
                    for u in self.variables['nodes']:
                        self.model.addConstr(
                            self.variables['Z'][i, j, u] <= quicksum(
                                self.variables['Gamma'][j, r]
                                for r in self.variables['routes'] if u in self.variables['routes'][r]
                            ),
                            name=f"Z_logic_2_{i}_{j}_{u}"
                        )    


class Sequencing(Constraints):
    def add_constraints(self):
        # Constraints (9) and (10): Sequencing consistency
        for i in self.variables['aircraft']:
            for j in self.variables['aircraft']:
                if i != j:
                    for u in self.variables['nodes']:
                        # Equation (9)
                        self.model.addConstr(
                            self.variables['Z'][i, j, u] + self.variables['Z'][j, i, u] 
                            <= 3 - (
                                quicksum(self.variables['Gamma'][i, r] for r in self.variables['routes'] if u in self.variables['routes'][r]) +
                                quicksum(self.variables['Gamma'][j, r] for r in self.variables['routes'] if u in self.variables['routes'][r])
                            ),
                            name=f"sequencing_upper_{i}_{j}_{u}"
                        )
                        # Equation (10)
                        self.model.addConstr(
                            self.variables['Z'][i, j, u] + self.variables['Z'][j, i, u] 
                            >= 2 * (
                                quicksum(self.variables['Gamma'][i, r] for r in self.variables['routes'] if u in self.variables['routes'][r]) +
                                quicksum(self.variables['Gamma'][j, r] for r in self.variables['routes'] if u in self.variables['routes'][r])
                            ) - 3,
                            name=f"sequencing_lower_{i}_{j}_{u}"
                        )


class Overtaking(Constraints):
    def add_constraints(self):
        # Constraints (11) and (12): No overtaking on the same edge
        for i in self.variables['aircraft']:
            for j in self.variables['aircraft']:
                if i != j:
                    for (u, v) in self.variables['edges']:
                        # Equation (11)
                        self.model.addConstr(
                            self.variables['Z'][i, j, u] - self.variables['Z'][i, j, v] 
                            <= 2 - (
                                quicksum(self.variables['Gamma'][i, r] for r in self.variables['routes'] if (u, v) in self.variables['edges'][r]) +
                                quicksum(self.variables['Gamma'][j, r] for r in self.variables['routes'] if (u, v) in self.variables['edges'][r])
                            ),
                            name=f"overtaking_upper_{i}_{j}_{u}_{v}"
                        )
                        # Equation (12)
                        self.model.addConstr(
                            self.variables['Z'][i, j, u] - self.variables['Z'][i, j, v] 
                            >= (
                                quicksum(self.variables['Gamma'][i, r] for r in self.variables['routes'] if (u, v) in self.variables['edges'][r]) +
                                quicksum(self.variables['Gamma'][j, r] for r in self.variables['routes'] if (u, v) in self.variables['edges'][r])
                            ) - 2,
                            name=f"overtaking_lower_{i}_{j}_{u}_{v}"
                        )

        # Constraints (13) and (14): Prevent head-on collisions
        for i in self.variables['aircraft']:
            for j in self.variables['aircraft']:
                if i != j:
                    for (u, v) in self.variables['edges']:
                        if (v, u) in self.variables['edges']:  # Only consider bidirectional edges
                            # Equation (13)
                            self.model.addConstr(
                                self.variables['Z'][i, j, u] - self.variables['Z'][j, i, v] 
                                <= 2 - (
                                    quicksum(self.variables['Gamma'][i, r] for r in self.variables['routes'] if (u, v) in self.variables['edges'][r]) +
                                    quicksum(self.variables['Gamma'][j, r] for r in self.variables['routes'] if (v, u) in self.variables['edges'][r])
                                ),
                                name=f"headon_upper_{i}_{j}_{u}_{v}"
                            )
                            # Equation (14)
                            self.model.addConstr(
                                self.variables['Z'][i, j, u] + self.variables['Z'][j, i, v] 
                                >= (
                                    quicksum(self.variables['Gamma'][i, r] for r in self.variables['routes'] if (u, v) in self.variables['edges'][r]) +
                                    quicksum(self.variables['Gamma'][j, r] for r in self.variables['routes'] if (v, u) in self.variables['edges'][r])
                                ) - 2,
                                name=f"headon_lower_{i}_{j}_{u}_{v}"
                            )


class Release(Constraints):
    def add_constraints(self):
        # Equation (15): Arrival aircraft must not start earlier than their estimated touchdown time
        for j in self.variables['arrivals']:
            self.model.addConstr(
                self.variables['t'][j, self.variables['origin'][j]] >= self.variables['ETD'][j],
                name=f"release_arrival_{j}"
            )

        # Equation (16): Departure aircraft must not start earlier than their push-back time
        for i in self.variables['departures']:
            self.model.addConstr(
                self.variables['t'][i, self.variables['origin'][i]] >= self.variables['PBT'][i],
                name=f"release_departure_{i}"
            )


class Speed(Constraints):
    def add_constraints(self):
        # Constraints (19) and (20): Linearized speed limits
        for i in self.variables['aircraft']:
            for (u, v) in self.variables['edges']:
                self.model.addConstr(
                    (self.variables['t'][i, v] - self.variables['t'][i, u]) 
                    <= self.variables['length'][u, v] / self.variables['Smax'][u, v] 
                    + self.variables['M'] * (1 - quicksum(self.variables['Gamma'][i, r] for r in self.variables['routes'] if (u, v) in self.variables['edges'][r])),
                    name=f"speed_linear_max_{i}_{u}_{v}"
                )
                self.model.addConstr(
                    (self.variables['t'][i, v] - self.variables['t'][i, u]) 
                    >= self.variables['length'][u, v] / self.variables['Smin'][u, v] 
                    - self.variables['M'] * (1 - quicksum(self.variables['Gamma'][i, r] for r in self.variables['routes'] if (u, v) in self.variables['edges'][r])),
                    name=f"speed_linear_min_{i}_{u}_{v}"
                )


class Separation(Constraints):
    def add_constraints(self):
        # Constraints (23) and (24): Spatial separation between aircraft
        for i in self.variables['aircraft']:
            for j in self.variables['aircraft']:
                if i != j:
                    for (u, v) in self.variables['edges']:
                        # Equation (23): Ensure aircraft i and j do not collide on edge (u, v)
                        self.model.addConstr(
                            self.variables['t'][j, u] - self.variables['t'][i, v]
                            >= self.variables['Sep'] - self.variables['M'] * (
                                1 - quicksum(
                                    self.variables['Gamma'][i, r] * self.variables['Gamma'][j, r]
                                    for r in self.variables['routes']
                                    if (u, v) in self.variables['edges'][r]
                                )
                            ),
                            name=f"separation_{i}_{j}_{u}_{v}"
                        )

                        # Equation (24): Ensure aircraft j and i do not collide on edge (v, u)
                        self.model.addConstr(
                            self.variables['t'][i, u] - self.variables['t'][j, v]
                            >= self.variables['Sep'] - self.variables['M'] * (
                                1 - quicksum(
                                    self.variables['Gamma'][i, r] * self.variables['Gamma'][j, r]
                                    for r in self.variables['routes']
                                    if (v, u) in self.variables['edges'][r]
                                )
                            ),
                            name=f"separation_reverse_{i}_{j}_{u}_{v}"
                        )

class RunwayOccupancy(Constraints):
    def add_constraints(self):
        # Runway occupancy constraints
        for l in self.variables['runway_edges']:
            for i in self.variables['aircraft']:
                for j in self.variables['aircraft']:
                    if i != j:
                        # Ensure occupancy constraint is respected
                        self.model.addConstr(
                            self.variables['t'][i, l] + self.variables['T'][l, i, j] 
                            <= self.variables['t'][j, l] + self.variables['M'] * (1 - self.variables['rho'][i, j]),
                            name=f"runway_occupancy_upper_{i}_{j}_{l}"
                        )
                        self.model.addConstr(
                            self.variables['t'][j, l] + self.variables['T'][l, j, i] 
                            <= self.variables['t'][i, l] + self.variables['M'] * self.variables['rho'][i, j],
                            name=f"runway_occupancy_lower_{i}_{j}_{l}")


class Capacity(Constraints):
    def add_constraints(self):
        """
        Adds capacity constraints for runway crossing queues.
        Equation (33): Ensure aircraft at exit edges do not exceed prescribed capacity.
        """
        # Loop through each pair of aircraft and each runway exit edge
        for i in self.variables['aircraft']:
            for j in self.variables['aircraft']:
                if i != j:  # Avoid self-comparison
                    for l in self.variables['exit_edges']:
                        # Equation (33)
                        self.model.addConstr(
                            self.variables['t'][i, l] <= self.variables['T_l'][i, j, l],
                            name=f"capacity_{i}_{j}_{l}"
                        )



