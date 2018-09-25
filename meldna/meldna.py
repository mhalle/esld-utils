import sqlite3
import sys
from collections import namedtuple
from math import log

TestResult = namedtuple("TestResult", ["value", "freshness"])


class MeldResult(object):
    def __init__(self, cre, inr, na, tbili):
        self.CRE = cre
        self.INR = inr
        self.NA = na
        self.TBILI = tbili

    @property
    def freshness(self):
        freshness = 0
        for a in ("CRE", "INR", "NA", "TBILI"):
            lab = getattr(self, a)
            if abs(freshness) < abs(lab.freshness):
                freshness = lab.freshness
        return freshness


    @property
    def freshness(self):
        """freshness is the number of days between the given
        date and the lab test farthest into the past or future. 
        A positive value of freshness means that the lab test
        happened before the query date. A negative value means 
        lab was taken after the query date."""
        
        freshness = 0
        for a in ("CRE", "INR", "NA", "TBILI"):
            lab = getattr(self, a)
            if abs(freshness) < abs(lab.freshness):
                freshness = lab.freshness
        return freshness

    @property
    def meld_float(self):
        val = (
            3.78 * log(self.TBILI.value)
            + 11.2 * log(self.INR.value)
            + 9.57 * log(self.CRE.value)
            + 6.43
        )
        return val

    @property
    def meld(self):
        return int(round(self.meld_float))

    @property
    def meldna_float(self):

        na = self.NA.value
        if na > 140.0:
            na = 140.0
        elif na < 125.0:
            na = 125.0
        meld = self.meld_float

        val = meld - na - (0.025 * meld * (140 - na)) + 140
        return val

    @property
    def meldna(self):
        return int(round(self.meldna_float))


class MeldCalculator(object):
    def __init__(self, db):
        self.db = db

    def meld_at_date(self, mrn, date):
        cur = self.db.cursor()

        results = {}
        for lab in (("CRE", "PCRE"), ("INR", "PTI"), ("NA", "PNA"), ("TBILI", "TBILI")):
            r = query_lab(cur, lab[1], mrn, date)
            if not r:
                raise ValueError("test result does not exist", lab[0], lab[1])
            results[lab[0]] = TestResult(float(r[1]), float(r[2]))
        return MeldResult(
            results["CRE"], results["INR"], results["NA"], results["TBILI"]
        )


def query_lab(cur, lab, mrn, date):
    template = """select test_id, Result, 
                julianday(?)-julianday(Seq_Date_Time) as freshness 
                from Labs where MRN = ? and test_id = ? order by abs(freshness) limit 1"""

    cur.execute(template, (date, mrn, lab))
    return cur.fetchone()


if __name__ == "__main__":
    db = sqlite3.connect(sys.argv[1])
    mrn = sys.argv[2]
    date = sys.argv[3]
    calc = MeldCalculator(db)

    result = calc.meld_at_date(mrn, date)
    print(
        "{} {} {} {} {}".format(mrn, date, result.meldna, result.meld, result.freshness)
    )

