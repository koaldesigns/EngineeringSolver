"""Quick test for reported issues."""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from backend.solver.numerical import NumericalSolver


solver = NumericalSolver()

# Test 1: Unit display (J/kg/K issue)
print("=== Test 1: Unit Display (J/kg/K) ===")
eqs = ['cp = 4180 [J/kg/K]']
results, warnings = solver.solve(eqs)
print(f"cp: {results['cp']}")

# Test 2: Natural frequency units
print("\n=== Test 2: Natural Frequency Units ===")
eqs = ['m = 10 [kg]', 'k = 1000 [N/m]', 'omega_n = sqrt(k / m)']
results, warnings = solver.solve(eqs)
print(f"omega_n: {results['omega_n']}")
# omega_n should be rad/s

# Test 3: Nitrogen P issue
print("\n=== Test 3: Nitrogen P display ===")
eqs = [
    'T = 100',
    'P = 500000',
    'rho = prop("Nitrogen", "D", "T", T, "P", P)'
]
results, warnings = solver.solve(eqs)
print(f"T: {results['T']}")
print(f"P: {results['P']}")
print(f"rho: {results['rho']}")

# Test 4: Mach number units
print("\n=== Test 4: Mach Number Units ===")
eqs = [
    'V = 340 [m/s]',
    'T = 288.15 [K]',  # Fixed: added unit
    'gamma = 1.4',
    'R = 287 [J/kg/K]',
    'a = sqrt(gamma * R * T)',
    'M = V / a'
]
results, warnings = solver.solve(eqs)
print(f"a: {results['a']}")
print(f"M: {results['M']}")

# Test 5: Cantilever deflection units
print("\n=== Test 5: Cantilever Deflection Units ===")
eqs = [
    'P = 1000 [N]',
    'L_beam = 2 [m]',
    'E_mod = 200e9 [Pa]',
    'b_width = 0.05 [m]',
    'h_beam = 0.1 [m]',
    'I_moment = b_width * h_beam^3 / 12',
    'delta_max = P * L_beam^3 / (3 * E_mod * I_moment)'
]
results, warnings = solver.solve(eqs)
print(f"delta_max: {results['delta_max']}")
# Should simplify to meters

# Test 6: AC Power Factor with acos
print("\n=== Test 6: AC Power Factor ===")
eqs = [
    'V_rms = 120',
    'I_rms = 10',
    'P_real = 1000',
    'S_apparent = V_rms * I_rms',
    'PF = P_real / S_apparent',
    'phi = acos(PF)'
]
results, warnings = solver.solve(eqs, angle_unit='deg')
print(f"S_apparent: {results.get('S_apparent', 'N/A')}")
print(f"PF: {results.get('PF', 'N/A')}")
print(f"phi: {results.get('phi', 'N/A')}")
print(f"Warnings: {warnings}")
