from flask import Flask, request, jsonify
from flask_cors import CORS
import sympy as sp
from sympy.logic.boolalg import Implies, Equivalent, Not, Or, And, Xor
import re

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Health check endpoint
@app.route('/', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

def replace_logical_symbols(argument_str):
    replacements = {
        '=>': 'Implies',        # Implies
        '<=>': 'Equivalent',    # Biconditional (Equivalent)
        '∧': 'And',             # And
        '∨': 'Or',              # Or
        '¬': 'Not',             # Not
        '~': 'Not',             # Not
        '⊕': 'Xor'              # Exclusive Or
    }
    
    for old, new in replacements.items():
        argument_str = re.sub(r'\b{}\b'.format(re.escape(old)), new, argument_str)
    
    return argument_str

def build_sympy_expr(expr_str, symbols_dict):
    expr_str = replace_logical_symbols(expr_str)
    
    # Handle negations separately
    if expr_str.startswith('Not(') and expr_str.endswith(')'):
        return Not(build_sympy_expr(expr_str[4:-1], symbols_dict))
    elif expr_str.startswith('Not '):
        return Not(build_sympy_expr(expr_str[4:], symbols_dict))
    elif expr_str.startswith('¬') or expr_str.startswith('~'):
        return Not(build_sympy_expr(expr_str[1:].strip(), symbols_dict))

    # Check for parentheses
    if expr_str.startswith('(') and expr_str.endswith(')'):
        return build_sympy_expr(expr_str[1:-1], symbols_dict)
    
    # Handle binary operations
    for operator in ['Implies', 'Equivalent', 'And', 'Or', 'Xor']:
        if operator in expr_str:
            left, right = expr_str.split(operator)
            return eval(f"{operator}({build_sympy_expr(left.strip(), symbols_dict)}, {build_sympy_expr(right.strip(), symbols_dict)})", {**symbols_dict, **globals()})
    
    # Handle symbols
    if expr_str in symbols_dict:
        return symbols_dict[expr_str]
    else:
        raise ValueError(f"Unknown symbol: {expr_str}")

def parse_input(argument_str):
    # Define the symbols
    symbols_dict = {symbol: sp.Symbol(symbol) for symbol in 'P Q R S T U V W X Y Z'.split()}
    
    # Split the input into premises and conclusion
    parts = argument_str.split('therefore')
    premises_str = parts[0].strip().split(',')
    conclusion_str = parts[1].strip()

    # Parse premises
    premises = [build_sympy_expr(premise.strip(), symbols_dict) for premise in premises_str]
    
    # Parse conclusion
    conclusion = build_sympy_expr(conclusion_str, symbols_dict)
    
    return premises + [conclusion]

def generate_truth_table(expressions):
    # Extract symbols
    symbols = sorted(set.union(*[expr.free_symbols for expr in expressions]), key=str)

    # Generate all possible truth values
    truth_values = list(sp.utilities.iterables.product([True, False], repeat=len(symbols)))

    # Generate the truth table
    table = []
    for values in truth_values:
        valuation = dict(zip(symbols, values))
        row = [valuation[sym] for sym in symbols] + [expr.subs(valuation) for expr in expressions]
        table.append(row)

    return table, symbols

def is_valid_argument(expressions):
    premises = expressions[:-1]
    conclusion = expressions[-1]

    # Extract symbols
    symbols = sorted(set.union(*[expr.free_symbols for expr in expressions]), key=str)

    # Generate all possible truth values
    truth_values = list(sp.utilities.iterables.product([True, False], repeat=len(symbols)))

    # Check validity
    for values in truth_values:
        valuation = dict(zip(symbols, values))
        if all(premise.subs(valuation) for premise in premises) and not conclusion.subs(valuation):
            return False, valuation

    return True, None


def format_truth_table(table, symbols, expressions):
    header = symbols + expressions
    rows = [[str(cell) for cell in row] for row in table]
    return {'header': [str(h) for h in header], 'rows': rows}

@app.route('/evaluate', methods=['POST'])
def evaluate():
    data = request.get_json()
    argument = data['argument']
    try:
        print(argument)
        expressions = parse_input(argument)
        valid, counter_example = is_valid_argument(expressions)
        table, symbols = generate_truth_table(expressions)
        truth_table = format_truth_table(table, symbols, expressions)
        if valid:
            return jsonify({'message': 'The argument is valid.', 'truthTable': truth_table})
        else:
            return jsonify({'message': f'The argument is invalid. Counter example: {counter_example}', 'truthTable': truth_table})
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 400

if __name__ == '__main__':
    app.run(debug=True)
