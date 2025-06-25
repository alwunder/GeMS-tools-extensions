import os
import pandas as pd
import networkx as nx
import pydot # needs pygraphviz, install from python console: "conda install --channel conda-forge pygraphviz"

# Load dataset
ver = "28"  # Update this with current version number (propagates throughout script)
# folder = "C:\\GIS\\TOOLS\\PyCharmProjects\\AdvancedUnitSorting\\"
folder =  "G:\\Other computers\\My Work Computer\\GIS\\TOOLS\\PyCharmProjects\\AdvancedUnitSorting\\"
# file_path = f"{folder}UnitSort test {ver} DATA NoCoal.txt"  # Update this with test data tab-delimited txt file
# Demo errors path
file_path = f"UnitSort test {ver} DATA SHOW ERRORS.txt"
df = pd.read_csv(file_path, delimiter="\t")


# Sort the entire table by HierarchyKey first (this ensures primary grouping)
df = df.sort_values(by="HierarchyKeyAge", key=lambda x: x.str.split("-"))

# Dictionary to store sorted results
sorted_units = []

# Process each HierarchyKey independently
for hk, group_df in df.groupby("HierarchyKeyAge", sort=False):
    # Create a directed graph from the MapUnits in the HierarchyKey
    graph = nx.DiGraph()

    # Add nodes and edges
    for _, row in group_df.iterrows():
        #unitGroup = row["Unit"] + " (" + row["Group"] + ")"
        group = row["Group"]
        unit = row["Unit"]
        above = row["UnitAbove"] if pd.notna(row["UnitAbove"]) else None
        below = row["UnitBelow"] if pd.notna(row["UnitBelow"]) else None
        unitId = row["SORT"]

        # Add each unit as a node in the graph
        graph.add_node(unit)

        # Create edges between nodes based on unit above and unit below
        if above and above in group_df["Unit"].values:
            graph.add_edge(above, unit)  # UnitAbove → Unit edge
        if below and below in group_df["Unit"].values:
            graph.add_edge(unit, below)  # Unit → UnitBelow edge


    try:
        # Perform topological sorting within the HierarchyKey group
        sorted_list = list(nx.topological_sort(graph))
        sorted_units.extend([(unit, hk) for unit in sorted_list])
        # Draw a flowchart explaining the relationships between the units in the topologically sorted list
        nx.drawing.nx_agraph.write_dot(graph, f"{folder}Images\\{ver}\\UnitSort test {ver} graph {hk}.dot")
        (plot,) = pydot.graph_from_dot_file(f"{folder}Images\\{ver}\\UnitSort test {ver} graph {hk}.dot")
        plot.write_png(f"{folder}Images\\{ver}\\UnitSort test {ver} graph {hk}.png")
        os.remove(f"{folder}Images\\{ver}\\UnitSort test {ver} graph {hk}.dot")
        print(f"See 'UnitSort test {ver} graph {hk}.png' for diagram of sorted units in {hk}.")
    except nx.NetworkXUnfeasible:
        # This happens when there is an impossible relationship, i.e., a unit is both a parent and a child (cycle)
        print(f"Cycle detected in HierarchyKey {hk}; Unable to resolve directed graph, "
              f"items in this key will not be added to the final sorted list. "
              f"\n  Check the following for help resolving the error:")
        # Reports the units involved in the cycle error
        print(f"  Error(s) found in the sequence of the following units: {list(nx.chordless_cycles(graph))}")
        print(f"  cycle_basis for {hk}: {list(nx.simple_cycles(graph))}")
        # Find all simple cycles for error reporting
        errorCycles = list(nx.simple_cycles(graph))
        # Extract closing edges
        closing_edges = []
        for cycle in errorCycles:
            if len(cycle) > 1:
                # The edge from last node to the first closes the cycle
                closing_edge = (cycle[-1], cycle[0])
                closing_edges.append(closing_edge)
        # Print results
        print(f"  Detected cycle(s):")
        for cycle in errorCycles:
            print("   ", cycle)
        print(f"  Closing edge of each detected cycle(s):")
        for edge in closing_edges:
            print("   ", edge)

        # Draw a flowchart explaining the relationships (cycle) between the units causing the error
        nx.drawing.nx_agraph.write_dot(graph, f"{folder}Images\\{ver}\\UnitSort test {ver} graph error {hk}.dot")
        (plot,) = pydot.graph_from_dot_file(f"{folder}Images\\{ver}\\UnitSort test {ver} graph error {hk}.dot")
        plot.write_png(f"{folder}Images\\{ver}\\UnitSort test {ver} graph error {hk}.png")
        # Don't remove the dot file, so it can be edited to show error in different color
        #os.remove(f"{folder}Images\\UnitSort test {ver} cycle {unitId}.dot")
        try:
            print(f"  Check 'UnitSort test {ver} graph error {hk}.png' for diagram of graph error.")
            #print(f"  find_cycle: {nx.find_cycle(graph, orientation='original')}")
        except nx.NetworkXNoCycle:
            #print("  networkx.exception.NetworkXNoCycle: No cycle found.")
            continue


# Convert to DataFrame and output sorted data
sorted_df = pd.DataFrame(sorted_units, columns=["Unit", "HierarchyKeyAge"])
print(sorted_df)
sorted_df.to_csv(f"{folder}UnitSort test {ver} RESULTS NoCoal.txt", sep='\t', index=False)
