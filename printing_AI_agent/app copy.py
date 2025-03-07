# app.py - Flask application with Google OR-Tools for print optimization
from flask import Flask, request, jsonify, render_template
from ortools.linear_solver import pywraplp
import math

app = Flask(__name__)

# def optimize_printing(client_size, material_size, gutter, bleed, pull, machine_max_length, grain_direction, layout_orientation):
#     """
#     Optimize printing layout using Google OR-Tools

#     Parameters:
#     - client_size: tuple (length, width) - final required print size
#     - material_size: tuple (length, width) - available paper size
#     - gutter: float - spacing between printed items
#     - bleed: float - extra area for cutting accuracy
#     - pull: float - space for machine handling
#     - machine_max_length: float - maximum length that can be fed into machine
#     - grain_direction: str - 'any', 'lengthwise', or 'widthwise'
#     - layout_orientation: str - 'landscape', 'portrait', or 'flexible'

#     Returns:
#     - Dictionary with optimization results
#     """
#     client_length, client_width = client_size
#     material_length, material_width = material_size

#     # Calculate effective dimensions (including gutter and bleed)
#     effective_length = client_length + (2 * bleed) + gutter
#     effective_width = client_width + (2 * bleed) + gutter

#     # Initialize results
#     all_configurations = []

#     # Determine which orientations to check
#     client_orientations = []
#     if layout_orientation == 'flexible':
#         client_orientations = ['portrait', 'landscape']
#     else:
#         client_orientations = [layout_orientation]

#     # Check both material orientations
#     material_orientations = [
#         {"name": "Standard", "length": material_length, "width": material_width},
#         {"name": "Rotated", "length": material_width, "width": material_length}
#     ]

#     # Filter out material orientations that exceed machine constraints
#     valid_material_orientations = [
#         m for m in material_orientations
#         if m["width"] <= machine_max_length
#     ]

#     # Process all valid combinations
#     for client_orientation in client_orientations:
#         # Determine client piece dimensions based on orientation
#         if client_orientation == 'landscape':
#             piece_length = max(effective_length, effective_width)
#             piece_width = min(effective_length, effective_width)
#         else:  # portrait
#             piece_length = min(effective_length, effective_width)
#             piece_width = max(effective_length, effective_width)

#         for material_option in valid_material_orientations:
#             mat_length = material_option["length"]
#             mat_width = material_option["width"]

#             # Skip if grain direction constraints are not met
#             if grain_direction == 'lengthwise' and material_option["name"] == "Rotated":
#                 continue
#             if grain_direction == 'widthwise' and material_option["name"] == "Standard":
#                 continue

#             # Calculate how many pieces can fit in each direction
#             pieces_along_length = math.floor((mat_length - pull) / piece_length)
#             pieces_along_width = math.floor((mat_width - pull) / piece_width)

#             # Calculate total pieces on this sheet
#             total_pieces = pieces_along_length * pieces_along_width

#             if total_pieces > 0:
#                 # Calculate standard sheet outs (based on raw material size)
#                 # This represents how many raw material sheets are needed for this configuration
#                 standard_sheet_outs = math.ceil((total_pieces * piece_length * piece_width) / (mat_length * mat_width))

#                 # Calculate the efficiency
#                 efficiency = (total_pieces * piece_length * piece_width) / (mat_length * mat_width) * 100

#                 # Store the configuration
#                 config = {
#                     "materialOrientation": material_option["name"],
#                     "clientOrientation": client_orientation,
#                     "printingSize": {"length": piece_length, "width": piece_width},  # Dynamic size
#                     "actualPrintingSize": {"length": piece_length, "width": piece_width},
#                     "piecesAlongLength": pieces_along_length,
#                     "piecesAlongWidth": pieces_along_width,
#                     "printingOuts": total_pieces,
#                     "standardSizeOuts": standard_sheet_outs,
#                     "totalOuts": total_pieces * standard_sheet_outs,
#                     "efficiency": efficiency
#                 }

#                 all_configurations.append(config)

#     # Sort configurations by total outs (descending)
#     all_configurations.sort(key=lambda x: x["totalOuts"], reverse=True)

#     # If no valid configuration was found
#     if not all_configurations:
#         return {
#             "printingSize": {"length": 0, "width": 0},
#             "printingOuts": 0,
#             "standardSizeOuts": 0,
#             "totalOuts": 0,
#             "configurations": [],
#             "bestConfig": None
#         }

#     # Get the best configuration
#     best_config = all_configurations[0]

