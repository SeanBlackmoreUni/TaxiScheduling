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
        # I commented out 1-4 as they are already included in the creation of decision variables

        # # Equation (1): Z_{iju} is binary
        # for i in self.variables['aircraft']:
        #     for j in self.variables['aircraft']:
        #         for u in self.variables['all_nodes_per_aircraft'][i]:
        #             # print(f"YEEEEEEE: {u}")
        #             if i != j:
        #                 self.model.addConstr(
        #                     self.variables['Z'][i, j, u] >= 0,
        #                     name=f"Z_binary_lower_{i}_{j}_{u}"
        #                 )
        #                 self.model.addConstr(
        #                     self.variables['Z'][i, j, u] <= 1,
        #                     name=f"Z_binary_upper_{i}_{j}_{u}"
        #                 )

        # # Equation (2): Gamma_{ir} is binary
        # for i in self.variables['aircraft']:
        #     for r in range(len(self.variables['routes'][i])):
        #         self.model.addConstr(
        #             self.variables['Gamma'][i, r] >= 0,
        #             name=f"Gamma_binary_lower_{i}_{r}"
        #         )
        #         self.model.addConstr(
        #             self.variables['Gamma'][i, r] <= 1,
        #             name=f"Gamma_binary_upper_{i}_{r}"
        #         )

        # # Equation (3): rho_{ij} is binary
        # for i in self.variables['aircraft']:
        #     for j in self.variables['aircraft']:
        #         if i != j:
        #             self.model.addConstr(
        #                 self.variables['rho'][i, j] >= 0,
        #                 name=f"rho_binary_lower_{i}_{j}"
        #             )
        #             self.model.addConstr(
        #                 self.variables['rho'][i, j] <= 1,
        #                 name=f"rho_binary_upper_{i}_{j}"
        #             )

        # # Equation (4): t_{iu} is non-negative
        # for i in self.variables['aircraft']:
        #     for u in self.variables['nodes']:
        #         self.model.addConstr(
        #             self.variables['t'][i, u] >= 0,
        #             name=f"t_nonnegative_{i}_{u}"
        #         )

        # Equation (6): Each aircraft selects one route
        for i in self.variables['aircraft']:
            self.model.addConstr(
                quicksum(self.variables['Gamma'][i, r] for r in range(len(self.variables['routes'][i]))) == 1,
                name=f"route_selection_{i}"
            )

        # Equation (7): Z_{iju} logic constraint
        for i in self.variables['aircraft']:
            for j in self.variables['aircraft']:
                if i != j:
                    print(f"IIIIIIIII: {i}")
                    for u in [
                        item 
                        for item in self.variables['all_nodes_per_aircraft'][i]
                        if item in self.variables['all_nodes_per_aircraft'][j]
                    ]: 
                        print(f"UUUUUUUUUUU: {u}")
                        self.model.addConstr(
                            self.variables['Z'][i, j, u] <= quicksum(
                                self.variables['Gamma'][i, r]
                                for r in range(len(self.variables['routes'][i])) if u in self.variables['routes'][i][r]["nodes"]
                            ),
                            name=f"Z_logic_1_{i}_{j}_{u}"
                        )

        # Equation (8): Z_{iju} logic constraint for j
                        self.model.addConstr(
                            self.variables['Z'][i, j, u] <= quicksum(
                                self.variables['Gamma'][j, r]
                                for r in range(len(self.variables['routes'][j])) if u in self.variables['routes'][j][r]["nodes"]
                            ),
                            name=f"Z_logic_2_{i}_{j}_{u}"
                        )    


class Sequencing(Constraints):
    def add_constraints(self):
        # Constraints (9) and (10): Sequencing consistency
        for i in self.variables['aircraft']:
            for j in self.variables['aircraft']:
                if i != j:
                    for u in [
                        item 
                        for item in self.variables['all_nodes_per_aircraft'][i]
                        if item in self.variables['all_nodes_per_aircraft'][j]
                    ]:
                        # Equation (9)
                        self.model.addConstr(
                            self.variables['Z'][i, j, u] + self.variables['Z'][j, i, u] 
                            <= 3 - (
                                quicksum(self.variables['Gamma'][i, r] for r in range(len(self.variables['routes'][i])) if u in self.variables['routes'][i][r]["nodes"]) +
                                quicksum(self.variables['Gamma'][j, r] for r in range(len(self.variables['routes'][j])) if u in self.variables['routes'][j][r]["nodes"])
                            ),
                            name=f"sequencing_upper_{i}_{j}_{u}"
                        )
                        # Equation (10)
                        self.model.addConstr(
                            self.variables['Z'][i, j, u] + self.variables['Z'][j, i, u] 
                            >= 2 * (
                                quicksum(self.variables['Gamma'][i, r] for r in range(len(self.variables['routes'][i])) if u in self.variables['routes'][i][r]["nodes"]) +
                                quicksum(self.variables['Gamma'][j, r] for r in range(len(self.variables['routes'][j])) if u in self.variables['routes'][j][r]["nodes"])
                            ) - 3,
                            name=f"sequencing_lower_{i}_{j}_{u}"
                        )


