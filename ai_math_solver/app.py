"""
AI Math Solver - College Project
A web-based mathematical problem solver using Python Flask
Supports: Algebra, Calculus, Trigonometry, Statistics, and more
"""

from flask import Flask, render_template_string, request, jsonify
import sympy as sp
from sympy import *
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
import re

app = Flask(__name__)

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Math Solver - Smart Mathematics Assistant</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
        }

        header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
            animation: fadeIn 1s ease-in;
        }

        header h1 {
            font-size: 3em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }

        header p {
            font-size: 1.2em;
            opacity: 0.9;
        }

        .main-card {
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            animation: slideUp 0.8s ease-out;
        }

        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }

        .tab-button {
            padding: 12px 24px;
            border: none;
            background: #f0f0f0;
            border-radius: 10px;
            cursor: pointer;
            font-size: 1em;
            transition: all 0.3s;
            font-weight: 600;
        }

        .tab-button:hover {
            background: #667eea;
            color: white;
            transform: translateY(-2px);
        }

        .tab-button.active {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }

        .input-section {
            margin-bottom: 30px;
        }

        .input-group {
            margin-bottom: 20px;
        }

        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #333;
            font-size: 1.1em;
        }

        input[type="text"], textarea, select {
            width: 100%;
            padding: 15px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 1.1em;
            transition: all 0.3s;
            font-family: 'Courier New', monospace;
        }

        input[type="text"]:focus, textarea:focus, select:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        textarea {
            resize: vertical;
            min-height: 100px;
        }

        .solve-button {
            width: 100%;
            padding: 18px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 1.2em;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .solve-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }

        .solve-button:active {
            transform: translateY(0);
        }

        .result-section {
            margin-top: 30px;
            padding: 25px;
            background: #f8f9fa;
            border-radius: 15px;
            display: none;
            animation: fadeIn 0.5s ease-in;
        }

        .result-section.show {
            display: block;
        }

        .result-title {
            font-size: 1.5em;
            color: #667eea;
            margin-bottom: 20px;
            font-weight: bold;
        }

        .result-content {
            background: white;
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #667eea;
            margin-bottom: 15px;
        }

        .result-item {
            margin-bottom: 15px;
            line-height: 1.8;
        }

        .result-item strong {
            color: #667eea;
            font-size: 1.1em;
        }

        .math-expression {
            background: #f0f0f0;
            padding: 15px;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            font-size: 1.2em;
            margin: 10px 0;
            overflow-x: auto;
        }

        .graph-container {
            text-align: center;
            margin-top: 20px;
        }

        .graph-container img {
            max-width: 100%;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }

        .error-message {
            background: #fee;
            color: #c00;
            padding: 15px;
            border-radius: 10px;
            border-left: 4px solid #c00;
        }

        .examples {
            background: #e3f2fd;
            padding: 20px;
            border-radius: 10px;
            margin-top: 20px;
        }

        .examples h3 {
            color: #1976d2;
            margin-bottom: 15px;
        }

        .example-item {
            background: white;
            padding: 10px 15px;
            margin: 8px 0;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            cursor: pointer;
            transition: all 0.3s;
        }

        .example-item:hover {
            background: #667eea;
            color: white;
            transform: translateX(5px);
        }

        .loader {
            display: none;
            text-align: center;
            padding: 20px;
        }

        .loader.show {
            display: block;
        }

        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }

        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }

        .feature-card {
            background: white;
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transition: all 0.3s;
        }

        .feature-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.2);
        }

        .feature-icon {
            font-size: 3em;
            margin-bottom: 10px;
        }

        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }

        @keyframes slideUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        @media (max-width: 768px) {
            header h1 {
                font-size: 2em;
            }
            
            .main-card {
                padding: 20px;
            }
            
            .tabs {
                flex-direction: column;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🧮 AI Math Solver</h1>
            <p>Your Smart Mathematics Assistant - Solve Any Math Problem Instantly</p>
        </header>

        <div class="main-card">
            <div class="tabs">
                <button class="tab-button active" onclick="showTab('algebra')">Algebra</button>
                <button class="tab-button" onclick="showTab('calculus')">Calculus</button>
                <button class="tab-button" onclick="showTab('equations')">Equations</button>
                <button class="tab-button" onclick="showTab('trigonometry')">Trigonometry</button>
                <button class="tab-button" onclick="showTab('statistics')">Statistics</button>
            </div>

            <div class="input-section">
                <div class="input-group">
                    <label for="problem-type">Select Problem Type:</label>
                    <select id="problem-type" onchange="updateExamples()">
                        <option value="simplify">Simplify Expression</option>
                        <option value="solve">Solve Equation</option>
                        <option value="derivative">Find Derivative</option>
                        <option value="integrate">Find Integral</option>
                        <option value="factor">Factor Expression</option>
                        <option value="expand">Expand Expression</option>
                        <option value="limit">Find Limit</option>
                        <option value="plot">Plot Graph</option>
                    </select>
                </div>

                <div class="input-group">
                    <label for="math-input">Enter Your Math Problem:</label>
                    <textarea id="math-input" placeholder="Example: x**2 + 5*x + 6"></textarea>
                </div>

                <button class="solve-button" onclick="solveProblem()">🚀 Solve Problem</button>
            </div>

            <div class="loader" id="loader">
                <div class="spinner"></div>
                <p style="margin-top: 15px; color: #667eea; font-weight: bold;">Solving your problem...</p>
            </div>

            <div class="result-section" id="result-section">
                <div class="result-title">📊 Solution:</div>
                <div id="result-content"></div>
            </div>

            <div class="examples">
                <h3>📝 Example Problems (Click to try):</h3>
                <div id="examples-list"></div>
            </div>
        </div>

        <div class="features">
            <div class="feature-card">
                <div class="feature-icon">🎯</div>
                <h3>Step-by-Step Solutions</h3>
                <p>Get detailed explanations for every problem</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">📈</div>
                <h3>Graph Visualization</h3>
                <p>See visual representations of functions</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">⚡</div>
                <h3>Instant Results</h3>
                <p>Lightning-fast calculations powered by AI</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">🔢</div>
                <h3>Multiple Topics</h3>
                <p>Algebra, Calculus, Statistics & More</p>
            </div>
        </div>
    </div>

    <script>
        const examples = {
            'simplify': ['(x**2 + 2*x + 1)/(x + 1)', 'sqrt(50) + sqrt(18)', '(x**2 - 4)/(x - 2)'],
            'solve': ['x**2 + 5*x + 6 = 0', '2*x + 3 = 7', 'x**2 - 4 = 0'],
            'derivative': ['x**3 + 2*x**2 + x', 'sin(x)*cos(x)', 'exp(x**2)'],
            'integrate': ['x**2', 'sin(x)', '1/(x**2 + 1)'],
            'factor': ['x**2 + 5*x + 6', 'x**3 - 8', 'x**2 - 9'],
            'expand': ['(x + 2)**3', '(x + 1)*(x - 1)', '(x + y)**2'],
            'limit': ['sin(x)/x, x, 0', '(x**2 - 1)/(x - 1), x, 1', '1/x, x, oo'],
            'plot': ['x**2', 'sin(x)', 'exp(-x**2)']
        };

        function updateExamples() {
            const problemType = document.getElementById('problem-type').value;
            const examplesList = document.getElementById('examples-list');
            examplesList.innerHTML = '';
            
            examples[problemType].forEach(ex => {
                const div = document.createElement('div');
                div.className = 'example-item';
                div.textContent = ex;
                div.onclick = () => {
                    document.getElementById('math-input').value = ex;
                };
                examplesList.appendChild(div);
            });
        }

        function showTab(tab) {
            const buttons = document.querySelectorAll('.tab-button');
            buttons.forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            
            // Update problem type based on tab
            const select = document.getElementById('problem-type');
            if (tab === 'algebra') select.value = 'simplify';
            if (tab === 'calculus') select.value = 'derivative';
            if (tab === 'equations') select.value = 'solve';
            if (tab === 'trigonometry') select.value = 'simplify';
            if (tab === 'statistics') select.value = 'simplify';
            
            updateExamples();
        }

        async function solveProblem() {
            const problemType = document.getElementById('problem-type').value;
            const mathInput = document.getElementById('math-input').value.trim();
            
            if (!mathInput) {
                alert('Please enter a math problem!');
                return;
            }

            // Show loader
            document.getElementById('loader').classList.add('show');
            document.getElementById('result-section').classList.remove('show');

            try {
                const response = await fetch('/solve', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        problem_type: problemType,
                        expression: mathInput
                    })
                });

                const data = await response.json();
                
                // Hide loader
                document.getElementById('loader').classList.remove('show');
                
                // Show result
                displayResult(data);
            } catch (error) {
                document.getElementById('loader').classList.remove('show');
                displayError('An error occurred. Please check your input and try again.');
            }
        }

        function displayResult(data) {
            const resultContent = document.getElementById('result-content');
            
            if (data.error) {
                resultContent.innerHTML = `<div class="error-message">${data.error}</div>`;
            } else {
                let html = '<div class="result-content">';
                
                if (data.original) {
                    html += `<div class="result-item"><strong>Original Expression:</strong><div class="math-expression">${data.original}</div></div>`;
                }
                
                if (data.result) {
                    html += `<div class="result-item"><strong>Result:</strong><div class="math-expression">${data.result}</div></div>`;
                }
                
                if (data.steps && data.steps.length > 0) {
                    html += '<div class="result-item"><strong>Steps:</strong><ol style="margin-left: 20px; margin-top: 10px;">';
                    data.steps.forEach(step => {
                        html += `<li style="margin: 8px 0;">${step}</li>`;
                    });
                    html += '</ol></div>';
                }
                
                if (data.graph) {
                    html += `<div class="graph-container"><img src="data:image/png;base64,${data.graph}" alt="Graph"></div>`;
                }
                
                html += '</div>';
                resultContent.innerHTML = html;
            }
            
            document.getElementById('result-section').classList.add('show');
        }

        function displayError(message) {
            const resultContent = document.getElementById('result-content');
            resultContent.innerHTML = `<div class="error-message">${message}</div>`;
            document.getElementById('result-section').classList.add('show');
        }

        // Initialize examples on load
        updateExamples();
    </script>
