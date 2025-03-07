from flask import Flask, render_template, request
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from ortools.linear_solver import pywraplp
import os

app = Flask(__name__)
os.makedirs('static', exist_ok=True)  # Ensure static directory exists

# Home route with form input and result
@app.route('/', methods=['GET', 'POST'])
def render_index():
    if request.method == 'POST':
        # Fetch input parameters
        client_width = float(request.form['client_width'])
        client_length = float(request.form['client_length'])
        raw_width = float(request.form['raw_width'])
        raw_length = float(request.form['raw_length'])
        gutter = float(request.form['gutter'])
        pull = float(request.form['pull'])
        max_width = float(request.form['max_width'])
        max_length = float(request.form['max_length'])
        layout = request.form['layout']

        # Calculate printing size
        print_width = client_width + 2 * gutter
        print_length = client_length + 2 * gutter

        # Ensure print size fits machine constraints
        if print_width > max_width or print_length > max_length:
            return render_template('index.html', error="Print size exceeds machine constraints.", result=None)

        # Optimization logic
        printing_size_outs = (raw_width // print_width) * (raw_length // print_length)
        standard_size_outs = (max_width // print_width) * (max_length // print_length)
        total_outs = printing_size_outs * standard_size_outs

        # Visualization
        fig, ax = plt.subplots()
        ax.set_title('Optimal Cut Layout')
        for i in range(int(printing_size_outs)):
            ax.add_patch(plt.Rectangle((i * print_width, 0), print_width, print_length, edgecolor='blue', facecolor='none'))
        plt.xlim(0, raw_width)
        plt.ylim(0, raw_length)
        plt.gca().set_aspect('equal', adjustable='box')
        plt.savefig('static/plot.png')

        return render_template('index.html', result={
            "printing_size": f"{print_width} x {print_length}",
            "printing_size_outs": printing_size_outs,
            "standard_size_outs": standard_size_outs,
            "total_outs": total_outs,
            "plot": '/static/plot.png'
        }, error=None)

    return render_template('index.html', result=None, error=None)

if __name__ == '__main__':
    app.run(debug=True)
