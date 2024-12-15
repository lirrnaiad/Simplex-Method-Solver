import sys
import copy
import fractions

from prettytable import PrettyTable


def separate_terms(equation: str) -> list[str]:
    terms = []
    equation = equation.replace(" ", "")

    # Check if the equation is an objective function
    is_objective_function = False
    if "z" in equation:
        equation = equation.replace("z=", "")
        is_objective_function = True

    # Check if the equation is a constraint, convert the relational operator into an equal sign
    relational_operators = [">", "<", ">=", "<="]
    for relational_operator in relational_operators:
        if relational_operator in equation:
            equation = equation.replace(relational_operator, "=")

    # Iterate through the string until an operator is encountered, add it to the terms list and empty the string
    current_term = ""
    for i, ch in enumerate(equation):
        if ch == "+":
            if current_term:  # Append the current term if it's not empty
                terms.append(current_term)
            current_term = ""
        elif ch == "-":
            if current_term:  # Append the previous term before handling the negative sign
                terms.append(current_term)
            current_term = "-"  # Start the next term with the negative sign
        elif ch == "=":
            if current_term:  # Append the last term before the "="
                terms.append(current_term)
            current_term = ""
        else:
            current_term += ch

    # Append the final term
    if current_term:
        terms.append(current_term)

    # Append 0 if the equation was the objective function
    if is_objective_function:
        terms.append("0")

    return terms


def convert_term(term: str):
    # For positive x and y (1)
    if "x" in term or "y" in term:
        term = term.replace("x", "").replace("y", "")

    # For negative x and y (-1)
    if "-x" in term or "-y" in term:
        term = term.replace("-x", "-").replace("-y", "-")

    # Convert to 1 or -1 if the term was simply x or -x
    if term == "":
        term = "1"
    elif term == "-":
        term = "-1"

    if "." in term:     # Convert to float if there is a decimal point
        return float(term)
    elif "/" in term:
        # If the term is a fraction use the helper function convert_term_to_fraction()
        term = convert_term_to_fraction(term)
        return term
    else:
        return int(term)


# If the term is a fraction, this function will be used
def convert_term_to_fraction(term: str) -> fractions.Fraction:
    # Remove x or y first
    if "x" in term or "y" in term:
        term = term.replace("x", "").replace("y", "")

    numerator, denominator = term.split("/")

    numerator = int(numerator)
    denominator = int(denominator)
    return fractions.Fraction(numerator, denominator)


def get_objective_function() -> str:
    return input("Enter objective function: ")


def get_constraints() -> list:
    constraints = []
    constraints_number = int(input("Enter the number of constraints (excluding non-negativity constraints): "))

    for i in range(constraints_number):
        constraints.append(input(f"Enter constraint {i + 1}: "))

    return constraints


def formulate_LP_model(objective_function: str, constraints: list[str]) -> None:
    print(f"Max {objective_function}")
    print("subject to the constraints")
    for constraint in constraints:
        print(f"  {constraint}")
    print("  x, y >= 0\n")


def print_table(matrix_labeled: list[list[int]]) -> None:
    table = PrettyTable()

    # Set up table
    table.field_names = matrix_labeled[0]
    for i, row in enumerate(matrix_labeled):
        if i == 0: # The first row are the field names, skip it
            continue

        table.add_row(row)

    print(table)


# Add the first row identifying what column, and the first row indexes identifying what basic variable
# For the prettytable function
def add_labels(matrix: list, basic_variables: list[str]) -> list:
    matrix_labeled = copy.deepcopy(matrix)
    constraints_num = len(matrix) - 1 # Get number of constraints by getting length - 1 (z)

    # Build first row
    first_row = ["B.V", "x", "y"]
    for i in range(constraints_num):
        first_row.append(f"S{i+1}")
    first_row.append("RHS")

    # Add corresponding basic variable in each column
    for i, row in enumerate(matrix_labeled):
        if i == len(matrix_labeled) - 1: # If last row, it's the objective function
            row.insert(0, "z")
        else:
            row.insert(0, basic_variables[i])

    # Insert the first row
    matrix_labeled.insert(0, first_row)

    return matrix_labeled


