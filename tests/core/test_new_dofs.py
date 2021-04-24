import unittest
import numpy as np
from collections import Counter

from simsopt._core.new_optimizable import DOF, DOFs
from simsopt.objectives.new_functions import Identity, Adder, \
                        TestObject2, Rosenbrock, Affine


class DOFTest(unittest.TestCase):
    """
    Unit tests for simsopt.core.DOF class
    """
    def setUp(self):
        self.dof1 = DOF(2.0, 'x', True, np.NINF, np.inf)
        self.dof2 = DOF(3.0, 'y', False, np.NINF, np.inf)

    def tearDown(self) -> None:
        self.dof1 = None
        self.dof2 = None

    #def test_hash(self):
    #    self.assertFalse(True)

    #def test_extended_name(self):
    #    self.assertFalse(True)

    def test_is_fixed(self):
        self.assertFalse(self.dof1.is_fixed())
        self.assertTrue(self.dof2.is_fixed())

    def test_is_free(self):
        self.assertTrue(self.dof1.is_free())
        self.assertFalse(self.dof2.is_free())

    def test_fix(self):
        self.dof1.fix()
        self.assertTrue(self.dof1.is_fixed())

    def test_unfix(self):
        self.dof2.unfix()
        self.assertTrue(self.dof2.is_free())

    def test_min(self):
        self.assertTrue(np.isclose(self.dof1.min, np.NINF))
        self.dof1.min = -10.0
        self.assertAlmostEqual(self.dof1.min, -10.0)

    def test_max(self):
        self.assertTrue(np.isclose(self.dof1.max, np.inf))
        self.dof1.max = 1e2
        self.assertAlmostEqual(self.dof1.max, 100.0)

    #def test_owner(self):
    #    self.assertTrue(False)

    def test_x(self):
        self.assertAlmostEqual(self.dof1.x, 2.0)
        self.dof1.x = 10.0
        self.assertAlmostEqual(self.dof1.x, 10.0)


