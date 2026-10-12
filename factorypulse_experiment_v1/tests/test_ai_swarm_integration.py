"""End-to-end CP-SAT test; unlike mock tests, executes solve_shared."""
import sys
import unittest
from pathlib import Path
sys.path[:0] = [str(Path(__file__).resolve().parents[1]), str(Path(__file__).resolve().parents[1] / 'src')]
from ai_swarm.integration import run_integrated_pilot

class IntegrationTests(unittest.TestCase):
    def test_amr_failure_material_cpsat_audit(self):
        try:
            import ortools  # noqa: F401
        except ImportError:
            self.skipTest('OR-Tools unavailable locally; CI requires OR-Tools and runs this test')
        report = run_integrated_pilot(timeout=10)
        self.assertNotEqual(report['failed_robot'], report['replacement_robot'])
        for item in report['arms'].values():
            self.assertIn(item['solver_status'], ('OPTIMAL', 'FEASIBLE'))
            self.assertFalse(item['independent_audit_errors'])
        self.assertGreaterEqual(report['failure_fleet_eta'], report['baseline_fleet_eta'])
        self.assertGreaterEqual(report['arms']['AMR_FAILURE']['material_eta'], report['arms']['BASELINE']['material_eta'])

if __name__ == '__main__': unittest.main()