#     return {
#         "printingSize": best_config["printingSize"],  # Dynamic size from the best config
#         "printingOuts": best_config["printingOuts"],
#         "standardSizeOuts": best_config["standardSizeOuts"],
#         "totalOuts": best_config["totalOuts"],
#         "configurations": all_configurations,
#         "bestConfig": best_config
#     }

# def optimize_printing(client_size, material_size, gutter, bleed, pull, machine_max_length, grain_direction, layout_orientation):
#     """
#     Optimize printing layout using a precomputation approach.

#     Parameters:
#     - client_size: tuple (length, width) - final required print size
#     - material_size: tuple (length, width) - available paper size
#     - gutter: float - spacing between printed items
#     - bleed: float - extra area for cutting accuracy
#     - pull: float - space for machine handling
#     - machine_max_length: float - maximum length that can be fed into machine
#     - grain_direction: str - 'any', 'lengthwise', or 'widthwise'
#     - layout_orientation: str - 'landscape', 'portrait', or 'flexible'

#     Returns:
#     - Dictionary with optimization results
#     """
#     client_length, client_width = client_size
#     material_length, material_width = material_size

#     # Calculate effective dimensions (including gutter and bleed)
#     effective_length = client_length + (2 * bleed) + gutter
#     effective_width = client_width + (2 * bleed) + gutter

#     # Initialize results
#     all_configurations = []

#     # Determine which orientations to check
#     client_orientations = []
#     if layout_orientation == 'flexible':
#         client_orientations = ['portrait', 'landscape']
#     else:
#         client_orientations = [layout_orientation]

#     # Check both material orientations
#     material_orientations = [
#         {"name": "Standard", "length": material_length, "width": material_width},
#         {"name": "Rotated", "length": material_width, "width": material_length}
#     ]

#     # Process all valid combinations
#     for client_orientation in client_orientations:
#         # Determine client piece dimensions based on orientation
#         if client_orientation == 'landscape':
#             piece_length = max(effective_length, effective_width)
#             piece_width = min(effective_length, effective_width)
#         else:  # portrait
#             piece_length = min(effective_length, effective_width)
#             piece_width = max(effective_length, effective_width)

#         for material_option in material_orientations:
#             mat_length = material_option["length"]
#             mat_width = material_option["width"]

#             # Skip if material width exceeds machine constraints
#             if mat_width > machine_max_length:
#                 continue

#             # Skip if grain direction constraints are not met
#             if grain_direction == 'lengthwise' and material_option["name"] == "Rotated":
#                 continue
#             if grain_direction == 'widthwise' and material_option["name"] == "Standard":
#                 continue

#             # Calculate maximum number of pieces along length and width
#             max_pieces_along_length = int((mat_length - pull) // piece_length)
#             max_pieces_along_width = int((mat_width - pull) // piece_width)

#             # If no valid configuration is possible, skip
#             if max_pieces_along_length <= 0 or max_pieces_along_width <= 0:
#                 continue

#             # Precompute the total number of pieces for all valid combinations
#             total_pieces = max_pieces_along_length * max_pieces_along_width

#             # Calculate efficiency
#             efficiency = (total_pieces * piece_length * piece_width) / (mat_length * mat_width) * 100

#             # Store the configuration
#             config = {
#                 "materialOrientation": material_option["name"],
#                 "clientOrientation": client_orientation,
#                 "printingSize": {"length": piece_length, "width": piece_width},
#                 "piecesAlongLength": max_pieces_along_length,
#                 "piecesAlongWidth": max_pieces_along_width,
#                 "printingOuts": total_pieces,
#                 "efficiency": efficiency,
#             }

#             all_configurations.append(config)

#     # Sort configurations by total outs (descending)
#     all_configurations.sort(key=lambda x: x["printingOuts"], reverse=True)

#     # If no valid configuration was found
#     if not all_configurations:
#         return {
#             "printingSize": {"length": 0, "width": 0},
#             "printingOuts": 0,
#             "configurations": [],
#             "bestConfig": None
#         }

#     # Get the best configuration
#     best_config = all_configurations[0]

#     return {
#         "printingSize": best_config["printingSize"],  # Dynamic size from the best config
#         "printingOuts": best_config["printingOuts"],
#         "configurations": all_configurations,
#         "bestConfig": best_config
#     }

