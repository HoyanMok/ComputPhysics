"""Matrix manipulation and system of linear equations"""
# for type hints
from typing import Any, Callable, Generic, List, Optional, TypeVar, Union, Tuple, overload
from numbers import Number
Idx = Union[int, Tuple[Union[int, slice], Union[int, slice]]]

from ._util import _flatten
from ._const import _EPS    # mechine error

Num = TypeVar("Num", bound=Number)

class Matrix(Generic[Num]):
    """Matrix class with shape (m, n) and elements of 2D list
    """
    def __init__(self, 
        elements: "Union[Matrix[Num], List[List[Num]], List[Num]]",
        shape: Union[int, Tuple[int, int], None] = None) -> None:   #TODO: create a better user interface for this
        """Generates a Matrix from elements and an optional shape.

        Args:
            elements (Union[Matrix, List[List[Num]], List[Num]]): 
                when elements is not a Matrix and shape is not None, the elements shall fit the shape.
            shape (Union[int, Tuple[int, int], None], optional): 
                The shape of the matrix. Defaults to None. 

        Raises:
            ValueError "The number of the elements cannot fit the shape of the matrix": 
                raised when elements is not a Matrix and it does not fit the shape.
            ValueError "The shape of a matrix shall be rectangular. ": 
                raised when shape is None and the elements is a list with sublists that have different lengths.
        """
        if isinstance(elements, Matrix):
            self.elements: List[List[Num]] = elements.elements
            self.shape: Tuple[int, int] = elements.shape
            return
        if shape is not None:
            try:    # check if shape is a tuple
                n, m = shape
            except TypeError:
                n: int = shape
                m = 1
            elements = _flatten(elements)
            if len(elements) != n * m:
                raise ValueError("The number of the elements cannot fit the shape of the matrix")
            self.elements = [elements[i*m:(i+1)*m] for i in range(n)]
        else:
            n = len(elements)
            try:
                m = len(elements[0])    # Check if elements if of type List[List[T]]
            except TypeError:
                self.shape = (1, n)
                self.elements: List[List[Num]] = [elements]
                return

            for row in elements:
                if len(row) != m:
                    raise ValueError("The shape of a matrix shall be rectangular. ")
            self.elements: List[List[Num]] = elements

        self.shape: Tuple[int, int] = (n, m)
        return

    @overload
    def __getitem__(self, idx: Tuple[int, int]) -> Num:
        ...
    def __getitem__(self, idx: Idx) -> "Matrix[Num]":
        if isinstance(idx, int): 
            return Matrix(self.elements[idx])
        
        i, j = idx
        
        if not isinstance(i, slice):
            if isinstance(j, slice):
                return Matrix(self.elements[i][j])
            else:
                return self.elements[i][j]
        else:
            if isinstance(j, slice):
                return Matrix([row[j] for row in self.elements[i]])
            else:
                return Matrix([[row[j]] for row in self.elements[i]])
    
    def __setitem__(self, idx: Idx, item: Num):
        try:
            i, j = idx
        except TypeError:
            self.elements[idx] = item
        
        if not isinstance(i, slice):
            self.elements[i][j] = item
        else:
            _, m = self.shape
            for k in range(0, m)[i]:
                self.elements[k][j] = item[k]

    def is_diag(self, error: float = _EPS) -> bool:
        """Check if a matrix is a diagonal square matrix

        Args:
            error (float, optional): Allowed error. Defaults to EPS i.e. the machine error.

        Returns:
            bool: if the matrix is square and diagonal, returns True, elsewise False.
        """
        n, m = self.shape
        if n != m:
            return False
        for i, j in zip(range(n), range(m)):
            if abs(self[i, j]) < error and i != j:
                return False
        else:
            return True

    def __float__(self) -> float:
        """Convert a $\lambda I_n$-like matrix to a floating number.

        Returns:
            float: the diagonal value $\lambda$.
        """
        n, m = self.shape
        if n == m:
            if self.is_diag():
                diag = self[0, 0]
                for i in range(n):
                    if self[i, i] != diag:
                        raise ValueError("Cannot convert a matrix that has different diagonal values into a float.")
                else:
                    return float(diag)
            else:
                raise ValueError("Cannot convert a non-diagonal matrix into a float.")
        else:
            raise ValueError("Cannot convert a non-square matrix into a float.")
    
    def __iter__(self):
        return iter(self.elements)

    @overload
    def __add__(self, B: Union["Matrix[Num]", Num]) -> "Matrix[Num]":
        ...
    def __add__(self, B: Union["Matrix[Number]", Number]) -> "Matrix[Number]":
        A = self
        n, m = self.shape
        if isinstance(B, Matrix):
            if self.shape != B.shape:
                raise ValueError("The shape of two matrices shall be the same.")
            C = []
            for i in range(n):
                C.append([A[i, j] + B[i, j] for j in range(m)])
        else:
            C = []
            for i in range(n):
                C.append([A[i, j] + B for j in range(m)])
        return Matrix(C)
    
    @overload
    def __radd__(self, B: Union["Matrix[Num]", Num]) -> "Matrix[Num]":
        ...
    def __radd__(self, B: Union["Matrix[Number]", Number]) -> "Matrix[Number]":
        return self + B
    
    @overload
    def __sub__(self, B: Union["Matrix[Num]", Num]) -> "Matrix[Num]":
        ...
    def __sub__(self, B: Union["Matrix[Number]", Number]) -> "Matrix[Number]":
        return self + (-1) * B

    @overload
    def __rsub__(self, B: Union["Matrix[Num]", Num]) -> "Matrix[Num]":
        ...
    def __rsub__(self, B: Union["Matrix[Number]", Number]) -> "Matrix[Number]":
        return B + (-1) * self

    def __repr__(self) -> str:
        return "({},{}) Matrix\n{}".format(*self.shape, str(self.elements))

    def __eq__(self, B: Any) -> bool:
        return isinstance(B, Matrix) and B.elements == self.elements

    def T(self) -> "Matrix[Num]":
        return Matrix([list(pair) for pair in zip(*self.elements)])

    @overload
    def __mul__(self, B: Union["Matrix[Num]", Num]) -> "Matrix[Num]":
        ...
    def __mul__(self, B: Union["Matrix[Number]", Number]) -> "Matrix[Number]":
        A = self
        nA, mA = self.shape
        if type(B) == Matrix:
            nB, mB = B.shape
            if mA != nB:
                raise ValueError("In order for A * B to make sense, the number of columns of A must be equal to the number of rows of B.")
            C = []
            for i in range(nA):
                C.append([sum(A[i, k] * B[k, j] for k in range(mA)) for j in range(mB)])
        else:
            C = [[A[i, j] * B for j in range(mA)] for i in range(nA)]
        return Matrix(C)

    @overload
    def __rmul__(self, B: Union["Matrix[Num]", Num]) -> "Matrix[Num]":
        ...
    def __rmul__(self, B: Union["Matrix[Number]", Number]) -> "Matrix[Number]":
        return self * B

    def __truediv__(self, b: Number) -> "Matrix[Number]":
        n, m = self.shape
        C = [[self[i, j] / b for j in range(m)] for i in range(n)]
        return Matrix(C)

    def det(self) -> float:
        n, m = self.shape
        if n != m:
            raise ValueError("Cannot compute the determinent for non-square matrix.")
        A = [row.copy() for row in self.elements] # Copy the matrix's elements
        for j in range(n - 1):
            for k in range(j, n): # find the first row that is not zero
                if A[k][j] != 0:
                    break
            else:
                return 0. # A matrix with a zero column has a 0 determinent
            if k != j:
                for l in range(j, n):
                    A[j][l] += A[k][l]
                
            for i in range(j + 1, n):
                k = A[i][j] / A[j][j]
                for l in range(j, n):
                    A[i][l] -= k * A[j][l]
        result = 1.
        for i in range(n):
            result *= A[i][i] 
        return result

    def tr(self) -> Num:
        n, m = self.shape
        if n != m:
            raise ValueError("Cannot compute the trace for non-square matrix.")
        trace = 0.
        for i in range(n):
            trace += self[i, i]
        return trace

    def triangularize(
        self, pos: str = "upper", 
        bounds: Optional[Tuple[int, int]] = None): 
    # TODO: reimplement triangularization about bounds, make changes outside the bounds
        if bounds is None:
            row_l, col_l = 0, 0
            row_u, col_u = self.shape
        else:
            row_l, col_l = bounds[0]
            row_u, col_u = bounds[1]
            n, m = self.shape
            if not (0 <= row_l < row_u <= n) or not (0 <= col_l < col_u <= m):
                raise ValueError ("Bounds out of range")

        A = self.elements
        if pos == "upper":
            j_range = range(row_l, row_u - 1)
            j_row = lambda j: j
            k_range_arg = lambda j: (j, row_u)
            i_range_arg = lambda j: (j + 1, row_u)
            l_range_arg = lambda j: (j, col_u)
        elif pos == "lower":
            j_range = range(col_u - 1, col_u - row_u, -1)
            j_row = lambda j: row_u + j - col_u
            k_range_arg = lambda j: (row_u + j - col_u, row_l - 1, -1)
            i_range_arg = lambda j: (row_u + j - col_u - 1, row_l - 1, -1)
            l_range_arg = lambda j: (col_l, j + 1)
        else:
            raise ValueError("'pos' must be 'upper' or 'lower'")

        for j in j_range:
            zero_column = False
            for k in range(*k_range_arg(j)): # find the first row that is not zero
                if A[k][j] != 0:
                    break
            else:
                zero_column = True
            if k != j_row(j):
                for l in range(*l_range_arg(j)):
                    A[j_row(j)][l] += A[k][l]
                
            if not zero_column:
                for i in range(*i_range_arg(j)):
                    K = A[i][j] / A[j_row(j)][j]
                    for l in range(*l_range_arg(j)):
                        A[i][l] -= K * A[j_row(j)][l]

    def is_inversible(self) -> bool:
        return self.det() != 0

    def T(self) -> "Matrix":
        return Matrix([list(row) for row in zip(*self.elements)])

    def inverse(self) -> "Matrix[Number]": 
        n, m = self.shape
        if n != m:
            raise ValueError ("Cannot compute inverse of a non-square matrix")
        I_n = eye(n)
        A = concatenate(self, I_n)
        A.triangularize()
        for j in range(n):
            eigenvalue = A[j, j]
            if eigenvalue == 0.:
                raise ValueError("The matrix is not inversible.")
            for l in range(j, 2*n):
                A[j, l] /= eigenvalue
            for i in range(j):
                K = A[i, j]
                for l in range(j, 2*n):
                    A[i, l] -= K * A[j, l]
        inversed: "Matrix" = A[:, n:]
        return inversed
    
    def __pow__(self, p: int) -> "Matrix[Number]":
        n, m = self.shape
        if n != m:
            raise ValueError ("Cannot compute power for non-square matrix")
        
        if p > 0:
            A = self
        else:
            A = self.inverse()
            p = -p
        result = eye(n)
        if p < 16:
            for _ in range(1, p+1):
                result *= A
        else:
            gen_bin = (int(i) for i in bin(p)[2:])
            A2i = A
            for bi in gen_bin:
                if bi == 1:
                    result *= A2i
                A2i **= 2 
        return result

    def copy(self) -> "Matrix[Num]":
        return Matrix([row.copy() for row in self.elements])

