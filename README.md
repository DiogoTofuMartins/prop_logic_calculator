# Proposition Logic Evaluator

Proposition Logic Evaluator is a web-based tool that allows users to construct logical propositions and evaluate their validity. The application takes logical statements, constructs a truth table, and determines the validity of logical arguments. It supports various logical operators such as implication, biconditional, conjunction, disjunction, negation, and exclusive or.

## Features

- Input multiple logical propositions and a conclusion.
- Supports logical operators: implication (=>), biconditional (<=>), conjunction (∧), disjunction (∨), negation (¬), and exclusive or (⊕).
- Constructs a truth table for the given propositions.
- Determines the validity of the logical argument based on the truth table.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

- Python 3.8 or later
- pip (Python package installer)

### Installing

1. **Clone the repository:**

    ```sh
    git clone git@github.com:DiogoTofuMartins/prop_logic_calculator.git
    cd prop-logic-evaluator
    ```

2. **Set up a virtual environment:**

    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install the required Python packages:**

    ```sh
    pip install -r requirements.txt
    ```

4. **Run the Flask application:**

    ```sh
    flask run
    ```

    The Flask application should now be running on `http://127.0.0.1:5000/`.

5. **Serve the HTML file:**

    Open `index.html` in a web browser or use a simple HTTP server:

    ```sh
    python -m http.server
    ```

    The frontend should now be accessible, and it will be running on `http://127.0.0.1:8000/`.

## Deployment

### Deploying to AWS Lambda using Zappa

1. **Install Zappa:**

    ```sh
    pip install zappa
    ```

2. **Initialize Zappa:**

    ```sh
    zappa init
    ```

    Follow the prompts to configure Zappa for deployment.

3. **Deploy the application:**

    ```sh
    zappa deploy dev
    ```

    Zappa will package your application and deploy it to AWS Lambda and API Gateway. Note the API Gateway URL provided after deployment.

4. **Update `index.html` to use the API Gateway URL:**

    Edit the `fetch` call in `index.html` to use the API Gateway URL provided by Zappa.

### Example `index.html` fetch call:

```javascript
fetch('YOUR_API_GATEWAY_URL/evaluate', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({ argument }),
})
.then(response => response.json())
.then(data => {
    const resultDiv = document.getElementById('result');
    resultDiv.innerHTML = `<p>${data.message}</p>`;
    if (data.truthTable) {
        const tableHtml = generateTableHtml(data.truthTable);
        resultDiv.innerHTML += tableHtml;
    }
})
.catch(error => console.error('Error:', error));
```

## Usage

### Input Propositions:
1. **Enter Propositions**: Enter the logical propositions in the input boxes.
2. **Select Operators**: Select the appropriate logical operator from the dropdown.
3. **Add More Propositions**: Click the `+` button to add more propositions.

### Input Conclusion:
1. **Enter Conclusion**: Enter the conclusion in the "Therefore" input box.

### Submit:
1. **Evaluate Argument**: Click the `Submit` button to evaluate the argument.

### Results:
1. **View Results**: The application will display the truth table and indicate whether the argument is valid or not.

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## Acknowledgments

- [SymPy](https://www.sympy.org/en/index.html) for symbolic mathematics in Python
- [Flask](https://flask.palletsprojects.com/en/2.0.x/) for the web framework
- [Zappa](https://github.com/zappa/Zappa) for serverless deployment