class Overtaking(Constraints):
    def add_constraints(self):
        # Constraints (11) and (12): No overtaking on the same edge
        for i in self.variables['aircraft']:
            for j in self.variables['aircraft']:
                if i != j:
                    for (u, v) in [
                        item 
                        for item in self.variables['all_edges_per_aircraft'][i]
                        if item in self.variables['all_edges_per_aircraft'][j]
                    ]:
                        # Equation (11)
                        self.model.addConstr(
                            self.variables['Z'][i, j, u] - self.variables['Z'][i, j, v] 
                            <= 2 - (
                                quicksum(self.variables['Gamma'][i, r] for r in range(len(self.variables['routes'][i])) if (u, v) in self.variables['routes'][i][r]["edges"]) +
                                quicksum(self.variables['Gamma'][j, r] for r in range(len(self.variables['routes'][j])) if (u, v) in self.variables['routes'][j][r]["edges"])
                            ),
                            name=f"overtaking_upper_{i}_{j}_{u}_{v}"
                        )
                        # Equation (12)
                        self.model.addConstr(
                            self.variables['Z'][i, j, u] - self.variables['Z'][i, j, v] 
                            >= (
                                quicksum(self.variables['Gamma'][i, r] for r in range(len(self.variables['routes'][i])) if (u, v) in self.variables['routes'][i][r]["edges"]) +
                                quicksum(self.variables['Gamma'][j, r] for r in range(len(self.variables['routes'][j])) if (u, v) in self.variables['routes'][j][r]["edges"])
                            ) - 2,
                            name=f"overtaking_lower_{i}_{j}_{u}_{v}"
                        )

        # Constraints (13) and (14): Prevent head-on collisions
        for i in self.variables['aircraft']:
            for j in self.variables['aircraft']:
                if i != j:
                    for (u, v) in self.variables['all_edges_per_aircraft'][i]:
                        if (v, u) in self.variables['all_edges_per_aircraft'][j]:  # Only consider bidirectional edges
                            # Equation (13)
                            self.model.addConstr(
                                self.variables['Z'][i, j, u] - self.variables['Z'][j, i, v] 
                                <= 2 - (
                                    quicksum(self.variables['Gamma'][i, r] for r in range(len(self.variables['routes'][i])) if (u, v) in self.variables['routes'][i][r]["edges"]) +
                                    quicksum(self.variables['Gamma'][j, r] for r in range(len(self.variables['routes'][j])) if (v, u) in self.variables['routes'][j][r]["edges"])
                                ),
                                name=f"headon_upper_{i}_{j}_{u}_{v}"
                            )
                            # Equation (14)
                            self.model.addConstr(
                                self.variables['Z'][i, j, u] + self.variables['Z'][j, i, v] 
                                >= (
                                    quicksum(self.variables['Gamma'][i, r] for r in range(len(self.variables['routes'][i])) if (u, v) in self.variables['routes'][i][r]["edges"]) +
                                    quicksum(self.variables['Gamma'][j, r] for r in range(len(self.variables['routes'][j])) if (v, u) in self.variables['routes'][j][r]["edges"])
                                ) - 2,
                                name=f"headon_lower_{i}_{j}_{u}_{v}"
                            )


class Release(Constraints):
    def add_constraints(self):
        # Equation (15): Arrival aircraft must not start earlier than their estimated touchdown time
        for j in self.variables['arrivals']:
            #print(f"ETDDDDDD: {self.variables['ETD'][j]}")
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


# class Speed(Constraints):
#     def add_constraints(self):
#         # Constraints (19) and (20): Linearized speed limits
#         for i in self.variables['aircraft']:
#             for (u, v) in self.variables['edges']:
#                 self.model.addConstr(
#                     (self.variables['t'][i, v] - self.variables['t'][i, u]) 
#                     <= self.variables['length'][u, v] / self.variables['Smax'][u, v] 
#                     + self.variables['M'] * (1 - quicksum(self.variables['Gamma'][i, r] for r in range(len(self.variables['routes'][i])) if (u, v) in self.variables['routes'][i][r]["edges"])),
#                     name=f"speed_linear_max_{i}_{u}_{v}"
#                 )
#                 self.model.addConstr(
#                     (self.variables['t'][i, v] - self.variables['t'][i, u]) 
#                     >= self.variables['length'][u, v] / self.variables['Smin'][u, v] 
#                     - self.variables['M'] * (1 - quicksum(self.variables['Gamma'][i, r] for r in range(len(self.variables['routes'][i])) if (u, v) in self.variables['routes'][i][r]["edges"])),
#                     name=f"speed_linear_min_{i}_{u}_{v}"
#                 )