</body>
</html>
"""

def create_graph(expr_str, var='x'):
    """Create a graph for the given expression"""
    try:
        x = sp.Symbol('x')
        expr = parse_expr(expr_str, transformations='all')
        
        # Convert to numerical function
        f = sp.lambdify(x, expr, 'numpy')
        
        # Generate x values
        x_vals = np.linspace(-10, 10, 1000)
        y_vals = f(x_vals)
        
        # Create plot
        plt.figure(figsize=(10, 6))
        plt.plot(x_vals, y_vals, 'b-', linewidth=2)
        plt.grid(True, alpha=0.3)
        plt.axhline(y=0, color='k', linewidth=0.5)
        plt.axvline(x=0, color='k', linewidth=0.5)
        plt.xlabel('x', fontsize=12)
        plt.ylabel('f(x)', fontsize=12)
        plt.title(f'Graph of f(x) = {expr_str}', fontsize=14, fontweight='bold')
        
        # Save to base64
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()
        
        return img_base64
    except Exception as e:
        return None

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/solve', methods=['POST'])
def solve():
    try:
        data = request.json
        problem_type = data.get('problem_type')
        expression = data.get('expression')
        
        x, y, z = sp.symbols('x y z')
        result_data = {
            'original': expression,
            'result': '',
            'steps': [],
            'graph': None
        }
        
        # Parse the expression
        transformations = standard_transformations + (implicit_multiplication_application,)
        
        if problem_type == 'simplify':
            expr = parse_expr(expression, transformations=transformations)
            simplified = sp.simplify(expr)
            result_data['result'] = str(simplified)
            result_data['steps'] = [
                f'Original expression: {expr}',
                f'Apply simplification rules',
                f'Simplified form: {simplified}'
            ]
            
        elif problem_type == 'solve':
            # Handle equation
            if '=' in expression:
                lhs, rhs = expression.split('=')
                lhs_expr = parse_expr(lhs.strip(), transformations=transformations)
                rhs_expr = parse_expr(rhs.strip(), transformations=transformations)
                equation = sp.Eq(lhs_expr, rhs_expr)
            else:
                expr = parse_expr(expression, transformations=transformations)
                equation = sp.Eq(expr, 0)
            
            solutions = sp.solve(equation, x)
            result_data['result'] = f'x = {solutions}'
            result_data['steps'] = [
                f'Equation: {equation}',
                f'Apply solving techniques',
                f'Solutions: x = {solutions}'
            ]
            
        elif problem_type == 'derivative':
            expr = parse_expr(expression, transformations=transformations)
            derivative = sp.diff(expr, x)
            result_data['result'] = str(derivative)
            result_data['steps'] = [
                f'Function: f(x) = {expr}',
                f'Apply differentiation rules',
                f"Derivative: f'(x) = {derivative}"
            ]
            
        elif problem_type == 'integrate':
            expr = parse_expr(expression, transformations=transformations)
            integral = sp.integrate(expr, x)
            result_data['result'] = str(integral) + ' + C'
            result_data['steps'] = [
                f'Function: f(x) = {expr}',
                f'Apply integration rules',
                f'Integral: ∫f(x)dx = {integral} + C'
            ]
            
        elif problem_type == 'factor':
            expr = parse_expr(expression, transformations=transformations)
            factored = sp.factor(expr)
            result_data['result'] = str(factored)
            result_data['steps'] = [
                f'Expression: {expr}',
                f'Find common factors',
                f'Factored form: {factored}'
            ]
            
        elif problem_type == 'expand':
            expr = parse_expr(expression, transformations=transformations)
            expanded = sp.expand(expr)
            result_data['result'] = str(expanded)
            result_data['steps'] = [
                f'Expression: {expr}',
                f'Apply expansion rules',
                f'Expanded form: {expanded}'
            ]
            
        elif problem_type == 'limit':
            parts = expression.split(',')
            expr = parse_expr(parts[0].strip(), transformations=transformations)
            var = sp.Symbol(parts[1].strip())
            point = parts[2].strip()
            
            if point == 'oo':
                point = sp.oo
            else:
                point = parse_expr(point)
            
            limit_result = sp.limit(expr, var, point)
            result_data['result'] = str(limit_result)
            result_data['steps'] = [
                f'Function: {expr}',
                f'Variable: {var} → {point}',
                f'Limit: {limit_result}'
            ]
            
        elif problem_type == 'plot':
            expr = parse_expr(expression, transformations=transformations)
            result_data['result'] = f'Graph of f(x) = {expr}'
            result_data['graph'] = create_graph(expression)
            result_data['steps'] = [
                f'Function: f(x) = {expr}',
                'Plot the function over range [-10, 10]',
                'Graph displayed below'
            ]
        
        return jsonify(result_data)
        
    except Exception as e:
        return jsonify({'error': f'Error solving problem: {str(e)}'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)