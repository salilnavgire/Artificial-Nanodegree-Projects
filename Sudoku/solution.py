import re

assignments = []
rows = 'ABCDEFGHI'
cols = '123456789'


def cross(a, b):
    '''Cross product of elements in A and elements in B.
    '''
    return [s + t for s in a for t in b]


boxes = cross(rows, cols)
row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC', 'DEF', 'GHI') for cs in
                ('123', '456', '789')]
diagonal_units = [[''.join(foo) for foo in zip(res, cols)] for res in
                  [rows, rows[::-1]]]
unitlist = row_units + column_units + square_units + diagonal_units
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s], [])) - set([s])) for s in boxes)


def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """

    # Don't waste memory appending actions that don't actually change any
    # values

    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values


def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """

    # We go through all units and check if there are any naked twins with
    # length 2. If we catch a naked twin we go ahead and eliminate those 2
    # digits from all its peers.

    for res in unitlist:
        l = [values[val] for val in res]
        dupes = [x for n, x in enumerate(l) if x in l[:n]]
        if dupes:
            for dup in dupes:
                if len(dup) == 2:
                    for x in res:
                        if values[x] == dup:
                            pass
                        else:
                            values[x] = re.sub('|'.join(list(dup)), '',
                                               values[x])
    return values


def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value,
            then the value will be '123456789'.
    """
    chars = []
    digits = '123456789'
    for c in grid:
        if c in digits:
            chars.append(c)
        if c == '.':
            chars.append(digits)
    assert len(chars) == 81
    return dict(zip(boxes, chars))


def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1 + max(len(values[s]) for s in boxes)
    line = '+'.join(['-' * (width * 3)] * 3)
    for r in rows:
        print(''.join(values[r + c].center(width) + ('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF':
            print(line)
    return


def eliminate(values):
    """
    Go through all the boxes, and whenever there is a box with a value,
    eliminate this value from the values of all its peers.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    for box in solved_values:
        digit = values[box]
        for peer in peers[box]:
            values[peer] = values[peer].replace(digit, '')
    return values


def only_choice(values):
    """
    Go through all the units, and whenever there is a unit with a value that
    only fits in one box, assign the value to this box.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    for unit in unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                values[dplaces[0]] = digit
    return values


def reduce_puzzle(values):
    """
    Iterate eliminate() and only_choice(). If at some point, there is a box
    with no available values, return False.

    If the sudoku is solved, return the sudoku.

    If after an iteration of both functions, the sudoku remains the same,
    return the sudoku.

    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if
                                    len(values[box]) == 1])
        # Your code here: Use the Eliminate Strategy
        values = eliminate(values)
        # Use the Naked Twins Strategy
        values = naked_twins(values)
        # Your code here: Use the Only Choice Strategy
        values = only_choice(values)
        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if
                                   len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero
        # available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values


def search(values):
    # Using depth-first search and propagation, create a search tree and solve
    # the sudoku.
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)
    if values:
        if len([res for res in values if
                len(values[res]) == 1]) == len(values):
            return values
        else:
            m = [len(values[res]) for res in values if len(values[res]) > 1]
            if m:
                # Choose one of the unfilled squares with the fewest
                # possibilities
                minx = [res for res in values if len(values[res]) == min(m)][0]

                # Now use recursion to solve each one of the resulting sudokus,
                # and if one returns a value (not False), return that answer!
                for res in list(values[minx]):
                    vals = values.copy()
                    vals[minx] = str(res)
                    vals = search(vals)
                    if vals:
                        return vals
            else:
                return False
    else:
        return False


def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...
                        4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if
        no solution exists.
    """
    values = grid_values(grid)
    values = reduce_puzzle(values)
    if values:
        if len([res for res in values if
                len(values[res]) == 1]) == len(values):
            return values
        else:
            m = [len(values[res]) for res in values if len(values[res]) > 1]
            if m:
                # Choose one of the unfilled squares with the fewest
                # possibilities
                minx = [res for res in values if len(values[res]) == min(m)][0]

                # Now use recursion to solve each one of the resulting sudokus,
                # and if one returns a value (not False), return that answer!
                for res in list(values[minx]):
                    vals = values.copy()
                    vals[minx] = str(res)
                    vals = search(vals)
                    if vals:
                        return vals
            else:
                return False
    else:
        return False


if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue.'
              'Not a problem! It is not a requirement.')