class DOFsTests(unittest.TestCase):

    def setUp(self):
        self.identity_dofs = Identity(x=1, dof_name='x')._dofs
        self.adder_dofs = Adder(3, x0=[2, 3, 4], dof_names=["x", "y", "z"])._dofs
        self.rosenbrock_dofs = Rosenbrock()._dofs

    def tearDown(self) -> None:
        self.identity_dofs = None
        self.adder_dofs = None
        self.rosenbrock_dofs = None

    def test_init(self):
        # Create an empty dof and check all the methods
        empty_dof = DOFs()
        empty_dof.fix_all()
        empty_dof.unfix_all()
        self.assertFalse(empty_dof.any_free())
        self.assertFalse(empty_dof.any_fixed())
        self.assertTrue(empty_dof.all_free())
        self.assertTrue(empty_dof.all_fixed())
        empty_dof.x = []  # This statement working is what is desired
        self.assertTrue(len(empty_dof) == 0)
        self.assertTrue(empty_dof.reduced_len == 0)

    def test_fix(self):
        # TODO: This test uses too many methods of DOFs.
        self.adder_dofs.fix("x")
        self.assertTrue(self.adder_dofs.any_fixed())
        self.assertFalse(self.adder_dofs.all_free())
        self.assertEqual(self.adder_dofs.reduced_len, 2)
        with self.assertRaises(ValueError):
            self.adder_dofs.x = np.array([4,5,6])

        self.adder_dofs.fix("x")
        self.assertEqual(self.adder_dofs.reduced_len, 2)

        self.adder_dofs.fix("y")
        self.assertEqual(self.adder_dofs.reduced_len, 1)

    def test_fix_all(self):
        self.identity_dofs.fix_all()
        self.adder_dofs.fix_all()
        self.rosenbrock_dofs.fix_all()

        self.assertEqual(self.identity_dofs.reduced_len, 0)
        self.assertEqual(self.adder_dofs.reduced_len, 0)
        self.assertEqual(self.rosenbrock_dofs.reduced_len, 0)

    def test_unfix(self):
        self.adder_dofs.fix("x")
        self.adder_dofs.fix("y")
        self.rosenbrock_dofs.fix("x")
        self.assertEqual(self.adder_dofs.reduced_len, 1)
        self.assertEqual(self.rosenbrock_dofs.reduced_len, 1)

        self.adder_dofs.unfix("x")
        self.assertEqual(self.adder_dofs.reduced_len, 2)
        self.adder_dofs.unfix("x")
        self.assertEqual(self.adder_dofs.reduced_len, 2)
        self.rosenbrock_dofs.unfix("y")
        self.assertEqual(self.rosenbrock_dofs.reduced_len, 1)

    def test_unfix_all(self):
        self.adder_dofs.fix("x")
        self.rosenbrock_dofs.fix("x")

        self.adder_dofs.unfix_all()
        self.rosenbrock_dofs.unfix_all()

        self.assertEqual(self.identity_dofs.reduced_len, 1)
        self.assertEqual(self.adder_dofs.reduced_len, 3)
        self.assertEqual(self.rosenbrock_dofs.reduced_len, 2)

    def test_any_free(self):
        fixed_dofs = DOFs(x=np.array([1,2,3]),
                          names=np.array(['x', 'y', 'z']),
                          free=np.array([False, False, False]))
        self.assertFalse(fixed_dofs.any_free())
        one_fixed_dofs = DOFs(x=np.array([1,2,3]),
                          names=np.array(['x', 'y', 'z']),
                          free=np.array([True, True, False]))
        self.assertTrue(one_fixed_dofs.any_free())

    def test_any_fixed(self):
        free_dofs = DOFs(x=np.array([1,2,3]),
                          names=np.array(['x', 'y', 'z']),
                          free=np.array([True, True, True]))
        self.assertFalse(free_dofs.any_fixed())
        one_fixed_dofs = DOFs(x=np.array([1,2,3]),
                              names=np.array(['x', 'y', 'z']),
                              free=np.array([True, True, False]))
        self.assertTrue(one_fixed_dofs.any_fixed())

    def test_all_free(self):
        free_dofs = DOFs(x=np.array([1,2,3]),
                          names=np.array(['x', 'y', 'z']),
                          free=np.array([True, True, True]))
        self.assertTrue(free_dofs.all_free())
        one_fixed_dofs = DOFs(x=np.array([1,2,3]),
                              names=np.array(['x', 'y', 'z']),
                              free=np.array([True, True, False]))
        self.assertFalse(one_fixed_dofs.all_free())

    def test_all_fixed(self):
        fixed_dofs = DOFs(x=np.array([1,2,3]),
                          names=np.array(['x', 'y', 'z']),
                          free=np.array([False, False, False]))
        self.assertTrue(fixed_dofs.all_fixed())
        one_fixed_dofs = DOFs(x=np.array([1,2,3]),
                              names=np.array(['x', 'y', 'z']),
                              free=np.array([True, True, False]))
        self.assertFalse(one_fixed_dofs.all_fixed())

    def test_x(self):
        # Test the getter
        fixed_dofs = DOFs(x=np.array([1,2,3]),
                          names=np.array(['x', 'y', 'z']),
                          free=np.array([False, False, False]))
        free_dofs = DOFs(x=np.array([1,2,3]),
                         names=np.array(['x', 'y', 'z']),
                         free=np.array([True, True, True]))
        one_fixed_dofs = DOFs(x=np.array([1,2,3]),
                              names=np.array(['x', 'y', 'z']),
                              free=np.array([True, True, False]))
        self.assertTrue(np.allclose(fixed_dofs.x, np.array([])))
        self.assertTrue(np.allclose(free_dofs.x, np.array([1, 2, 3])))
        self.assertTrue(np.allclose(one_fixed_dofs.x, np.array([1, 2])))

        # Test the setter

        # Use full array size
        with self.assertRaises(ValueError):
            fixed_dofs.x = np.array([4, 5, 6])
        with self.assertRaises(ValueError):
            one_fixed_dofs.x = np.array([4, 5, 6])

        free_dofs.x = np.array([4, 5, 6])
        self.assertTrue(np.allclose(free_dofs.x, np.array([4, 5, 6])))
        one_fixed_dofs.x = np.array([4, 5])
        self.assertTrue(np.allclose(one_fixed_dofs.full_x, np.array([4, 5, 3])))

    def test_full_x(self):
        fixed_dofs = DOFs(x=np.array([1,2,3]),
                          names=np.array(['x', 'y', 'z']),
                          free=np.array([False, False, False]))
        free_dofs = DOFs(x=np.array([1,2,3]),
                         names=np.array(['x', 'y', 'z']),
                         free=np.array([True, True, True]))
        one_fixed_dofs = DOFs(x=np.array([1,2,3]),
                              names=np.array(['x', 'y', 'z']),
                              free=np.array([True, True, False]))
        output = np.array([1, 2, 3])
        self.assertTrue(np.allclose(fixed_dofs.full_x, output))
        self.assertTrue(np.allclose(free_dofs.full_x, output))
        self.assertTrue(np.allclose(one_fixed_dofs.full_x, output))

    def test_lower_bounds(self):
        dofs = DOFs(x=np.array([1,2,3]),
                    names=np.array(['x', 'y', 'z']),
                    free=np.array([True, True, False]))
        self.assertTrue(np.allclose(dofs.lower_bounds,
                                    np.array([np.NINF, np.NINF])))

        with self.assertRaises(ValueError):
            dofs.lower_bounds = np.array([-1000.0, -1001.0, -1002.0])
        with self.assertRaises(ValueError):
            dofs.lower_bounds = np.array([-1000.0])
        dofs.lower_bounds = np.array([-1000.0, -1001.0])
        self.assertTrue(np.allclose(dofs.lower_bounds,
                                    np.array([-1000.0, -1001.0])))

        dofs.unfix_all()
        self.assertTrue(np.allclose(dofs.lower_bounds,
                                    np.array([-1000.0, -1001.0, np.NINF])))

        dofs.lower_bounds = np.array([-1000.0, -1001.0, -1002.])
        self.assertTrue(np.allclose(dofs.lower_bounds,
                                    np.array([-1000.0, -1001.0, -1002.0])))

        with self.assertRaises(ValueError):
            dofs.lower_bounds = np.array([-1000.0])
        with self.assertRaises(ValueError):
            dofs.lower_bounds = np.array([-1000.0, -1001.0])

    def test_upper_bounds(self):
        dofs = DOFs(x=np.array([1,2,3]),
                    names=np.array(['x', 'y', 'z']),
                    free=np.array([True, True, False]))
        self.assertTrue(np.allclose(dofs.upper_bounds,
                                    np.array([np.inf, np.inf])))

        with self.assertRaises(ValueError):
            dofs.upper_bounds = np.array([1000.0, 1001.0, 1002.0])
        with self.assertRaises(ValueError):
            dofs.upper_bounds = np.array([1000.0])
        dofs.upper_bounds = np.array([1000.0, 1001.0])
        self.assertTrue(np.allclose(dofs.upper_bounds,
                                    np.array([1000.0, 1001.0])))

        dofs.unfix_all()
        self.assertTrue(np.allclose(dofs.upper_bounds,
                                    np.array([1000.0, 1001.0, np.inf])))

        dofs.upper_bounds = np.array([1000.0, 1001.0, 1002.])
        self.assertTrue(np.allclose(dofs.upper_bounds,
                                    np.array([1000.0, 1001.0, 1002.0])))

        with self.assertRaises(ValueError):
            dofs.upper_bounds = np.array([1000.0])
        with self.assertRaises(ValueError):
            dofs.upper_bounds = np.array([1000.0, 1001.0])

    def test_bounds(self):
        dofs = DOFs(x=np.array([1,2,3]),
                    names=np.array(['x', 'y', 'z']),
                    free=np.array([True, True, False]),
                    lower_bounds=np.array([-100.0, -101.0, -102.0]),
                    upper_bounds=np.array([100.0, 101.0, 102.0]))
        bounds = dofs.bounds
        self.assertTrue(np.allclose(bounds[0],
                                    np.array([-100.0, -101.0]))
                        and np.allclose(bounds[1],
                                        np.array([100.0, 101.0])))

    def test_update_upper_bound(self):
        dofs = DOFs(x=np.array([1,2,3]),
                    names=np.array(['x', 'y', 'z']),
                    free=np.array([True, True, False]),
                    lower_bounds=np.array([-100.0, -101.0, -102.0]),
                    upper_bounds=np.array([100.0, 101.0, 102.0]))
        dofs.update_upper_bound("x", 200)
        self.assertTrue(np.allclose(dofs.upper_bounds,
                                    np.array([200.0, 101.0])))

        # Test with integer keys

    def test_update_lower_bound(self):
        dofs = DOFs(x=np.array([1,2,3]),
                    names=np.array(['x', 'y', 'z']),
                    free=np.array([True, True, False]),
                    lower_bounds=np.array([-100.0, -101.0, -102.0]),
                    upper_bounds=np.array([100.0, 101.0, 102.0]))
        dofs.update_lower_bound("x", -200)
        self.assertTrue(np.allclose(dofs.lower_bounds,
                                    np.array([-200.0, -101.0])))
        # Test with integer keys

    def test_update_bounds(self):
        pass
               

if __name__ == "__main__":
    unittest.main()
