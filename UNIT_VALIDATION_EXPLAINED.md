# Unit Validation - How It Works

## Before the Fix

```
User inputs: A = L^2 [m^2]
             where L = 10 [m]

Parser extracts:
  - variable_units['A'] = 'm^2'  (from [m^2])
  - assignments['A'] = 'L**2'     (expression)

Solver evaluates:
  - L**2 = (10 m)^2 = 100 m^2    (calculated units)
  
Problem:
  - Calculated units (m^2) not validated against specified units (m^2)
  - No check that they match dimensionally
  - Units could be double-counted or mismatched
```

## After the Fix

```
User inputs: A = L^2 [m^2]
             where L = 10 [m]

Step 1 - Parse:
  variable_units['A'] = 'm^2'
  assignments['A'] = 'L**2'

Step 2 - Evaluate Expression:
  value = eval('L**2') = 100 m^2  (Pint Quantity with units)
  
Step 3 - Validate Units:
  ┌─────────────────────────────────────────────────┐
  │ Does expression have units? YES (m^2)           │
  │ Does variable have manual unit? YES (m^2)       │
  │                                                 │
  │ Create specified quantity: Q_(1.0, 'm^2')       │
  │                                                 │
  │ Check dimensionality:                           │
  │   calculated: [length]²                         │
  │   specified:  [length]²                         │
  │   Match? YES ✓                                  │
  │                                                 │
  │ Convert to user format:                         │
  │   value.to('m^2') = 100 m²                      │
  └─────────────────────────────────────────────────┘

Step 4 - Store Result:
  A = 100 m²  (using user's preferred unit format)
```

## Error Cases

### Case 1: Wrong Dimensionality
```
User inputs: A = L^2 [m]   (WRONG: should be m^2)
             where L = 10 [m]

Evaluation:
  value = eval('L**2') = 100 m^2

Validation:
  ┌─────────────────────────────────────────────────┐
  │ calculated: [length]² (m^2)                     │
  │ specified:  [length]  (m)                       │
  │ Match? NO ✗                                     │
  │                                                 │
  │ RAISE ValueError:                               │
  │ "Unit mismatch for variable 'A':                │
  │  Expression 'L**2' calculates to units 'm ** 2' │
  │  but 'm' was specified.                         │
  │  These have different dimensionalities."        │
  └─────────────────────────────────────────────────┘
```

### Case 2: Dimensionless vs Dimensional
```
User inputs: y = x * 2 [kg]
             where x = 5  (no units)

Evaluation:
  value = eval('x * 2') = 10  (no units, dimensionless)

Validation:
  ┌─────────────────────────────────────────────────┐
  │ Expression result: dimensionless                │
  │ Specified unit: kg (dimensional)                │
  │                                                 │
  │ Create specified quantity: Q_(1.0, 'kg')        │
  │ Is it dimensionless? NO                         │
  │                                                 │
  │ RAISE ValueError:                               │
  │ "Unit mismatch for variable 'y':                │
  │  Expression 'x * 2' produces a dimensionless    │
  │  result but dimensional unit 'kg' was           │
  │  specified."                                    │
  └─────────────────────────────────────────────────┘
```

### Case 3: Compatible Conversion
```
User inputs: A = L^2 [ft^2]  (different unit, same dimensionality)
             where L = 10 [m]

Evaluation:
  value = eval('L**2') = 100 m^2

Validation:
  ┌─────────────────────────────────────────────────┐
  │ calculated: [length]² (m^2)                     │
  │ specified:  [length]² (ft^2)                    │
  │ Match? YES ✓                                    │
  │                                                 │
  │ Convert to user format:                         │
  │   value.to('ft^2') = 1076.39 ft²               │
  └─────────────────────────────────────────────────┘

Result:  
  A = 1076.39 ft²  (auto-converted from m² to ft²)
```

## Key Benefits

1. **Prevents Silent Errors**: Unit mismatches are caught immediately
2. **Flexible Display**: User can specify preferred unit format
3. **Auto-Conversion**: Compatible units are automatically converted
4. **Clear Errors**: Descriptive messages explain exactlywhat's wrong
5. **Two-Layer Validation**: Catches errors in both forward evaluation and inference stages
