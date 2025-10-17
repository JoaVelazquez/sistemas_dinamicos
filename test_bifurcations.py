#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for bifurcation detection in the Bifurcaciones GUI application.

Run with: python test_bifurcations.py
"""

import unittest
import sys
import numpy as np
import sympy as sp
from sympy import sympify, diff

# Import the application class
from bifurcaciones_1 import BifurcationApp, find_equilibria, stability_fx


class TestBifurcationDetection(unittest.TestCase):
    """Unit tests for bifurcation detection algorithms."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a minimal app instance for testing
        self.app = BifurcationApp()
        self.app.withdraw()  # Hide the GUI window during testing
        
        # Set up symbolic variables
        self.x = sp.Symbol('x')
        self.r = sp.Symbol('r')
        
        # Set test parameters
        self.app.x_min.set(-2.0)
        self.app.x_max.set(2.0)
        self.app.r_min.set(-0.1)
        self.app.r_max.set(0.1)

    def tearDown(self):
        """Clean up after each test."""
        self.app.destroy()

    def test_saddle_node_bifurcation(self):
        """Test detection of saddle-node bifurcation with f(x,r) = r + x^2."""
        # Define the function: f(x,r) = r + x^2
        # This has a saddle-node bifurcation at r = 0
        f_expr = self.r + self.x**2
        fx_expr = diff(f_expr, self.x)
        fxx_expr = diff(fx_expr, self.x)
        
        # Generate test data around the bifurcation
        r_values = np.linspace(-0.05, 0.05, 11)
        equilibria_list = []
        
        for r_val in r_values:
            eq = find_equilibria(f_expr, self.x, self.r, r_val, -2, 2)
            equilibria_list.append(eq)
        
        # Detect bifurcations
        bifurcations = self.app._detect_bifurcation_type(f_expr, fx_expr, fxx_expr, r_values, equilibria_list)
        
        # Assertions
        self.assertTrue(len(bifurcations) > 0, "Should detect at least one bifurcation")
        
        # Check that a saddle-node bifurcation is detected near r=0
        saddle_node_found = False
        for r_bif, bif_type in bifurcations:
            if abs(r_bif) < 0.02 and "silla-nodo" in bif_type.lower():
                saddle_node_found = True
                break
        
        self.assertTrue(saddle_node_found, f"Should detect saddle-node bifurcation near r=0. Found: {bifurcations}")

    def test_transcritical_bifurcation(self):
        """Test detection of transcritical bifurcation with f(x,r) = rx - x^2."""
        # Define the function: f(x,r) = rx - x^2
        # This has a transcritical bifurcation at r = 0
        f_expr = self.r * self.x - self.x**2
        fx_expr = diff(f_expr, self.x)
        fxx_expr = diff(fx_expr, self.x)
        
        # Generate test data around the bifurcation
        r_values = np.linspace(-0.05, 0.05, 11)
        equilibria_list = []
        
        for r_val in r_values:
            eq = find_equilibria(f_expr, self.x, self.r, r_val, -2, 2)
            equilibria_list.append(eq)
        
        # Detect bifurcations
        bifurcations = self.app._detect_bifurcation_type(f_expr, fx_expr, fxx_expr, r_values, equilibria_list)
        
        # Assertions
        self.assertTrue(len(bifurcations) > 0, "Should detect at least one bifurcation")
        
        # Check that a transcritical bifurcation is detected near r=0
        transcritical_found = False
        for r_bif, bif_type in bifurcations:
            if abs(r_bif) < 0.02 and "transcrítica" in bif_type.lower():
                transcritical_found = True
                break
        
        self.assertTrue(transcritical_found, f"Should detect transcritical bifurcation near r=0. Found: {bifurcations}")

    def test_pitchfork_bifurcation(self):
        """Test detection of pitchfork bifurcation with f(x,r) = rx - x^3."""
        # Define the function: f(x,r) = rx - x^3
        # This has a pitchfork bifurcation at r = 0
        f_expr = self.r * self.x - self.x**3
        fx_expr = diff(f_expr, self.x)
        fxx_expr = diff(fx_expr, self.x)
        
        # Generate test data around the bifurcation
        r_values = np.linspace(-0.05, 0.05, 11)
        equilibria_list = []
        
        for r_val in r_values:
            eq = find_equilibria(f_expr, self.x, self.r, r_val, -2, 2)
            equilibria_list.append(eq)
        
        # Detect bifurcations
        bifurcations = self.app._detect_bifurcation_type(f_expr, fx_expr, fxx_expr, r_values, equilibria_list)
        
        # Assertions
        self.assertTrue(len(bifurcations) > 0, "Should detect at least one bifurcation")
        
        # Check that a pitchfork bifurcation is detected near r=0
        pitchfork_found = False
        for r_bif, bif_type in bifurcations:
            if abs(r_bif) < 0.02 and ("horquilla" in bif_type.lower() or "pitchfork" in bif_type.lower()):
                pitchfork_found = True
                break
        
        self.assertTrue(pitchfork_found, f"Should detect pitchfork bifurcation near r=0. Found: {bifurcations}")

    def test_no_bifurcation(self):
        """Test that no bifurcations are detected when there shouldn't be any."""
        # Define a function with no bifurcations: f(x,r) = -x^2 - 1
        # This always has no real equilibria
        f_expr = -self.x**2 - 1
        fx_expr = diff(f_expr, self.x)
        fxx_expr = diff(fx_expr, self.x)
        
        # Generate test data
        r_values = np.linspace(-0.1, 0.1, 11)
        equilibria_list = []
        
        for r_val in r_values:
            eq = find_equilibria(f_expr, self.x, self.r, r_val, -2, 2)
            equilibria_list.append(eq)
        
        # Detect bifurcations
        bifurcations = self.app._detect_bifurcation_type(f_expr, fx_expr, fxx_expr, r_values, equilibria_list)
        
        # Should detect no bifurcations
        self.assertEqual(len(bifurcations), 0, f"Should detect no bifurcations. Found: {bifurcations}")

    def test_equilibria_finding(self):
        """Test the equilibria finding function with known cases."""
        # Test case 1: f(x,r) = x^2 + r
        f1 = self.x**2 + self.r
        
        # For r = -1, should have two equilibria at x = ±1
        eq1 = find_equilibria(f1, self.x, self.r, -1, -2, 2)
        self.assertEqual(len(eq1), 2, "Should find 2 equilibria for r = -1")
        self.assertTrue(abs(abs(eq1[0]) - 1) < 0.01 or abs(abs(eq1[1]) - 1) < 0.01, 
                       "Should find equilibria near ±1")
        
        # For r = 1, should have no real equilibria
        eq2 = find_equilibria(f1, self.x, self.r, 1, -2, 2)
        self.assertEqual(len(eq2), 0, "Should find 0 equilibria for r = 1")

    def test_stability_analysis(self):
        """Test the stability analysis function."""
        # Test with f(x,r) = rx - x^2, f'(x,r) = r - 2x
        f_expr = self.r * self.x - self.x**2
        fx_expr = self.r - 2 * self.x
        
        # At r = 1, equilibria are at x = 0 and x = 1
        # x = 0: f'(0,1) = 1 > 0 → unstable
        stab1, slope1 = stability_fx(fx_expr, self.x, self.r, 0, 1)
        self.assertEqual(stab1, 'inestable', "x=0 should be unstable at r=1")
        self.assertGreater(slope1, 0, "Slope should be positive")
        
        # x = 1: f'(1,1) = 1 - 2 = -1 < 0 → stable
        stab2, slope2 = stability_fx(fx_expr, self.x, self.r, 1, 1)
        self.assertEqual(stab2, 'estable', "x=1 should be stable at r=1")
        self.assertLess(slope2, 0, "Slope should be negative")


def run_tests():
    """Run all bifurcation tests and display results."""
    print("Running bifurcation detection unit tests...")
    print("=" * 50)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestBifurcationDetection)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("✓ All tests passed! Bifurcation detection is working correctly.")
    else:
        print(f"✗ {len(result.failures)} test(s) failed, {len(result.errors)} error(s)")
        
        if result.failures:
            print("\nFailures:")
            for test, traceback in result.failures:
                print(f"- {test}: {traceback}")
                
        if result.errors:
            print("\nErrors:")
            for test, traceback in result.errors:
                print(f"- {test}: {traceback}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    # Set up minimal Tkinter environment for testing
    import tkinter as tk
    
    # Run the tests
    success = run_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)