@overload
def concatenate(A: Matrix[Num], B: "Matrix[Num]", vertical: bool = False) -> "Matrix[Num]":
    ...
def concatenate(A: Matrix[Num], B: "Matrix[Number]", vertical: bool = False) -> "Matrix[Number]":
    n_A, m_A = A.shape
    n_B, m_B = A.shape
    if not vertical:
        if n_A != n_B:
            raise ValueError ("Cannot concatenate two matrices with different number of rows")
        A = A.elements
        B = B.elements
        C = [A[i] + B[i] for i in range(n_B)]
        return Matrix(C)
    else:
        if m_A != m_B:
            raise ValueError ("Cannot stack two matrices with different number of columns")
        A = A.elements
        B = B.elements
        C = A + B
        return Matrix(C)

def triangularize(A: Matrix[Num], pos: str = "upper", 
                  bounds: Union[Tuple[int, int], None] = None): 
    A = A.copy()
    A.triangularize(pos, bounds)
    return A
        
def eye(n: int) -> Matrix[float]:
    O_n = zeros(n, n)
    for i in range(n):
        O_n[i, i] = 1.
    I_n = O_n
    return I_n

def zeros(n: int, m: int = 1) -> Matrix[float]:
    O_n = [[0.] * m for _ in range(n)]
    return Matrix(O_n)