def optimize_printing(client_size, material_size, gutter, bleed, pull, machine_max_length, grain_direction, layout_orientation):
    """
    Optimize printing layout using a precomputation approach.

    Parameters:
    - client_size: tuple (length, width) - final required print size
    - material_size: tuple (length, width) - available paper size
    - gutter: float - spacing between printed items
    - bleed: float - extra area for cutting accuracy
    - pull: float - space for machine handling
    - machine_max_length: float - maximum length that can be fed into machine
    - grain_direction: str - 'any', 'lengthwise', or 'widthwise'
    - layout_orientation: str - 'landscape', 'portrait', or 'flexible'

    Returns:
    - Dictionary with optimization results
    """
    client_length, client_width = client_size
    material_length, material_width = material_size

    # Calculate effective dimensions (including gutter and bleed)
    effective_length = client_length + (2 * bleed) + gutter
    effective_width = client_width + (2 * bleed) + gutter

    # Initialize results
    all_configurations = []

    # Determine which orientations to check
    client_orientations = []
    if layout_orientation == 'flexible':
        client_orientations = ['portrait', 'landscape']
    else:
        client_orientations = [layout_orientation]

    # Check both material orientations
    material_orientations = [
        {"name": "Standard", "length": material_length, "width": material_width},
        {"name": "Rotated", "length": material_width, "width": material_length}
    ]

    # Process all valid combinations
    for client_orientation in client_orientations:
        # Determine client piece dimensions based on orientation
        if client_orientation == 'landscape':
            piece_length = max(effective_length, effective_width)
            piece_width = min(effective_length, effective_width)
        else:  # portrait
            piece_length = min(effective_length, effective_width)
            piece_width = max(effective_length, effective_width)

        for material_option in material_orientations:
            mat_length = material_option["length"]
            mat_width = material_option["width"]

            # Skip if material width exceeds machine constraints
            if mat_width > machine_max_length:
                continue

            # Skip if grain direction constraints are not met
            if grain_direction == 'lengthwise' and material_option["name"] == "Rotated":
                continue
            if grain_direction == 'widthwise' and material_option["name"] == "Standard":
                continue

            # Calculate maximum number of pieces along length and width
            max_pieces_along_length = int((mat_length - pull) // piece_length)
            max_pieces_along_width = int((mat_width - pull) // piece_width)

            # If no valid configuration is possible, skip
            if max_pieces_along_length <= 0 or max_pieces_along_width <= 0:
                continue

            # Precompute the total number of pieces for all valid combinations
            total_pieces = max_pieces_along_length * max_pieces_along_width

            # Calculate efficiency
            efficiency = (total_pieces * piece_length * piece_width) / (mat_length * mat_width) * 100

            # Calculate standard size outs (assuming standard material size)
            standard_size_outs = int(material_length // effective_length) * int(material_width // effective_width)

            # Store the configuration
            config = {
                "materialOrientation": material_option["name"],
                "clientOrientation": client_orientation,
                "printingSize": {"length": piece_length, "width": piece_width},
                "piecesAlongLength": max_pieces_along_length,
                "piecesAlongWidth": max_pieces_along_width,
                "printingOuts": total_pieces,
                "standardSizeOuts": standard_size_outs,
                "efficiency": efficiency,
            }

            all_configurations.append(config)

    # Sort configurations by total outs (descending)
    all_configurations.sort(key=lambda x: x["printingOuts"], reverse=True)

    # If no valid configuration was found
    if not all_configurations:
        return {
            "printingSize": {"length": 0, "width": 0},
            "printingOuts": 0,
            "standardSizeOuts": 0,
            "configurations": [],
            "bestConfig": None
        }

    # Get the best configuration
    best_config = all_configurations[0]

    return {
        "printingSize": best_config["printingSize"],  # Dynamic size from the best config
        "printingOuts": best_config["printingOuts"],
        "standardSizeOuts": best_config["standardSizeOuts"],
        "configurations": all_configurations,
        "bestConfig": best_config
    }

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/optimize', methods=['POST'])
def optimize():
    data = request.json
    
    # Extract input parameters
    client_size = (float(data['clientLength']), float(data['clientWidth']))
    material_size = (float(data['materialLength']), float(data['materialWidth']))
    gutter = float(data['gutter'])
    bleed = float(data['bleed'])
    pull = float(data['pull'])
    machine_max_length = float(data['machineMaxLength'])
    grain_direction = data['grainDirection']
    layout_orientation = data['orientation']
    
    # Call optimization function
    results = optimize_printing(
        client_size, 
        material_size,
        gutter,
        bleed,
        pull,
        machine_max_length,
        grain_direction,
        layout_orientation
    )
    
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True) 