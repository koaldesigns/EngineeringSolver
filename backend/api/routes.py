from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import json
import os
from pathlib import Path
from solver.numerical import NumericalSolver
from solver.thermo import ThermoProps
from solver.units import UnitRegistry
from solver.plotting import generate_plots_from_results

router = APIRouter()
solver = NumericalSolver()
thermo = ThermoProps()
units = UnitRegistry()

# Custom tabs storage path
CUSTOM_TABS_FILE = Path(__file__).parent.parent.parent / "user_data" / "custom_tabs.json"

def ensure_custom_tabs_file():
    """Ensure the custom tabs file exists."""
    CUSTOM_TABS_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not CUSTOM_TABS_FILE.exists():
        with open(CUSTOM_TABS_FILE, 'w') as f:
            json.dump({"tabs": []}, f)

def load_custom_tabs():
    """Load custom tabs from file."""
    ensure_custom_tabs_file()
    try:
        with open(CUSTOM_TABS_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {"tabs": []}

def save_custom_tabs(data):
    """Save custom tabs to file."""
    ensure_custom_tabs_file()
    with open(CUSTOM_TABS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

class SolveRequest(BaseModel):
    equations: List[str]
    guesses: Optional[Dict[str, float]] = None
    angle_unit: Optional[str] = "deg"
    output_units: Optional[Dict[str, str]] = None
    array_mode: Optional[str] = "parallel"  # "parallel" or "grid"

class SolveResponse(BaseModel):
    results: Dict[str, Dict[str, Any]]  # {var: {value: float|List[float], unit: str, is_array?: bool}}
    status: str
    unit_warnings: Optional[List[str]] = None
    plots: Optional[List[Dict[str, Any]]] = None  # Plotly configurations
    is_array_solve: Optional[bool] = None

@router.post("/solve", response_model=SolveResponse)
async def solve_equations(request: SolveRequest):
    try:
        # Try array solve first (will fall back to regular solve if no arrays)
        raw_results, unit_warnings, is_array_solve, plot_directives = solver.solve_with_arrays(
            request.equations, 
            request.guesses, 
            request.angle_unit,
            request.array_mode or "parallel"
        )
        
        # Handle output unit conversion
        final_results = {}
        for var, data in raw_results.items():
            val = data["value"]
            unit = data.get("unit", "")
            is_array = data.get("is_array", False)
            unit_source = data.get("unit_source", "propagated")
            
            if request.output_units and var in request.output_units:
                target_unit = request.output_units[var]
                if unit:
                    try:
                        if isinstance(val, list):
                            # Convert each element in array
                            val = [units.convert(v, unit, target_unit) for v in val]
                        else:
                            val = units.convert(val, unit, target_unit)
                        unit = target_unit
                    except Exception as e:
                        # If conversion fails, keep original
                        pass
            
            # Format the unit for pretty display
            formatted_unit = units.format_unit_display(unit) if unit else ""
            result_entry = {"value": val, "unit": formatted_unit, "unit_source": unit_source}
            if is_array:
                result_entry["is_array"] = True
            final_results[var] = result_entry
        
        # Generate plots if there are plot directives and array results
        plots = None
        if is_array_solve and plot_directives:
            plots = generate_plots_from_results(final_results, plot_directives)
        
        return {
            "results": final_results, 
            "status": "converged", 
            "unit_warnings": unit_warnings if unit_warnings else None,
            "plots": plots if plots else None,
            "is_array_solve": is_array_solve
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

class ThermoRequest(BaseModel):
    fluid: str
    output_prop: str
    input_prop1: str
    value1: float
    input_prop2: str
    value2: float

@router.post("/thermo")
async def get_thermo_prop(request: ThermoRequest):
    try:
        val = thermo.get_prop(
            request.fluid, 
            request.output_prop, 
            request.input_prop1, 
            request.value1, 
            request.input_prop2, 
            request.value2
        )
        return {"value": val}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============== Custom Tabs API ==============

class EquationSet(BaseModel):
    id: str
    title: str
    description: str
    equations: str

class CustomTab(BaseModel):
    id: str
    name: str
    icon: str
    equationSets: List[EquationSet]

class CustomTabsData(BaseModel):
    tabs: List[CustomTab]

class ImportTabRequest(BaseModel):
    tab: CustomTab

@router.get("/custom-tabs")
async def get_custom_tabs():
    """Get all custom tabs."""
    try:
        data = load_custom_tabs()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/custom-tabs")
async def save_all_custom_tabs(data: CustomTabsData):
    """Save all custom tabs."""
    try:
        save_custom_tabs(data.dict())
        return {"status": "saved", "message": f"Saved {len(data.tabs)} tabs"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/custom-tabs/export/{tab_id}")
async def export_custom_tab(tab_id: str):
    """Export a single custom tab for sharing."""
    try:
        data = load_custom_tabs()
        for tab in data.get("tabs", []):
            if tab.get("id") == tab_id:
                return {"tab": tab}
        raise HTTPException(status_code=404, detail=f"Tab with id '{tab_id}' not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/custom-tabs/import")
async def import_custom_tab(request: ImportTabRequest):
    """Import a custom tab from shared data."""
    try:
        data = load_custom_tabs()
        # Check for duplicate ID and rename if needed
        new_tab = request.tab.dict()
        existing_ids = {tab.get("id") for tab in data.get("tabs", [])}
        
        # Generate unique ID if conflict
        original_id = new_tab["id"]
        counter = 1
        while new_tab["id"] in existing_ids:
            new_tab["id"] = f"{original_id}_{counter}"
            counter += 1
        
        data["tabs"].append(new_tab)
        save_custom_tabs(data)
        return {"status": "imported", "tab": new_tab}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