X = TypeVar("X")
Func = Callable[[X, Optional[Any]], X]

def matrixify(
    func: Func[Num], *args, **kwargs
    ) -> Func[Matrix[Num]]:
    def Mfunc(A):
        if isinstance(A, Matrix):
            n, m = A.shape
            A_func = [[func(A[i, j], *args, **kwargs) for j in range(m)] for i in range(n)]
            return Matrix(A_func)
        else:
            return func(A)
    return Mfunc

def solve_linear(A: Matrix[Num], b: Matrix[Number]) -> dict:
    """Solve a linear system with equations Ax = b, where A is a Matrix and b is a vector (i.e. (n, 1) Matrix).

    Args:
        A (Matrix): a (m, n) Matrix
        b (Matrix): a (m, 1) Matrix

    Raises:
        ValueError: raised when the shape of A and b cannot fit Ax = b

    Returns:
        sols (dict): a dict with keys "nonzero_sols_homo", "sol_inhomo" and "solable". 
            sol["solable"] (bool): 
                if the equations are solable.
            sol["sol_inhomo"] (Matrix): 
                a solution of the equations Ax = b. If not solable, then None.
            sol["nonzere_sols_homo"] (list[Matrix]): 
                a list of solutions of the equations Ax = 0. If not solable, then None.
    """
    n, m = A.shape
    if (n, 1) != b.shape:
        raise ValueError ("The shape of A and b shall fit the linear equations Ax = b.")
    
    def idx_first_non_empty(A: Matrix[Num], i: int, j: int) -> Optional[int]:
        """Find the index of the first element that is not empty in between A[i, j] and A[n-1, j].

        Args:
            i (int): starting row.
            j (int): column.

        Returns:
            Optional[int]: the first row index of the non-zero element, if not found return None.
        """
        for k in range(i, n):
            if A[i, j] != 0:
                return k
        return None

    sol_cols = [] # col idx for cols that can't be triangulize
    num_skipped_col = 0

    Ab = concatenate(A, b)

    sols = {
        "nonzero_sols_homo" : None,
        "sol_inhomo" : None,
        "solable": False
    }
    

    for j in range(m):
        start_row = j - num_skipped_col
        i = idx_first_non_empty(Ab, start_row, j) 
        if i is not None:
            if i != start_row:
                for l in range(j, m + 1):
                    Ab[start_row, l] += Ab[i, j] # This is faster than exchanging two rows
        else:
            sol_cols.append(j) # A null column
            num_skipped_col += 1
            continue
        
        Ajj = Ab[start_row, j]
        for l in range(j, m + 1):
            Ab[start_row, l] /= Ajj

        for i in range(n):
            if i != start_row:
                K = Ab[i, j]
                for l in range(j, m + 1):
                    Ab[i, l] -= K * Ab[start_row, l]

    unit_cols = [] # col numbers for cols like [0, ..., 1, ...]
    for j in range(m):
        if j not in sol_cols:
            unit_cols.append(j)

    for k in range(num_skipped_col):
        if abs(Ab[-k-1, -1]) > _EPS:
            return sols

    nonzero_sols_homo = []
    for j in sol_cols: # (label for free var, sol_col)
        sol_homo_vec = [0.] * n
        sol_homo_vec[j] = 1.
        for i in unit_cols:
            sol_homo_vec[i] = - Ab[i, j]
        
        nonzero_sols_homo.append(Matrix(sol_homo_vec, (n, 1)))
    
    sol_inhomo = [0.] * n
    for k, i in enumerate(unit_cols):
        sol_inhomo[i] = Ab[k, -1]
    

    if nonzero_sols_homo:
        sols["nonzero_sols_homo"] = nonzero_sols_homo
    else:
        sols["nonzero_sols_homo"] = None
    sols["sol_inhomo"] = Matrix(sol_inhomo, (n, 1))
    sols["solable"] = True

    return sols
