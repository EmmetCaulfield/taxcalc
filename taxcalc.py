#!/usr/bin/env python3

import sys
import yaml

def die(msg: str, code: int=2):
    print(f'FATAL: {msg}')
    sys.exit(code)

def usage():
    print("USAGE: taxcalc <country-code> <gross-pay>")
    sys.exit(1)
    
class Band():
    def __init__(self: object, lo: str, hi: str, rate: str) -> None:
        if lo is None:
            self.lo = 0.0
        else:
            self.lo = float(lo)
        if hi is None:
            self.hi = float("inf")
        else:
            self.hi = float(hi)
        self.rate = float(rate)

        # To calculate loss of tax-free allowance above a certain
        # amount (as done in the UK):
        self.slope = None
        self.origin = None

    # Low limit:
    def low(self: object, override: float) -> float:
        if override is None:
            return self.lo
        return override


class Credit():
    def __init__(self: object, id: str, name: str, amount: str) -> None:
        self.id = id
        self.name = name
        self.amount = float(amount)

class Country():
    def __init__(self: object, id: str, name: str) -> None:
        self.id = id
        self.name = name
        self.taxes = []

    def addTax(self:object, tax: object) -> None:
        self.taxes.append(tax)
    
class Tax():
    def __init__(self: object, id: str, name: str, country: str) -> None:
        self.id = id
        self.name = name
        self.country = country
        self.bands = []

        # To apply an alternative minimum tax (as is done in
        # Singapore):
        self.altmin = None
        
        # To apply tax credits (as is done in Ireland):
        self.credits = []

    def appendBand(self: object, hi: str, rate: str) -> object:
        lo = 0.0
        if len(self.bands) > 0:
            lo = float(self.bands[-1].hi) + 0.01
        band = Band(lo, hi, rate)
        self.bands.append(band)
        return band

    def appendCredit(self: object, id: str, name: str, amount: str) -> object:
        cr = Credit(id, name, amount)
        self.credits.append(cr)
        return cr

    def totalCredits(self: object) -> float:
        ttl = 0.0
        for cr in self.credits:
            print(f"\t{cr.name:>49s}: ({cr.amount:-8.2f})")
            ttl += cr.amount
        return ttl

    def alternativeMinimumTax(self: object, gross: float) -> float:
        if self.altmin is not None:
            return gross * float(self.altmin)/100.0
        else:
            return 0.0

    # Gross tax before credits
    def grossTaxBeforeCredits(self: object, gross: float) -> float:
        # Compute effective bands, applying sliding bands if any:
        ebands = []
        lo_override = None
        # print(yaml.dump(self.bands))
        for i, b in enumerate(self.bands):
            if b.slope is not None:
                # print("Applying slope")
                origin = float(b.origin)
                y, x = b.slope.split("/")
                # Rate of loss over origin
                rate = float(y) / float(x)
                base = (gross - origin)
                if base <= 0:
                    # Gross is too small for reduction in band to apply
                    ebands.append((b.low(lo_override), b.hi, b.rate, lo_override is None))
                    lo_override = None
                    continue
                # Amount of band lost:
                loss = rate * base
                new_hi = b.hi + loss
                if new_hi <= b.lo:
                    # The entire band has been lost. The next higher
                    # band's lower limit is now this band's lower
                    # limit and this band can be eliminated
                    lo_override = b.lo
                    continue
                # Some of the band has been lost:
                ebands.append((b.low(lo_override), new_hi, b.rate, False))
                lo_override = new_hi + 0.01
                continue
            # b.slope is none, just copy the band across
            ebands.append((b.low(lo_override), b.hi, b.rate, lo_override is None))
            lo_override = None

        tax = 0.0
        for i, (lo, hi, rate, adj) in enumerate(ebands):
            if gross > hi:
                span = hi - lo
            elif gross > lo:
                span = gross - lo
            else:
                break
            t = span * float(rate)/100.0
            tax += t
            star = ' ' if adj else '*'
            print(f"  Band {i}{star}{lo:9.2f}, {hi:9.2f}, {rate:4.1f} : {span:9.2f}, {t:8.2f}, {tax:9.2f}")
        return tax

    def grossTax(self: object, gross: float) -> float:
        tax = self.grossTaxBeforeCredits(gross) - self.totalCredits()
        atax = self.alternativeMinimumTax(gross)
        return max(tax, atax)

    def totalBurden(self: object, gross: float) -> float:
        return round(100.0*self.grossTax(gross)/gross, 2)

    @staticmethod
    def read(filename: str) -> dict[object]:
        taxes = {}
        countries = {}
        with open(filename) as f:
            try:
                tax_data = yaml.safe_load(f)
            except Exception as e:
                die(f"exception ({e}) loading YAML from file ({filename})")
        for tax in tax_data["taxes"]:
            t = Tax(tax["id"], tax["name"], tax["country"])
            if "bands" not in tax:
                die(f"No bands in tax {tax['id']}")
            for band in tax["bands"]:
                if 'high' not in band:
                    band['high'] = None;
                if 'rate' not in band:
                    die("No rate in band")
                b = t.appendBand(band['high'], band['rate'])
                if 'slide' in band:
                    s = band['slide']
                    b.origin = s['origin']
                    b.slope = s['slope']
            if "credits" in tax:
                for cr in tax["credits"]:
                    t.appendCredit(cr["id"], cr["name"], cr["amount"])
            if "altmin" in tax:
                t.altmin = float(tax["altmin"][0]["rate"])
            taxes[t.id] = t
        for country in tax_data["countries"]:
            c = Country(country["id"], country["name"])
            for t in country["taxes"]:
                c.addTax(taxes[t])
            countries[c.id] = c
        return countries

def main():
    if len(sys.argv) < 2:
        die("Need an amount as an argument")
    countries = Tax.read('bands.yaml')

    if len(sys.argv) != 3:
        usage()
    if sys.argv[1] not in countries:
        die(f"Unknown country '{sys.argv[1]}'")

    taxes = countries[sys.argv[1]].taxes
    gross = int(sys.argv[2])

    itax = []
    ttax = 0.0
    for t in taxes:
        print(f"{t.name} ({t.country})")
        amt = t.grossTax(gross)
        print(f"{t.name:>57s}: {amt:9.2f}\n")
        itax.append(str(round(amt)))
        ttax += amt
    nett = gross - ttax
    burden = round(100.0*ttax/gross, 2)

    print(f"{gross} -> {round(nett)} ({round(ttax)}={'+'.join(itax)} = {burden}%)")

if __name__ == "__main__":
    main()
