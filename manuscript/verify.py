import itertools
import json
from itertools import permutations, product
from math import comb, factorial
from fractions import Fraction
from pathlib import Path


def matrix(dimension):
    return [[column + dimension * (row - 1) if row % 2 else
             dimension * row - column + 1
             for column in range(1, dimension + 1)]
            for row in range(1, dimension + 1)]


def multiply(left, right):
    columns = list(zip(*right))
    return [[sum(first * second for first, second in zip(row, column))
             for column in columns] for row in left]


def identity(dimension):
    return [[int(row == column) for column in range(dimension)]
            for row in range(dimension)]


def trace(square):
    return sum(square[index][index] for index in range(len(square)))


def antidiagonal_product(dimension):
    value=1
    for index in range(1,dimension+1):
        value*=((dimension-1)*index+1 if index % 2 else (dimension+1)*index-dimension)
    return value


def characteristic(square):
    dimension = len(square)
    power = identity(dimension)
    power_traces = [dimension]
    coefficients = [1]
    for degree in range(1, dimension + 1):
        power = multiply(power, square)
        power_traces.append(trace(power))
        numerator = -sum(coefficients[degree - index] * power_traces[index]
                         for index in range(1, degree + 1))
        assert numerator % degree == 0
        coefficients.append(numerator // degree)
    return coefficients


def determinant(square):
    dimension = len(square)
    if dimension == 0:
        return 1
    working = [list(map(Fraction, row)) for row in square]
    result = Fraction(1)
    for column in range(dimension):
        pivot = next((row for row in range(column, dimension)
                      if working[row][column]), None)
        if pivot is None:
            return 0
        if pivot != column:
            working[pivot], working[column] = working[column], working[pivot]
            result = -result
        diagonal = working[column][column]
        result *= diagonal
        for row in range(column + 1, dimension):
            multiplier = working[row][column] / diagonal
            for remaining in range(column, dimension):
                working[row][remaining] -= multiplier * working[column][remaining]
    assert result.denominator == 1
    return result.numerator


def constants(dimension):
    parity = dimension % 2
    first = Fraction(dimension * (dimension**2 + parity), 2)
    second = Fraction(dimension**2 * (3 * (1 + dimension**2)
                      - 2 * (2 + dimension**2) * parity), 12)
    assert first.denominator == second.denominator == 1
    return int(first), int(second)


def diagonal_formula(dimension, offset, upper):
    if upper:
        length = dimension - offset
        return Fraction(dimension * (length**2 + length % 2), 2)
    return Fraction(dimension * (dimension**2 - offset**2
                    + dimension % 2 + offset % 2) - 2 * offset * (dimension % 2), 2)


def product_coefficients(factors):
    coefficients = [Fraction(1)]
    for constant, linear in factors:
        updated = [Fraction(0)] * (len(coefficients) + 1)
        for degree, coefficient in enumerate(coefficients):
            updated[degree] += constant * coefficient
            updated[degree + 1] += linear * coefficient
        coefficients = updated
    return coefficients


def exponential_coefficient(polynomial, degree, sign=1):
    return sum(Fraction(coefficient * sign**(degree - power), factorial(degree - power))
               for power, coefficient in enumerate(polynomial) if degree >= power)


def ordinary_coefficient(numerator, degree, step=1, order=5):
    return sum(coefficient * comb((degree - power) // step + order - 1, order - 1)
               for power, coefficient in enumerate(numerator)
               if degree >= power and (degree - power) % step == 0)


def sibling_checks():
    permanent_cases = 0
    for dimension in range(9):
        square = matrix(dimension)
        row_coefficients = product_coefficients([
            (Fraction(2 * dimension * row - dimension + 1, 2), (-1)**(row - 1))
            for row in range(1, dimension + 1)])
        column_coefficients = product_coefficients([
            (1, Fraction(2 * column - dimension - 1, 2))
            for column in range(1, dimension + 1)])
        formula = sum(factorial(degree) * factorial(dimension - degree)
                      * row_coefficients[degree] * column_coefficients[degree]
                      for degree in range(dimension + 1))
        direct = 0
        for permutation in permutations(range(dimension)):
            term = 1
            for row, column in enumerate(permutation):
                term *= square[row][column]
            direct += term
        assert formula == direct, ('permanent', dimension)
        permanent_cases += 1
    spectral_cases = 0
    for dimension in range(2, 25, 2):
        positive = dimension * (dimension**2 + 1) // 2
        negative = -dimension // 2
        assert characteristic(matrix(dimension)) == [
            1, -positive-negative, positive*negative] + [0]*(dimension-2)
        spectral_cases += 1
    for dimension in range(2, 13, 2):
        for step in range(1, 9):
            square = [[column + step*(row-1) if row % 2 else step*row-column+1
                       for column in range(1, dimension+1)]
                      for row in range(1, dimension+1)]
            positive = dimension*(step*dimension+1)//2
            negative = -dimension//2
            assert characteristic(square) == [
                1, -positive-negative, positive*negative]+[0]*(dimension-2)
            spectral_cases += 1
    printed = [[1,2,3,4],[6,5,4,3],[7,8,9,10],[12,11,10,9]]
    assert characteristic(printed) == [1,-24,-52,0,0]
    orientation_cases = 0
    for dimension in range(2,9):
        for signs in product([-1,1],repeat=dimension):
            square=[[column+dimension*(row-1) if signs[row-1]==1
                     else dimension*row-column+1
                     for column in range(1,dimension+1)]
                    for row in range(1,dimension+1)]
            total_sign=sum(signs)
            mixed=sum(sign*Fraction(2*row-dimension-1,2)
                      for row,sign in enumerate(signs,1))
            first=Fraction(dimension*(dimension**2+1),2)
            second=Fraction(dimension**2*(dimension**2-1),12)
            assert characteristic(square)==[1,-first-mixed,first*mixed-total_sign*second]+[0]*(dimension-2)
            orientation_cases += 1
    full_numerator = [0,0,5,6,43,20,43,6,5]
    even_numerator = [0,5,43,43,5]
    odd_numerator = [0,6,20,6]
    generating_cases = 0
    for degree in range(41):
        actual = constants(degree)[1]
        assert ordinary_coefficient(full_numerator, degree, 2) == actual
        exponential = (exponential_coefficient([0,3,15,12,2],degree)
                       + exponential_coefficient([0,-3,9,-6,1],degree,-1))/12
        assert exponential == Fraction(actual,factorial(degree))
        shifted = (exponential_coefficient([36,-33,15,-4,2],degree+2)
                   + exponential_coefficient([24,21,9,2,1],degree+2,-1))/12
        assert shifted == Fraction(actual,factorial(degree+2))
        even = constants(2*degree)[1]
        odd = constants(2*degree+1)[1]
        assert ordinary_coefficient(even_numerator,degree) == even
        assert ordinary_coefficient(odd_numerator,degree) == odd
        assert even == 4*degree**4+degree**2
        assert odd == Fraction(4*degree**4+8*degree**3+5*degree**2+degree,3)
        factorial_inverse = lambda index: Fraction(1,factorial(index)) if index >= 0 else Fraction(0)
        displayed_odd = (6*factorial_inverse(2*degree-2)
                         +6*factorial_inverse(2*degree-1)
                         +factorial_inverse(2*degree-3))/12
        displayed_even = (8*factorial_inverse(2*degree-2)
                          +factorial_inverse(2*degree-4)
                          +2*factorial_inverse(2*degree-1)
                          +6*factorial_inverse(2*degree-3))/4
        assert displayed_odd == Fraction(odd,factorial(2*degree+1))
        assert displayed_even == Fraction(even,factorial(2*degree))
        generating_cases += 7
    for index in range(5,101):
        for parity in [0,1]:
            values=[constants(2*(index-offset)+parity)[1] for offset in range(6)]
            assert values[0] == sum(coefficient*value for coefficient,value in
                                    zip([5,-10,10,-5,1],values[1:]))
    rows = [[1],[2,3]]
    for row_index in range(2,101):
        previous=rows[-1]
        beginning = ([previous[-1]+2,previous[-2]+2] if row_index % 2 == 0
                     else [previous[0]+1,previous[-1]+2])
        for column in range(2,row_index+1):
            beginning.append(beginning[column-2]+2)
        rows.append(beginning)
    for row_index,row in enumerate(rows):
        half=row_index//2 if row_index % 2 == 0 else (row_index+1)//2
        expected=(4*half**3+6*half**2+5*half+1 if row_index % 2 == 0
                  else 4*half**3+half)
        assert sum(row)==expected,('triangle',row_index)
        if row_index % 2 == 0:
            assert sum(value % 2 == 0 for value in row) == half
            assert sum(value % 2 == 1 for value in row) == half + 1
        else:
            assert sum(value % 2 == 0 for value in row) == half
            assert sum(value % 2 == 1 for value in row) == half
        assert sum(row)==Fraction(2*row_index**3+6*row_index**2+9*row_index+4
                                  +row_index*(-1)**row_index,4)
        generating = sum(coefficient*sum((-1)**negative*(negative+1)
                         *comb(row_index-power-negative+3,3)
                         for negative in range(row_index-power+1))
                         for power,coefficient in enumerate([1,3,5,1,2]) if row_index>=power)
        assert sum(row)==generating
        exponential=(exponential_coefficient([4,17,12,2],row_index)
                     -exponential_coefficient([0,1],row_index,-1))/4
        assert exponential==Fraction(sum(row),factorial(row_index))
        if row_index>=6:
            assert sum(row)==sum(coefficient*sum(rows[row_index-offset])
                                for offset,coefficient in enumerate([2,1,-4,1,2,-1],1))
    flattened = [value for row in rows for value in row]
    assert len(flattened) == len(set(flattened))
    last_half = (len(rows) - 1) // 2
    assert sorted(value for value in flattened if value % 2 == 0) == list(
        range(2, 2 * last_half**2 + 2 * last_half + 1, 2))
    assert sorted(value for value in flattened if value % 2 == 1) == list(
        range(1, 2 * last_half**2 + 4 * last_half + 2, 2))
    paired_interval_cases = 0
    for half in range(1, 51):
        paired = rows[2 * half - 1] + rows[2 * half]
        assert sorted(value for value in paired if value % 2 == 0) == list(
            range(2 * half**2 - 2 * half + 2, 2 * half**2 + 2 * half + 1, 2))
        assert sorted(value for value in paired if value % 2 == 1) == list(
            range(2 * half**2 + 1, 2 * half**2 + 4 * half + 2, 2))
        paired_interval_cases += 1
    offdiagonal_cases = 0
    for dimension in range(2, 101):
        square = matrix(dimension)
        lower = sum(square[row][row - 1] for row in range(1, dimension))
        upper = sum(square[row][row + 1] for row in range(dimension - 1))
        half = dimension // 2
        expected_lower = (4 * half**3 if dimension % 2 == 0 else
                          2 * half * (2 * half**2 + 3 * half + 2))
        expected_upper = (2 * half * (2 * half**2 - 2 * half + 1)
                          if dimension % 2 == 0 else 2 * half**2 * (2 * half + 1))
        assert lower == expected_lower and upper == expected_upper
        assert lower % 2 == upper % 2 == 0 and upper % 10 != 4
        offdiagonal_cases += 1
    even_residues = [(2 * half * (2 * half**2 - 2 * half + 1)) % 10 for half in range(5)]
    odd_residues = [(2 * half**2 * (2 * half + 1)) % 10 for half in range(5)]
    assert even_residues == [0, 2, 0, 8, 0]
    assert odd_residues == [0, 6, 0, 6, 8]
    for index in range(2,52):
        half=index-1
        assert sum(rows[2*index-3])==half*(4*half**2+1)
    for index in range(1,101):
        half=index-1
        value=half*(4*half**2+1)
        length=2*index-1
        assert value==Fraction((2*half+1)**4-(2*half-1)**4,16)
        assert value==(3*comb(length,3) if length>=3 else 0)+2*half
        assert value+1==length*(1+(comb(length-1,2) if length>=3 else 0))
        assert ordinary_coefficient([0,0,5,14,5],index,order=4)==value
        assert exponential_coefficient([0,5,12,4],half)==Fraction(value,factorial(half))
    for index in range(1,101):
        even=constants(2*index)[1]
        odd=constants(2*index+1)[1]
        assert Fraction(1,even)==Fraction(1,index**2)-Fraction(4,4*index**2+1)
        dimension=2*index+1
        assert Fraction(1,odd)==12*(Fraction(1,dimension**2-1)-Fraction(1,dimension**2))
    for dimension in range(101):
        square=matrix(dimension)
        direct=1
        for index in range(dimension):
            direct*=square[index][dimension-index-1]
        assert direct==antidiagonal_product(dimension)
        assert (direct % 10 == 0)==(dimension % 2 == 0 and dimension not in [0,2,6])
    return {'permanent_direct_permutation_cases':permanent_cases,
            'arbitrary_orientation_characteristic_cases':orientation_cases,
            'even_and_variable_row_step_characteristic_cases':spectral_cases,
            'printed_A317297_n3_characteristic':[1,-24,-52,0,0],
            'generating_function_exact_coefficients':generating_cases,
            'parity_recurrence_cases':192,'A246697_rows':101,
            'A246697_GF_coefficients':202,'A246697_recurrence_cases':95,
            'A246696_parity_rows':len(rows),
            'A246696_permutation_prefix_entries':len(flattened),
            'A246696_paired_interval_cases':paired_interval_cases,
            'first_offdiagonal_parity_and_terminal_digit_cases':offdiagonal_cases,
            'first_upper_offdiagonal_residues_even':even_residues,
            'first_upper_offdiagonal_residues_odd':odd_residues,
            'A317297_polynomial_and_GF_cases':100,
            'antidiagonal_product_and_trailing_zero_cases':101,
            'A317297_bisection_cases':50,'reciprocal_partial_fraction_cases':200,
            'ordinary_EGF_x2':str(Fraction(5,2)),
            'displayed_shifted_function_x2':str(Fraction(5,24))}


def run():
    characteristic_cases = 0
    exterior_cases = 0
    principal_minors = 0
    power_cases = 0
    diagonal_cases = 0
    for dimension in range(25):
        square = matrix(dimension)
        first, second = constants(dimension)
        expected = ([1] if dimension == 0 else [1, -1] if dimension == 1
                    else [1, -first, -second] + [0] * (dimension - 2))
        assert characteristic(square) == expected, ('characteristic', dimension)
        characteristic_cases += 1
        if dimension >= 2:
            power = identity(dimension)
            expected_previous, expected_current = 2, first
            for exponent in range(1, 9):
                power = multiply(power, square)
                assert trace(power) == expected_current, ('power', dimension, exponent)
                expected_previous, expected_current = (
                    expected_current, first * expected_current + second * expected_previous)
                power_cases += 1
        if dimension <= 8:
            for order in range(dimension + 3):
                actual = 0
                for indices in itertools.combinations(range(dimension), order):
                    minor = [[square[row][column] for column in indices] for row in indices]
                    actual += determinant(minor)
                    principal_minors += 1
                expected_trace = 1 if order == 0 else first if order == 1 else -second if order == 2 else 0
                assert actual == expected_trace, ('exterior', dimension, order)
                exterior_cases += 1
    for dimension in range(1, 101):
        square = matrix(dimension)
        first, second = constants(dimension)
        direct_second = sum(square[row][row] * square[column][column]
                            - square[row][column] * square[column][row]
                            for row in range(dimension) for column in range(row + 1, dimension))
        assert direct_second == -second
        assert trace(square) == first
        assert sum(map(sum, square)) == dimension**2 * (dimension**2 + 1) // 2
        centered_absolute=sum(abs(Fraction(2*index-dimension-1,2))
                              for index in range(1,dimension+1))
        assert dimension**3-2*dimension*centered_absolute==first
        for row in range(1, dimension + 1):
            assert sum(square[row - 1]) == dimension**2 * row - dimension * (dimension - 1) // 2
            sign = 1 if row % 2 else -1
            for column in range(1, dimension + 1):
                assert 2 * square[row - 1][column - 1] == (
                    2 * dimension * row - dimension + 1 + sign * (2 * column - dimension - 1))
            assert square[row - 1][dimension - row] == (
                (dimension - 1) * row + 1 if row % 2 else (dimension + 1) * row - dimension)
        for column in range(1, dimension + 1):
            expected_column = Fraction(dimension * (dimension**2 + 1), 2)
            expected_column += (dimension % 2) * Fraction(2 * column - dimension - 1, 2)
            assert sum(square[row][column - 1] for row in range(dimension)) == expected_column
        for offset in range(dimension):
            upper = sum(square[row][row + offset] for row in range(dimension - offset))
            lower = sum(square[row + offset][row] for row in range(dimension - offset))
            assert upper == diagonal_formula(dimension, offset, True)
            assert lower == diagonal_formula(dimension, offset, False)
            diagonal_cases += 2
    references = json.loads((Path(__file__).parent / 'reference-values.json').read_text())
    source_comparisons = 0
    for entry in references['sequences']:
        identifier = entry['id']
        offset = entry['offset']
        for index, expected in enumerate(entry['values'], offset):
            if identifier == 'A322844':
                actual = constants(index)[1]
            elif identifier == 'A317614':
                actual = trace(matrix(index))
            elif identifier == 'A130130':
                actual = min(index, 2)
            elif identifier == 'A037270':
                actual = sum(map(sum, matrix(index)))
            elif identifier == 'A002415':
                actual = index**2 * (index**2 - 1) // 12
            elif identifier == 'A317297':
                actual = (index-1)*(4*(index-1)**2+1)
            elif identifier == 'A246697':
                actual = Fraction(2*index**3+6*index**2+9*index+4+index*(-1)**index,4)
            elif identifier == 'A382597':
                actual = antidiagonal_product(index)
            elif identifier in ['A323723', 'A323724']:
                square = matrix(index)
                actual = (sum(square[row + 1][row] for row in range(index - 1))
                          if identifier == 'A323723' else
                          sum(square[row][row + 1] for row in range(index - 1)))
            else:
                continue
            assert actual == expected, ('source prefix', identifier, index)
            source_comparisons += 1
    for entry in references['triangles']:
        actual = []
        for dimension in range(1, entry['rows'] + 1):
            square = matrix(dimension)
            if entry['id'] == 'A241016':
                actual.extend(map(sum, square))
            elif entry['id'] == 'A317617':
                actual.extend(map(sum, zip(*square)))
            elif entry['id'] in ['A325516', 'A325655']:
                upper = entry['id'] == 'A325516'
                actual.extend(int(diagonal_formula(dimension, offset, upper))
                              for offset in range(dimension))
        assert actual == entry['values'], ('source triangle', entry['id'])
        source_comparisons += len(actual)
    antidiagonal = [matrix(4)[index][3 - index] for index in range(4)]
    assert antidiagonal == [4, 6, 10, 16]
    assert references['antidiagonal_comparison']['A074147_row_4'] == [6, 8, 10, 12]
    assert antidiagonal != references['antidiagonal_comparison']['A074147_row_4']
    return {'status': 'pass', 'arithmetic': 'exact integers and rational numbers',
            'sibling_checks': sibling_checks(),
            'characteristic_polynomials': {'n_min': 0, 'n_max': 24, 'cases': characteristic_cases},
            'principal_minor_exterior_traces': {'n_min': 0, 'n_max': 8,
                'orders': '0 through n+2', 'cases': exterior_cases, 'principal_minors': principal_minors},
            'power_traces': {'n_min': 2, 'n_max': 24, 'exponent_min': 1, 'exponent_max': 8, 'cases': power_cases},
            'entry_factorization_and_linear_sums': {'n_min': 1, 'n_max': 100},
            'signed_second_exterior_trace': {'n_min': 1, 'n_max': 100},
            'diagonal_sums': {'n_min': 1, 'n_max': 100, 'cases': diagonal_cases},
            'OEIS_value_comparisons': source_comparisons,
            'fixed_size_antidiagonal_n4': antidiagonal,
            'A074147_row_4': references['antidiagonal_comparison']['A074147_row_4']}


if __name__ == '__main__':
    print(json.dumps(run(), indent=2, sort_keys=True))