class Speed(Constraints):
    def add_constraints(self):
        # Constraints (19) and (20): Linearized speed limits
        for i in self.variables['aircraft']:
            for (u, v) in self.variables['all_edges_per_aircraft'][i]:
                # print(f'UUUUVVVV: {u, v}')
                x, y = (min(u, v), max(u, v))           # Only serves to properly look up the lengths, speeds etc.

                # Maximum speed constraint
                self.model.addConstr(
                    (self.variables['t'][i, v] - self.variables['t'][i, u]) 
                    <= (self.variables['length'][x, y] / self.variables['Smax'][x, y]) 
                    * (self.variables['M'] 
                    - self.variables['M'] * quicksum(
                        self.variables['Gamma'][i, r] 
                        for r in range(len(self.variables['routes'][i])) 
                        if (u, v) in self.variables['routes'][i][r]["edges"]
                    ) 
                    + quicksum(
                        self.variables['Gamma'][i, r] 
                        for r in range(len(self.variables['routes'][i])) 
                        if (u, v) in self.variables['routes'][i][r]["edges"]
                    )),
                    name=f"speed_linear_max_{i}_{u}_{v}"
                )
                # Minimum speed constraint
                self.model.addConstr(
                    (self.variables['t'][i, v] - self.variables['t'][i, u]) 
                    >= (self.variables['length'][x, y] / self.variables['Smin'][x, y]) 
                    * (self.variables['M'] * quicksum(
                        self.variables['Gamma'][i, r] 
                        for r in range(len(self.variables['routes'][i])) 
                        if (u, v) in self.variables['routes'][i][r]["edges"]
                    ) 
                    - self.variables['M'] 
                    + quicksum(
                        self.variables['Gamma'][i, r] 
                        for r in range(len(self.variables['routes'][i])) 
                        if (u, v) in self.variables['routes'][i][r]["edges"]
                    )),
                    name=f"speed_linear_min_{i}_{u}_{v}"
                )



# class Separation(Constraints):
#     def add_constraints(self):
#         # Constraints (23) and (24): Spatial separation between aircraft
#         for i in self.variables['aircraft']:
#             for j in self.variables['aircraft']:
#                 if i != j:
#                     for (u, v) in self.variables['edges']:
#                         # Equation (23): Ensure aircraft i and j do not collide on edge (u, v)
#                         self.model.addConstr(
#                             self.variables['t'][j, u] - self.variables['t'][i, v]
#                             >= self.variables['Sep'] - self.variables['M'] * (
#                                 1 - quicksum(
#                                     self.variables['Gamma'][i, r] * self.variables['Gamma'][j, r]
#                                     for r in self.variables['routes']
#                                     if (u, v) in self.variables['edges'][r]
#                                 )
#                             ),
#                             name=f"separation_{i}_{j}_{u}_{v}"
#                         )

#                         # Equation (24): Ensure aircraft j and i do not collide on edge (v, u)
#                         self.model.addConstr(
#                             self.variables['t'][i, u] - self.variables['t'][j, v]
#                             >= self.variables['Sep'] - self.variables['M'] * (
#                                 1 - quicksum(
#                                     self.variables['Gamma'][i, r] * self.variables['Gamma'][j, r]
#                                     for r in self.variables['routes']
#                                     if (v, u) in self.variables['edges'][r]
#                                 )
#                             ),
#                             name=f"separation_reverse_{i}_{j}_{u}_{v}"
#                         )

