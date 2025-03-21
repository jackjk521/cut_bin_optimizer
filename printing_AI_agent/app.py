from flask import Flask, request, render_template, jsonify
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use a non-interactive backend
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/'

# Ensure static directory exists
if not os.path.exists('static'):
    os.makedirs('static')

# Save plot function with gutter visualization
def save_plot(rectangles, width, height, gutter, filename):
    plt.figure(figsize=(10, 10))
    
    # Expand plot limits slightly to prevent clipping
    plt.xlim(-0.5, width + 0.5)
    plt.ylim(-0.5, height + 0.5)
    
    # Show every second tick to reduce clutter
    plt.xticks([i for i in range(0, int(width) + 1, 2)])
    plt.yticks([i for i in range(0, int(height) + 1, 2)])
    
    for rect in rectangles:
        x, y, w, h = rect
        # Draw rectangle with thicker outline
        plt.gca().add_patch(plt.Rectangle((x, y), w, h, edgecolor='blue', fill=False, linewidth=2))
        
        # Add gutter as dashed lines (for visualization)
        plt.gca().add_patch(plt.Rectangle((x - gutter / 2, y - gutter / 2), w + gutter, h + gutter,
                                          edgecolor='gray', fill=False, linestyle='--', linewidth=1))
        
        # Add label inside rectangle in the new format
        label = f"{w}\nx\n{h}"
        plt.text(x + w / 2, y + h / 2, label, ha='center', va='center', fontsize=10, color='black')
    
    # Improve grid visibility and reduce clutter
    plt.grid(True, which='major', color='gray', linestyle='--', linewidth=0.5)
    plt.minorticks_off()  # Disable minor grid lines for clarity
    
    # Ensure equal aspect ratio
    plt.gca().set_aspect('equal', adjustable='box')
    
    # Save plot with all content visible
    plt.tight_layout()
    plt.savefig(filename, bbox_inches='tight')
    plt.close()

    return len(rectangles)


# Generate cut layout including gutter on all sides
def generate_cut_layout(client_w, client_h, raw_w, raw_h, gutter):
    rectangles = []
    y = 0  # Start directly from 0

    while y + client_h + gutter <= raw_h or abs(y + client_h + gutter - raw_h) < 1e-6:
        x = 0  # Start each row directly from 0

        while x + client_w + gutter <= raw_w or abs(x + client_w + gutter - raw_w) < 1e-6:
            rectangles.append((x, y, client_w, client_h))
            x += client_w + gutter  # Move right by client width + gutter

        y += client_h + gutter  # Move up by client height + gutter

    return rectangles


# Find optimal printing size
def find_optimal_printing_size(client_w, client_h, max_w, max_h, gutter, step=0.25):
    best_size = (0, 0)
    max_outs = 0
    effective_w = client_w + gutter
    effective_h = client_h + gutter
    for w in range(int(max_w / gutter)):
        for h in range(int(max_h / gutter)):
            pw = (w + 1) * gutter
            ph = (h + 1) * gutter
            if pw > max_w or ph > max_h:
                continue
            outs = (pw // effective_w) * (ph // effective_h)
            if outs > max_outs:
                max_outs = outs
                best_size = (pw, ph)
    return best_size, max_outs

# Generate and save layout showing optimal sheets in raw material
def save_sheet_layout(client_w, client_h, raw_w, raw_h, optimal_w, optimal_h, gutter, filename):
    rectangles = []
    x, y = 0, 0
    num_sheets = 0
    while y + optimal_h <= raw_h:
        while x + optimal_w <= raw_w:
            sheet_rect = (x, y, optimal_w, optimal_h)
            rectangles.append(sheet_rect)
            num_sheets += 1
            x += optimal_w
        x = 0
        y += optimal_h
    num_sheets = save_plot(rectangles, raw_w, raw_h, gutter, filename)
    return num_sheets


@app.route('/')
def render_index():
    return render_template('index.html')

@app.route('/optimize', methods=['POST'])
def optimize():
    try:
        client_w = float(request.form['client_width'])
        client_h = float(request.form['client_length'])
        num_booklets = float(request.form['num_booklets'])
        num_shts_per_booklet = float(request.form['num_shts_per_booklet'])
        wastage_allowance = float(request.form['wastage_allowance'])
        raw_w = float(request.form['raw_width'])
        raw_h = float(request.form['raw_length'])
        gutter = float(request.form['gutter'])
        max_w = float(request.form['max_width'])
        max_h = float(request.form['max_length'])

        # Generate raw material cut layout
        raw_rectangles = generate_cut_layout(client_w, client_h, raw_w, raw_h, gutter)
        raw_file = 'static/raw_layout.png'
        total_outs = save_plot(raw_rectangles, raw_w, raw_h, gutter, raw_file)

        # Find optimal printing size
        best_size, _ = find_optimal_printing_size(client_w, client_h, max_w, max_h, gutter)
        print_file = 'static/print_layout.png'
        print_rectangles = generate_cut_layout(client_w, client_h, best_size[0], best_size[1], gutter)
        printing_size_outs = save_plot(print_rectangles, best_size[0], best_size[1], gutter, print_file)

       # Generate sheet layout and calculate total outs
        sheet_file = 'static/sheet_layout.png'
        standard_size_outs = save_sheet_layout(client_w, client_h, raw_w, raw_h, best_size[0], best_size[1], gutter, sheet_file)
        # total_outs = num_sheets * outs_per_sheet

        # Compute for number of sheets
        total_sheets = num_booklets *  num_shts_per_booklet
        total_w_wastage_amt = total_sheets * (1 + (wastage_allowance / 100)) 
        total_raw_mat_used = round(total_w_wastage_amt/total_outs)

        return jsonify({
            "raw_layout": raw_file,
            "print_layout": print_file,
            "sheet_layout": sheet_file,
            "best_size": f"{best_size[0]} x {best_size[1]}",
            "printing_size_outs": printing_size_outs,
            "total_outs": total_outs,
            "standard_size_outs": standard_size_outs,

            "total_sheets": total_sheets,
            "total_w_wastage_amt": total_w_wastage_amt,
            "total_raw_mat_used": total_raw_mat_used

            # "outs_per_sheet": outs_per_sheet,
            # "total_outs": total_outs
        })
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(debug=True)
