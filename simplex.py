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

    # Append 0 if the equation was the objetive function
    if is_objective_function:
        terms.append("0")

    return terms


def convert_term_to_integer(term: str) -> int:
    # For positive x and y (1)
    if "x" in term:
        term = term.replace("x", "1")
    elif "y" in term:
        term = term.replace("y", "1")

    # For negative x and y (-1)
    if "-x" in term:
        term = term.replace("-x", "-1")
    elif "-y" in term:
        term = term.replace("-y", "-1")

    return int(term)


def get_objective_function():
    return input("Enter objective function: ")


def get_constraints():
    constraints = []
    constraints_number = int(input("Enter the number of constraints (excluding non-negativity constraints): "))

    for i in range(constraints_number):
        constraints.append(input(f"Enter constraint {i + 1}: "))

    return constraints

# TODO: allow both maximize and minimize
def formulate_LP_model(objective_function: str, constraints: list):
    print(f"Max {objective_function}")
    print("subject to the constraints")
    for constraint in constraints:
        print(f"  {constraint}")
    print("  x, y >= 0\n")


def print_table(matrix):
    table = PrettyTable()
    matrix_labeled = add_labels(matrix)

    # Set up table
    table.field_names = matrix_labeled[0]
    for i, row in enumerate(matrix_labeled):
        if i == 0: # The first row are the field names, skip it
            continue

        table.add_row(row)

    print(table)


# Add the first row identifying what column, and the first row indexes identifying what basic variable
# For the prettytable function
def add_labels(matrix) -> list:
    matrix_labeled = copy.deepcopy(matrix)
    constraints_num = len(matrix) - 1 # Get number of constraints by getting length - 1 (z)

    # Build first row
    first_row = ["B.V", "x", "y"]
    for i in range(constraints_num):
        first_row.append(f"S{i+1}")
    else:
        first_row.append("RHS")

    # Add corresponding basic variable in each column
    # TODO: Use global boolean variables to check whether the x or y column is solved, update accordingly in the table if so
    n = 1
    for i, row in enumerate(matrix_labeled):
        if i == len(matrix_labeled) - 1: # If last row, it's the objective function
            row.insert(0, "z")
        else:
            row.insert(0, f"S{n}")
            n += 1

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
            row[0] = -convert_term_to_integer(objective_function_terms[0])
            row[1] = -convert_term_to_integer(objective_function_terms[1])

            # Fill RHS column
            row[columns - 1] = convert_term_to_integer(objective_function_terms[2])

        else:
            # Fill x and y columns
            row[0] = convert_term_to_integer(constraints_terms[i][0])
            row[1] = convert_term_to_integer(constraints_terms[i][1])

            # Fill the slack variable columns
            # TODO: Add an explanation, because I'm pretty sure I wouldn't understand this shit as well in a few months
            for j in range(rows):
                if i == j:
                    row[j + 2] = 1
                    break

            # Fill RHS column
            row[columns - 1] = convert_term_to_integer(constraints_terms[i][2])

    return matrix

# Returns true if a negative value exists in the objective row (last row),
# otherwise the indicated solution is already optimal and returns false
def objective_row_negative_exists(matrix) -> bool:
    for n in matrix[len(matrix) - 1]:
        if n < 0:
            return True

    return False


# Returns true if a positive value exists in the pivotal column (except for the objective row),
# otherwise there is no finite optimal solution and returns false
def pivot_column_positive_exists(matrix, pivot_column_index) -> bool:
    for i in range(len(matrix)):
        if matrix[i][pivot_column_index] > 0:
            return True

    return False


# Finds the smallest negative number in the objective row (if a negative value exists) and returns its index
def determine_pivot_column(matrix) -> int:
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
        ratio_result = matrix[i][right_hand_side_index] / matrix[i][pivot_column_index]
        if ratio_result < smallest:
            smallest = ratio_result
            smallest_index = i

    return smallest_index


# Get the pivot using the pivot row and pivot column
def get_pivot(matrix: list, row_index: int, column_index: int) -> int:
    return matrix[row_index][column_index]


# Perform pivot elimination given the pivotal row and column
def perform_pivot_elimination(matrix: list, pivot_row_index: int, pivot_column_index: int):
    new_matrix = copy.deepcopy(matrix)
    pivot = new_matrix[pivot_row_index][pivot_column_index]

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
                new_matrix[row][i] = n * (fractions.Fraction(1, pivot))
        else:
            row_pivot = new_matrix[row][pivot_column_index]
            for i, n in enumerate(matrix[row]):
                pivot_row_num = new_matrix[pivot_row_index][i]
                new_matrix[row][i] = n - (pivot_row_num * row_pivot)

    convert_fractions_to_integer(new_matrix)
    return new_matrix


# Converts fractions to integers if the resulting integer is a whole number (denominator is 1),
# otherwise keep it a fraction
def convert_fractions_to_integer(matrix: list) -> list[list[int]]:
    for row in matrix:
        for i, element in enumerate(row):
            if isinstance(element, fractions.Fraction):
                if element.denominator == 1:
                    row[i] = int(element)

    return matrix


def main():
    """
    # Let user input the objective function, how many constraints, and the constraints itself
    objective_function = get_objective_function()
    constraints = get_constraints()
    """

    """
    # Testing, has optimal solution (bounded)
    objective_function = "z = 120x + 100y"
    constraints = ["2x + 2y <= 8", "5x + 3y <= 15"]
    """

    # Testing, has no finite optimal solution (unbounded)
    objective_function = "z = x + y"
    constraints = ["x - y <= 2", "-x + y <= 1"]

    # Formulate the LP model
    print("\nLP Model:")
    formulate_LP_model(objective_function, constraints)

    # Separate the terms in each inequality/equation
    objective_function_terms = separate_terms(objective_function)
    constraints_terms = []
    for constraint in constraints:
        constraints_terms.append(separate_terms(constraint))

    # Print the terms for each equation/inequality
    print(f"The objective function has the terms: {objective_function_terms}")
    for i, constraint in enumerate(constraints_terms):
        print(f"Constraint {i + 1} has the terms: {constraint}")

    # Print the initial table
    print("\nInitial table:")
    matrix = initial_table(objective_function_terms, constraints_terms)
    print_table(matrix)

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
        matrix = perform_pivot_elimination(matrix, pivot_row_index, pivot_column_index)

        print(f"\nStep {step}:")
        print_table(matrix)
        step += 1


main()