def initial_table(objective_function_terms: list, constraints_terms: list) -> list[list[int]]:
    # Set up number of columns and rows
    columns = len(constraints_terms) + 3    # number of constraints for the slack variables + x, y, and RHS (3)
    rows = len(constraints_terms) + 1       # number of constraints + 1 (the objective function)

    # Set up matrix
    matrix = [[0] * columns for i in range(rows)]
    for i, row in enumerate(matrix):
        # If last row, it's the objective function's row
        if i == len(matrix) - 1:
            # Fill x and y columns (they'll be the opposite sign)
            row[0] = -convert_term(objective_function_terms[0])
            row[1] = -convert_term(objective_function_terms[1])

            # Fill RHS column
            row[columns - 1] = convert_term(objective_function_terms[2])

        else:
            # Fill x and y columns
            row[0] = convert_term(constraints_terms[i][0])
            row[1] = convert_term(constraints_terms[i][1])

            # This loop iterates through the rows to add slack variables.
            # It sets the slack variable for the current constraint to 1.
            # The "j + 2" index is used to place the slack variable in the correct column.
            for j in range(rows):
                if i == j:
                    row[j + 2] = 1
                    break

            # Fill RHS column
            row[columns - 1] = convert_term(constraints_terms[i][2])

    return matrix

# Returns true if a negative value exists in the objective row (last row),
# otherwise the indicated solution is already optimal and returns false
def objective_row_negative_exists(matrix: list) -> bool:
    for n in matrix[len(matrix) - 1]:
        if n < 0:
            return True

    return False


# Returns true if a positive value exists in the pivotal column (except for the objective row),
# otherwise there is no finite optimal solution and returns false
def pivot_column_positive_exists(matrix: list, pivot_column_index: int) -> bool:
    for i in range(len(matrix)):
        if matrix[i][pivot_column_index] > 0:
            return True

    return False


# Finds the smallest negative number in the objective row (if a negative value exists) and returns its index
def determine_pivot_column(matrix: list) -> int:
    smallest = matrix[len(matrix) - 1][0]
    smallest_index = 0

    for i, n in enumerate(matrix[len(matrix) - 1]):
        if n < smallest:
            smallest = n
            smallest_index = i

    return smallest_index


# Finds the smallest ratio in the pivotal column and returns its index
def determine_pivot_row(matrix: list, pivot_column_index: int) -> int:
    right_hand_side_index = len(matrix[0]) - 1
    smallest = sys.maxsize
    smallest_index = 0

    # TODO: Allow support for more than 2 decision variables
    for i in range(2): # Loop until num of decision variables (at 2 for now)
        # Ignore 0 and negative numbers
        if matrix[i][pivot_column_index] <= 0:
            continue

        ratio_result = matrix[i][right_hand_side_index] / matrix[i][pivot_column_index]
        if ratio_result < smallest:
            smallest = ratio_result
            smallest_index = i

    return smallest_index


# Get the pivot using the pivot row and pivot column
def get_pivot(matrix: list, row_index: int, column_index: int) -> int:
    return matrix[row_index][column_index]


