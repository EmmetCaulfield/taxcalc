#!/usr/bin/env python3

import sys
                
def die(msg: str, code: int=2):
    print(f'FATAL: {msg}')
    sys.exit(code)

def usage():
    print("USAGE: mgcalc <amount> <term-years> <annual-rate>")
    sys.exit(1)


def monthly_payment(r:float, P:float, N:int) -> float:
    """Calculates the monthly payment, `c`, given the simple monthly rate,
    `r`, principal, `P`, and number of months, `N`, using the formula
    and notation from
    https://en.wikipedia.org/wiki/Mortgage_calculator

    """
    k = pow(1.0+r, N)
    c = r*P*k/(k-1.0)
    return round(c, 2)


def main():
    if len(sys.argv) != 4:
        usage()
    amt = 100000
    yrs = 20
    rpy = 5
    try:
        amt = int(round(float(sys.argv[1]),0))
        yrs = int(sys.argv[2])
        rpy = float(sys.argv[3])/100.0
    except Exception as x:
        die(x)

    if yrs > 100:
        die(f"Term in years ({yrs}) can't be over 100")
    if rpy > 20:
        die(f"Annual interest rate ({rpy}) cannot exceed 20%")
        
    c = monthly_payment(rpy/12.0, float(amt), 12*yrs)
#    print(f"r: {100*r:.2f}, P: {P:.0f}, N: {N}, k: {k:.3f}")
    print(f"Monthly payment: {c:.2f}")


if __name__ == "__main__":
    main()
