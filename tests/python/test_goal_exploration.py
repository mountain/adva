from copy import deepcopy
from pathlib import Path
import unittest

from experiments.goal_exploration import calibration as c


class GoalExplorationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = Path(__file__).resolve().parents[2]
        cls.a = c.load_file(root / "examples/verified_witness/goal-exploration-f7.json")
        cls.r = cls.a["records"]
        cls.m = c.Meter()

    def test_artifact_replay_and_fixed_work_comparison(self):
        c.verify_artifact(self.a,self.m)
        for goal,n,answer in (("exists",2,True),("all",7,[1,6]),("unique",7,False)):
            short,full = self.r[f"main:{goal}"],self.r[f"baseline:{goal}"]
            self.assertEqual(len(short["rows"]),n)
            self.assertEqual(len(full["rows"]),7)
            self.assertEqual(short["judgment"]["answer"],answer)
            self.assertEqual(short["judgment"],full["judgment"])

    def test_question_decided_without_object_determined(self):
        r = self.r["main:exists"]
        self.assertEqual(r["discovered"],[1])
        self.assertIn(6,r["unvisited"])
        self.assertFalse(r["coverage_complete"])
        self.assertEqual(r["judgment"]["status"],"Verified")
        self.assertEqual(self.r["main:all"]["discovered"],[1,6])

    def test_one_witness_does_not_prove_unique(self):
        r = self.r["fuel2:unique"]
        self.assertEqual(r["discovered"],[1])
        self.assertEqual(r["judgment"]["status"],"Unknown")
        bad = deepcopy(r)
        bad["judgment"] = {"status":"Verified","answer":True,"basis":"one_witness"}
        with self.assertRaises(ValueError):
            c.verify_record(bad,self.m)

    def test_two_witnesses_refute_unique_before_coverage(self):
        r = self.r["reordered:unique"]
        self.assertEqual(r["discovered"],[6,1])
        self.assertFalse(r["coverage_complete"])
        self.assertEqual(len(r["rows"]),2)
        self.assertEqual(r["judgment"],{"status":"Verified","answer":False,"basis":"two_distinct_witnesses"})
        bad = deepcopy(r)
        bad["query"]["order"][1] = 6
        with self.assertRaises(ValueError):
            c.verify_record(bad,self.m)

    def test_complete_empty_distinct_from_zero_fuel_and_missing_input(self):
        for goal,answer in (("exists",False),("all",[]),("unique",False)):
            r = self.r[f"empty:{goal}"]
            self.assertEqual(r["judgment"]["answer"],answer)
            self.assertEqual(r["judgment"]["basis"],"complete_domain")
            self.assertTrue(r["coverage_complete"])
        zero = self.r["fuel0:exists"]
        self.assertEqual(zero["discovered"],[])
        self.assertEqual(zero["judgment"]["status"],"Unknown")
        self.assertEqual(zero["unvisited"],c.UNIVERSE)
        with self.assertRaises(c.MissingInput):
            c.task(None,1)
        self.assertFalse(self.a["missing_input"]["exploration_started"])

    def test_positive_uniqueness_needs_domain_evidence_in_this_checker(self):
        r = self.r["unique:unique"]
        self.assertEqual(r["judgment"],{"status":"Verified","answer":True,"basis":"complete_domain"})
        self.assertEqual(r["discovered"],[0])
        q = c.query("unique","unique",fuel=6)
        partial = c.explore(q,self.m)
        c.verify_record(partial,self.m)
        self.assertEqual(partial["judgment"]["status"],"Unknown")

    def test_partial_all_tampered_value_and_goal_drift_rejected(self):
        bad = deepcopy(self.r["fuel2:all"])
        bad["judgment"] = {"status":"Verified","answer":[1],"basis":"complete_domain"}
        with self.assertRaises(ValueError):
            c.verify_record(bad,self.m)
        bad = deepcopy(self.r["main:all"])
        bad["rows"].pop()
        with self.assertRaises(ValueError):
            c.verify_record(bad,self.m)
        bad = deepcopy(self.r["main:exists"])
        bad["rows"][0][1] = 0
        with self.assertRaises(ValueError):
            c.verify_record(bad,self.m)
        bad = deepcopy(self.r["main:exists"])
        bad["query"]["goal"] = "all"
        with self.assertRaises(ValueError):
            c.verify_record(bad,self.m)

    def test_fresh_equation_reuse_and_malformed_domain(self):
        self.assertEqual(self.r["fresh:all"]["judgment"]["answer"],[0,5])
        self.assertEqual(len(self.r["fresh:exists"]["rows"]),1)
        self.assertEqual(len(self.r["fresh:unique"]["rows"]),6)
        self.assertNotEqual(self.r["fresh:all"]["query"]["task"],self.r["main:all"]["query"]["task"])
        q = c.query("main","all")
        q["task"]["universe"] = []
        with self.assertRaises(ValueError):
            c.explore(q,self.m)
        for coefficients,rhs in (([True,0,6],1),([2,0],1),([2,0,6],7)):
            with self.assertRaises(ValueError):
                c.task(coefficients,rhs)


if __name__ == "__main__":
    unittest.main()
