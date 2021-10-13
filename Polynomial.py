
class Polynomial:
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
        y = 0
        for i, f in enumerate(self.factors):
            y += x**i * f
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

    def __repr__(self):
        factors = self.factors
        poly_str = "{}".format(factors[0])
        for i, f in enumerate(factors):
            if i == 0 or f == 0:
                continue
            if f < 0:
                sign = " - "
            else:
                sign = " + "
            poly_str += sign
            if i == 1:
                poly_str += "{} X".format(abs(f))
            else:
                poly_str += "{} X^{}".format(abs(f), i)

        return "Polynomial of degree {} \n".format(self.d) + poly_str

    def __truediv__(self, value):
        return self * value**(-1)
        
        
