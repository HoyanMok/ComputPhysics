"""Basic numerical polynomial operations"""
from itertools import islice
from numbers import Complex, Real
from math import factorial
from typing import Union

# from types import NotImplementedType only supported by python3.10+, 
# which is not implemented by pypy yet
NotImplementedType = type(NotImplemented)   

class Polynomial:
    """Polynomial class, with basic operations"""
    def __init__(self, factors: list):
        """generates a polynomial that satisfies y = factors[0] + x * factors[1] + ... + x**d * factors[d]

        Args:
            factors (list): the factors of the polynomial, factors[i] is the factor of x ** i.
        """
        for i in range(len(factors) - 1, -1, -1):
            if factors[i] != 0:
                self.d = i
                self.factors = factors[:i+1]
                break
        else:
            self.d = 0
            self.factors = [0.]

    def __call__(self, x):
        """Using Qin Jiushao (秦九韶) method to evaluate the polynomial's value at x"""
        factors = self.factors
        y = factors[-1]
        for f in islice(reversed(factors), 1, None):
            y = x * y + f
        return y

    def __add__(self, P):
        factors = (self.factors).copy()
        if not isinstance(P, Polynomial):
            factors[0] += P
            return Polynomial(factors)
        else:
            for i in range(min(len(factors), len(P.factors))):
                factors[i] += P.factors[i]
            if P.d > self.d:
                factors += P.factors[self.d+1:]
            return Polynomial(factors)

    def __radd__(self, P):
        return self + P

    def __mul__(self, P):
        if not isinstance(P, Polynomial):
            return Polynomial([P * factor for factor in self.factors])
        else:
            d = self.d + P.d
            factors = []
            for i in range(d + 1):
                factor = 0
                for j in range(max(0, i - P.d), min(i, self.d) + 1):
                    factor += self.factors[j] * P.factors[i-j] 
                factors.append(factor)
            
            return Polynomial(factors)

    def __rmul__(self, P):
        return self * P

    def __pow__(self, p: int) -> Union["Polynomial", NotImplementedType]: 
        if p < 0:
            return NotImplemented
        elif p == 0:
            return Polynomial([1])
        elif p < 16:
            result = self
            for _ in range(p-1):
                result *= self
        else:
            result = 1
            gen_bin = (int(i) for i in bin(p)[2:])
            A2i = self
            for bi in gen_bin:
                if bi == 1:
                    result *= A2i
                A2i **= 2 
        return result

    def __repr__(self):
        if self.factors[-1] == 0:
            return "zero Polynomial\n0"

        factors = self.factors
        for i, f in enumerate(factors):
            if f != 0:
                fst_idx_nonzero = i
                break

        fst_factor = factors[fst_idx_nonzero]
        if isinstance(fst_factor, Complex):
            poly_str = "({})".format(fst_factor)
        else:
            poly_str = "{}".format(fst_factor)
        if fst_idx_nonzero != 0:
            poly_str += " X"
            if fst_idx_nonzero != 1:
                poly_str += "^{}".format(fst_idx_nonzero)

        for i, f in islice(enumerate(factors), fst_idx_nonzero + 1, None):
            if i == 0 or f == 0:
                continue
            if isinstance(f, Real) and f < 0:
                sign = " - "
            else:
                sign = " + "
            poly_str += sign
            if i == 1:
                if isinstance(f, Complex):
                    poly_str += "({}) X".format(f)
                else:
                    poly_str += "{} X".format(abs(f))
            else:
                if isinstance(f, Complex):
                    poly_str += "({}) X^{}".format(f, i)
                else:
                    poly_str += "{} X^{}".format(abs(f), i)
                

        return "Polynomial of degree {} \n".format(self.d) + poly_str

    def __truediv__(self, value):
        return self * value**(-1)

    def diff(self, n: int=1):
        d = self.d
        if n > d:
            return zero_poly(type(self.factors[0]))
        
        factors = self.factors
        diff_factors = [0] * (d - n + 1)
        for i in range(d - n + 1):
            diff_factors[i] = factors[i + n]
            for j in range(n):
                diff_factors[i] *= (i + n - j)
        
        return Polynomial(diff_factors)

def zero_poly(type=int):
    return Polynomial([type(0)])

def polynomial_integrate(poly: Polynomial):
    d = poly.d
    int_poly_factors = poly.factors.copy()
    int_poly_factors.insert(0, 0)
    for i in range(2, d + 2):
        int_poly_factors[i] /= i
    return Polynomial(int_poly_factors)
        
def Legendre(n):
    """Orthogonal polynomials in [-1, 1]

    Args:
        n ([type]): the degree of the polynomials (\in \mathbb N)

    Returns:
        Polynomial
    """
    p = (Polynomial([-1, 0, 1])) ** n
    return p.diff(n=n) / (2**n * factorial(n))