class Separation(Constraints):
    def add_constraints(self):
        # Constraints (23) and (24): Spatial separation between aircraft
        for i in self.variables['aircraft']:
            for j in self.variables['aircraft']:
                if i != j:
                    for (u, v) in self.variables['all_edges_per_aircraft'][i]:
                        if u in [
                            item 
                            for item in self.variables['all_nodes_per_aircraft'][i]
                            if item in self.variables['all_nodes_per_aircraft'][j]
                        ]:
                            x, y = (min(u, v), max(u, v))           # Only serves to properly look up the lengths, speeds etc.
                            # Equation (23): Ensure aircraft i and j do not collide on edge (u, v)
                            self.model.addConstr(
                                self.variables['t'][j, u] - self.variables['t'][i, u]
                                - (self.variables['Sep'] / self.variables['length'][x, y]) * (self.variables['t'][i, v] - self.variables['t'][i, u])
                                >= - self.variables['M'] * (3 - (self.variables['Z'][i, j, u]
                                + quicksum(
                                    self.variables['Gamma'][i, r]
                                    for r in range(len(self.variables['routes'][i]))
                                    if (u, v) in self.variables['routes'][i][r]["edges"]
                                )
                                + quicksum(
                                    self.variables['Gamma'][j, r]
                                    for r in range(len(self.variables['routes'][j]))
                                    if u in self.variables['routes'][j][r]["nodes"]
                                ))) ,
                                name=f"separation_{i}_{j}_{u}_{v}"
                            )

        for i in self.variables['aircraft']:
            for j in self.variables['aircraft']:
                if i != j:
                    for (w, v) in self.variables['all_edges_per_aircraft'][j]:
                        if v in [
                            item 
                            for item in self.variables['all_nodes_per_aircraft'][i]
                            if item in self.variables['all_nodes_per_aircraft'][j]
                        ]:
                            x, y = (min(w, v), max(w, v))           # Only serves to properly look up the lengths, speeds etc.
                            # Equation (24): Ensure aircraft i and j do not collide on edge (w, v)
                            self.model.addConstr(
                                self.variables['t'][i, v] - self.variables['t'][j, v]
                                - (self.variables['Sep'] / self.variables['length'][x, y]) * (self.variables['t'][j, v] - self.variables['t'][j, w])
                                >= - self.variables['M'] * (3 - (self.variables['Z'][j, i, v]
                                + quicksum(
                                    self.variables['Gamma'][j, r]
                                    for r in range(len(self.variables['routes'][j]))
                                    if (w, v) in self.variables['routes'][j][r]["edges"]
                                )
                                + quicksum(
                                    self.variables['Gamma'][i, r]
                                    for r in range(len(self.variables['routes'][i]))
                                    if v in self.variables['routes'][i][r]["nodes"]
                                ))),
                                name=f"separation_reverse_{i}_{j}_{w}_{v}"
                            )


class RunwayOccupancy(Constraints):
    def add_constraints(self):
        # Constraint 28
        for i in self.variables['departures']:
            for j in self.variables['departures']:
                if i != j:  # Ensure i and j are different aircraft
                    # Add the new linearization constraint
                    self.model.addConstr(
                        self.variables['t'][j, self.variables['destination'][j]] - 
                        self.variables['t'][i, self.variables['destination'][i]] - 
                        self.variables['Vi_j'] >= 
                        -(1 - self.variables['rho'][i, j]) * self.variables['M'],
                        name=f"runway_linearization_{i}_{j}_lower"
                    )

        # Runway occupancy constraints 31, 32
        for i in self.variables['departures']:
            for j in self.variables['arrivals']:
                for b in self.variables['runway_entry_nodes']:
                    if i != j:
                        if b in self.variables['all_nodes_per_aircraft'][j]:
                            # Ensure occupancy constraint is respected
                            self.model.addConstr(
                                self.variables['t'][j, b] - self.variables['t'][i, self.variables['destination'][i]] - self.variables['T']  
                                >= - self.variables['M'] * (1 - self.variables['rho'][i, j]),
                                name=f"runway_occupancy_upper_{i}_{j}_{b}"
                            )

        for i in self.variables['departures']:
            for j in self.variables['arrivals']:
                for a in self.variables['runway_exit_nodes']:
                    if i != j:
                        if a in self.variables['all_nodes_per_aircraft'][j]:                
                            self.model.addConstr(
                                self.variables['t'][i, self.variables['destination'][i]] - self.variables['t'][j, a]
                                >= - self.variables['M'] * (1 - self.variables['rho'][j, i]),
                                name=f"runway_occupancy_lower_{i}_{j}_{a}")


class Capacity(Constraints):
    def add_constraints(self):
        """
        Adds capacity constraints for runway crossing queues.
        Equation (33): Ensure aircraft at exit edges do not exceed prescribed capacity.
        This applies only to arrival aircraft.
        """
        # Loop through all pairs of arrival aircraft and each runway exit edge
        for i in self.variables['arrivals']:
            for j in self.variables['arrivals']:
                if i != j:  # Avoid self-comparison
                    for l in self.variables['exit_edges']:
                        # Add capacity constraint (Equation 33)
                        self.model.addConstr(
                            self.variables['t'][i, l] <= self.variables['T'], #[l, i, j],
                            name=f"capacity_{i}_{j}_{l}"
                        )