# Perform pivot elimination given the pivotal row and column
def perform_pivot_elimination(matrix: list, pivot_row_index: int, pivot_column_index: int, basic_variables: list) -> list[list[int]]:
    new_matrix = copy.deepcopy(matrix)
    pivot = new_matrix[pivot_row_index][pivot_column_index]

    # Check to see if pivot is a float to prevent errors with type handling
    pivot_is_float = False
    if isinstance(pivot, float):
        pivot_is_float = True

    # List to keep track of which order of rows to do pivot elimination
    order = []
    for i in range(len(new_matrix)):
        order.append(i)

    # Put the pivot row on first
    order.remove(pivot_row_index)
    order.insert(0, pivot_row_index)

    for row in order:
        # If it's the pivot row, multiply it by 1/k where k is the pivot
        if row == pivot_row_index:
            for i, n in enumerate(matrix[row]):
                if pivot_is_float:
                    new_matrix[row][i] = n * (fractions.Fraction(1, fractions.Fraction(pivot)))
                else:
                    new_matrix[row][i] = n * (fractions.Fraction(1, pivot))
        else:
            row_pivot = new_matrix[row][pivot_column_index]
            for i, n in enumerate(matrix[row]):
                pivot_row_num = new_matrix[pivot_row_index][i]
                new_matrix[row][i] = n - (pivot_row_num * row_pivot)


    # Convert the fractions and floats to int if they're essentially a whole number for better viewing
    convert_fractions_to_integer(new_matrix)
    convert_floats_to_integer(new_matrix)

    # Round decimals to two digits
    convert_floats_to_two_decimals(new_matrix)

    # Update the labels of the basic variables
    entering_variable = "x" if pivot_column_index == 0 else "y" if pivot_column_index == 1 else basic_variables[pivot_row_index]
    basic_variables[pivot_row_index] = entering_variable
    return new_matrix


# Converts fractions to integers if the resulting integer is a whole number (denominator is 1),
# otherwise keep it a fraction
def convert_fractions_to_integer(matrix: list) -> list:
    for row in matrix:
        for i, element in enumerate(row):
            if isinstance(element, fractions.Fraction):
                if element.denominator == 1:
                    row[i] = int(element)

    return matrix


# Rounds decimals to two digits for better viewing
def convert_floats_to_two_decimals(matrix: list):
    for row in matrix:
        for i, element in enumerate(row):
            if isinstance(element, float):
                row[i] = round(element, 2)


def convert_floats_to_integer(matrix: list):
    for row in matrix:
        for i, element in enumerate(row):
            if isinstance(element, float):
                if element.is_integer():
                    row[i] = int(element)


def main():
    print("SIMPLEX METHOD SOLVER")
    while True:
        # Let user input the objective function, how many constraints, and the constraints itself
        objective_function = get_objective_function()
        constraints = get_constraints()

        # Formulate the LP model
        print("\nLP Model:")
        formulate_LP_model(objective_function, constraints)

        # Separate the terms in each inequality/equation
        objective_function_terms = separate_terms(objective_function)
        constraints_terms = []
        for constraint in constraints:
            constraints_terms.append(separate_terms(constraint))

        # Initialize basic variables
        basic_variables = [f"S{i + 1}" for i in range(len(constraints))]

        # Print the initial table
        print("Initial table:")
        matrix = initial_table(objective_function_terms, constraints_terms)
        print_table(add_labels(matrix, basic_variables))

        step = 1
        while objective_row_negative_exists(matrix):
            # Stop when there are no more negative numbers on the objective function (x and y)
            pivot_column_index = determine_pivot_column(matrix)

            # Stop when there are no more positive numbers on the pivot column (there is no finite solution)
            if pivot_column_positive_exists(matrix, pivot_column_index):
                pivot_row_index = determine_pivot_row(matrix, pivot_column_index)
            else:
                print("\nThere is no finite optimal solution. Stopping.")
                print_table(matrix)
                break

            matrix = perform_pivot_elimination(matrix, pivot_row_index, pivot_column_index, basic_variables)

            print(f"\nStep {step}:")
            print_table(add_labels(matrix, basic_variables))
            step += 1

        # Ask if user wants to input a new problem
        choice = input("\nWould you like to continue? (y/n): ").lower()
        if choice == "y":
            print("Continuing!\n\n")
        elif choice == "n":
            break
        else:
            print("Invalid choice. Continuing anyway!\n\n")


main()