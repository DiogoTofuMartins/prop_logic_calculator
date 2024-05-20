from flask import Flask, request, jsonify
from flask_cors import CORS
import sympy as sp
from sympy.logic.boolalg import Implies, Equivalent, Not, Or, And, Xor
from sympy import symbols

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def replace_logical_symbols(argument_str):
    replacements = {
        '<=>': 'Equivalent',    # Biconditional (Equivalent)
        '=>': 'Implies',        # Implies
        '∧': 'And',             # And
        '∨': 'Or',              # Or
        '¬': 'Not',             # Not
        '~': 'Not',             # Not
        '⊕': 'Xor'              # Exclusive Or
    }
    
    for old, new in replacements.items():
        argument_str = argument_str.replace(old, f' {new} ')
    
    return argument_str

def tokenize(expression):
    tokens = []
    token = ""
    i = 0
    while i < len(expression):
        if expression[i].isspace():
            if token:
                tokens.append(token)
                token = ""
        elif expression[i] in "∧∨¬⊕()":
            if token:
                tokens.append(token)
                token = ""
            tokens.append(expression[i])
        elif expression[i:i+2] in ["=>", "<="]:
            if token:
                tokens.append(token)
                token = ""
            tokens.append(expression[i:i+2])
            i += 1
        elif expression[i:i+3] == "<=>":
            if token:
                tokens.append(token)
                token = ""
            tokens.append(expression[i:i+3])
            i += 2
        else:
            token += expression[i]
        i += 1
    if token:
        tokens.append(token)
    return tokens

def parse_tokens(tokens, symbols_dict):
    precedence = {'Not': 3, 'And': 2, 'Or': 1, 'Implies': 0, 'Equivalent': 0}
    output = []
    operators = []

    def apply_operator(op):
        if op == 'Not':
            operand = output.pop()
            output.append(Not(operand))
        else:
            right = output.pop()
            left = output.pop()
            if op == 'And':
                output.append(And(left, right))
            elif op == 'Or':
                output.append(Or(left, right))
            elif op == 'Implies':
                output.append(Implies(left, right))
            elif op == 'Equivalent':
                output.append(Equivalent(left, right))
            elif op == 'Xor':
                output.append(left ^ right)

    for token in tokens:
        if token in symbols_dict:
            output.append(symbols_dict[token])
        elif token == '(':
            operators.append(token)
        elif token == ')':
            while operators and operators[-1] != '(':
                apply_operator(operators.pop())
            operators.pop()  # Remove '('
        elif token in precedence:
            while (operators and operators[-1] in precedence and
                   precedence[operators[-1]] >= precedence[token]):
                apply_operator(operators.pop())
            operators.append(token)
        else:
            raise ValueError(f"Unknown token: {token}")

    while operators:
        apply_operator(operators.pop())

    return output[0]

def build_sympy_expr(expr_str, symbols_dict):
    expr_str = replace_logical_symbols(expr_str)
    tokens = tokenize(expr_str)
    expr = parse_tokens(tokens, symbols_dict)
    return expr

def parse_input(argument_str):
    symbols_dict = {symbol: symbols(symbol) for symbol in 'A B C D E F G H I J K L M N O P Q R S T U V W X Y Z'.split()}
    
    parts = argument_str.split('therefore')
    premises_str = parts[0].strip().split(',')
    conclusion_str = parts[1].strip()

    premises = [build_sympy_expr(premise.strip(), symbols_dict) for premise in premises_str]
    conclusion = build_sympy_expr(conclusion_str, symbols_dict)
    
    return premises + [conclusion]

def generate_truth_table(expressions):
    symbols = sorted(set.union(*[expr.free_symbols for expr in expressions]), key=str)
    truth_values = list(sp.utilities.iterables.product([True, False], repeat=len(symbols)))

    table = []
    for values in truth_values:
        valuation = dict(zip(symbols, values))
        row = [1 if valuation[sym] else 0 for sym in symbols] + [1 if expr.subs(valuation) else 0 for expr in expressions]
        table.append(row)

    return table, symbols

def is_valid_argument(expressions):
    premises = expressions[:-1]
    conclusion = expressions[-1]

    symbols = sorted(set.union(*[expr.free_symbols for expr in expressions]), key=str)
    truth_values = list(sp.utilities.iterables.product([True, False], repeat=len(symbols)))

    for values in truth_values:
        valuation = dict(zip(symbols, values))
        if all(premise.subs(valuation) for premise in premises) and not conclusion.subs(valuation):
            counter_example = {str(sym): 1 if val else 0 for sym, val in valuation.items()}
            return False, counter_example

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
