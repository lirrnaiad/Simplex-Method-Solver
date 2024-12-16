# Simplex Method Solver

## Description
A Python-based Simplex Method Solver for linear programming problems. This tool allows users to input an objective function and constraints, and it solves the linear programming problem using the Simplex method.

## Features
- Input objective function and constraints
- Formulate and display the linear programming model
- Perform Simplex method iterations
- Display intermediate and final Simplex tables
- Handle fractions and floating-point numbers

## Requirements
- Python 3.x (Download it [here](https://www.python.org/downloads/))
- `prettytable` library

## Installation
1. **Clone the Repository**:
    ```sh
    git clone https://github.com/lirrnaiad/Simplex-Method-Solver.git
    cd Simplex-Method-Solver
    ```

2. **Create a Virtual Environment**:
    ```sh
    python -m venv venv
    ```

3. **Activate the Virtual Environment**:
    - On Windows:
        ```sh
        venv\Scripts\activate
        ```
    - On macOS/Linux:
        ```sh
        source venv/bin/activate
        ```

4. **Install Dependencies**:
    ```sh
    pip install -r requirements.txt
    ```

## Usage
1. **Run the Script**:
    ```sh
    python simplex.py
    ```

2. **Input the Objective Function**:
    ```
    Enter objective function: z = 120x + 100y
    ```

3. **Input the Number of Constraints**:
    ```
    Enter the number of constraints (excluding non-negativity constraints): 2
    ```

4. **Input Each Constraint**:
    ```
    Enter constraint 1: 2x + 2y <= 8
    Enter constraint 2: 5x + 3y <= 15
    ```

5. **View the Formulated LP Model**:
    ```
    LP Model:
    Max 120x + 100y
    subject to the constraints
      2x + 2y <= 8
      5x + 3y <= 15
      x, y >= 0
    ```

6. **View the Initial Simplex Table**:
    ```
    Initial table:
    +-----+-----+-----+-----+-----+-----+
    | B.V |  x  |  y  | S1  | S2  | RHS |
    +-----+-----+-----+-----+-----+-----+
    |  S1 |  2  |  2  |  1  |  0  |  8  |
    |  S2 |  5  |  3  |  0  |  1  | 15  |
    |  z  | -120| -100|  0  |  0  |  0  |
    +-----+-----+-----+-----+-----+-----+
    ```

7. **Follow the Simplex Method Iterations**:
    - The program will display each step of the Simplex method, showing the intermediate tables and the pivot operations.

8. **View the Final Simplex Table and Solution**:
    - The program will display the final Simplex table and the optimal solution for the given linear programming problem.

