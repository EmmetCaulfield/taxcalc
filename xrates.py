#!/usr/bin/env python3

import sys
import json
from statistics import mean, median

                
def die(msg: str, code: int=2):
    print(f'FATAL: {msg}')
    sys.exit(code)

def usage():
    print("USAGE: xrates <amount> <currency-code>")
    sys.exit(1)

class Currency():
    def __init__(self:object, sym: str, amt: float) -> None:
        self.from_sym = sym
        self.amount = float(amt)
        self.to_sym = {}

    def to(self: object, sym: str, val: float) -> None:
        if sym not in self.to_sym:
            self.to_sym[sym] = []
        self.to_sym[sym].append(float(val)/float(self.amount))

    def mean(self: object, sym: str, dp:int = 4) -> float:
        if sym not in self.to_sym:
            raise KeyError(f"Symbol '{sym}' not in {list(self.to_sym.keys())}")
        return round(mean(self.to_sym[sym]), dp)

    def median(self: object, sym: str, dp:int = 4) -> float:
        return round(median(self.to_sym[sym]), dp)

    def max(self: object, sym: str, dp:int = 4) -> float:
        return round(max(self.to_sym[sym]), dp)

    def min(self: object, sym: str, dp:int = 4) -> float:
        return round(min(self.to_sym[sym]), dp)

    def invert(self: object, sym: str) -> object:
        if sym == self.from_sym:
            return self
        if sym not in self.to_sym:
            return None
        inv = Currency(sym, 1.0)
        inv.to_sym[self.from_sym] = [1.0/x for x in self.to_sym[sym]]
        for s in self.to_sym.keys():
            if s == sym:
                continue
            else:
                inv.to_sym[s] = [y/x for (x,y) in zip(self.to_sym[sym], self.to_sym[s])]
        return inv


def loadCurrencyData(filename: str = 'xrates.json'):
    with open(filename) as f:
        try:
            rates = json.load(f)
        except Exception as e:
            die(f"exception ({e}) loading JSON from file ({filename})")
    amount = rates["amount"]
    fromcur = rates["from"]
    curr = Currency(fromcur, amount)
    for sym in rates["to"].keys():
        for datum in rates["to"][sym]:
            curr.to(sym, float(datum["mid"]))
    return curr
            
def main():
    if len(sys.argv) != 3:
        usage()
    usd = loadCurrencyData()
    amt = float(sys.argv[1])
    cc  = sys.argv[2].upper()
    if cc == "STG":
        cc = "GBP"
    cur = usd.invert(cc)
    if cur is None:
        die("Unknown currency code '{cc}'")
    for code in cur.to_sym.keys():
        lo = cur.min(code) * amt
        mid = cur.mean(code) * amt
        hi = cur.max(code) * amt
        p = 100*(hi - mid)/mid
        m = 100*(mid - lo)/mid
        print(f"{code} {lo:.2f} {mid:.2f} {hi:.2f} (-{m:.2f}/+{p:.2f}%)")
    
if __name__ == "__main__":
    main()
 
