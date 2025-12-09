from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import json
import os
from pathlib import Path
from sqlalchemy.orm import Session

from solver.numerical import NumericalSolver
from solver.thermo import ThermoProps
from solver.units import UnitRegistry
from solver.plotting import generate_plots_from_results
from database import get_db
from models import User, UserPreferences, EquationTab, EquationSet as EquationSetModel
from auth import get_current_user, get_current_user_optional

router = APIRouter()
solver = NumericalSolver()
thermo = ThermoProps()
units = UnitRegistry()

# Limits for user data
MAX_TABS_PER_USER = 50
MAX_SETS_PER_TAB = 100

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

class ConvertUnitRequest(BaseModel):
    value: float
    from_unit: str
    to_unit: str

class ConvertUnitResponse(BaseModel):
    success: bool
    value: Optional[float] = None
    unit: Optional[str] = None  # Formatted display unit
    factor: Optional[float] = None  # Conversion factor (to_value = from_value * factor)
    error: Optional[str] = None

class UnitSuggestionsRequest(BaseModel):
    unit: str

class UnitSuggestionsResponse(BaseModel):
    success: bool
    suggestions: List[str] = []
    error: Optional[str] = None

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

@router.post("/convert-unit", response_model=ConvertUnitResponse)
async def convert_unit(request: ConvertUnitRequest):
    """
    Convert a value from one unit to another using Pint.
    Supports compound units like m/s, kg/m^3, J/(kg*K), etc.
    Returns the converted value, formatted unit, and conversion factor.
    """
    try:
        # Use the existing UnitRegistry for conversion
        converted_value = units.convert(request.value, request.from_unit, request.to_unit)
        
        # Calculate conversion factor (useful for caching)
        factor = converted_value / request.value if request.value != 0 else units.convert(1.0, request.from_unit, request.to_unit)
        
        # Format the display unit
        formatted_unit = units.format_unit_display(request.to_unit)
        
        return {
            "success": True,
            "value": converted_value,
            "unit": formatted_unit or request.to_unit,
            "factor": factor
        }
    except ValueError as e:
        return {
            "success": False,
            "error": str(e)
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Conversion failed: {str(e)}"
        }

@router.post("/unit-suggestions", response_model=UnitSuggestionsResponse)
async def get_unit_suggestions(request: UnitSuggestionsRequest):
    """
    Get compatible unit suggestions for a given unit based on dimensional analysis.
    Uses Pint to determine the dimensionality and returns common engineering units.
    """
    try:
        suggestions = units.get_compatible_units(request.unit)
        return {
            "success": True,
            "suggestions": suggestions
        }
    except Exception as e:
        return {
            "success": False,
            "suggestions": [],
            "error": str(e)
        }


# ============== Custom Tabs API ==============

class EquationSetSchema(BaseModel):
    id: str
    title: str
    description: str
    equations: str

class CustomTabSchema(BaseModel):
    id: str
    name: str
    icon: str
    equationSets: List[EquationSetSchema]

class CustomTabsData(BaseModel):
    tabs: List[CustomTabSchema]

class ImportTabRequest(BaseModel):
    tab: CustomTabSchema


def tabs_to_dict(tabs: List[EquationTab]) -> List[dict]:
    """Convert database EquationTab objects to frontend-compatible dicts."""
    result = []
    for tab in sorted(tabs, key=lambda t: t.position):
        sets = []
        for eq_set in sorted(tab.equation_sets, key=lambda s: s.position):
            sets.append({
                "id": eq_set.set_id,
                "title": eq_set.title,
                "description": eq_set.description or "",
                "equations": eq_set.equations or ""
            })
        result.append({
            "id": tab.tab_id,
            "name": tab.name,
            "icon": tab.icon or "📐",
            "equationSets": sets
        })
    return result


@router.get("/custom-tabs")
async def get_custom_tabs(
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Get all custom tabs for the current user.
    Returns empty list if not logged in.
    """
    if not current_user:
        return {"tabs": [], "logged_in": False}
    
    tabs = db.query(EquationTab).filter(
        EquationTab.user_id == current_user.id
    ).all()
    
    return {"tabs": tabs_to_dict(tabs), "logged_in": True}


@router.post("/custom-tabs")
async def save_all_custom_tabs(
    data: CustomTabsData,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Save all custom tabs for the current user.
    Requires authentication.
    """
    # Enforce tab limit
    if len(data.tabs) > MAX_TABS_PER_USER:
        raise HTTPException(
            status_code=400, 
            detail=f"Maximum {MAX_TABS_PER_USER} tabs allowed"
        )
    
    # Delete all existing tabs for this user
    db.query(EquationTab).filter(
        EquationTab.user_id == current_user.id
    ).delete()
    
    # Create new tabs
    for position, tab_data in enumerate(data.tabs):
        # Enforce set limit per tab
        if len(tab_data.equationSets) > MAX_SETS_PER_TAB:
            raise HTTPException(
                status_code=400,
                detail=f"Maximum {MAX_SETS_PER_TAB} equation sets per tab allowed"
            )
        
        new_tab = EquationTab(
            user_id=current_user.id,
            tab_id=tab_data.id,
            name=tab_data.name,
            icon=tab_data.icon,
            position=position
        )
        db.add(new_tab)
        db.flush()  # Get tab ID
        
        for set_position, eq_set in enumerate(tab_data.equationSets):
            new_set = EquationSetModel(
                tab_id=new_tab.id,
                set_id=eq_set.id,
                title=eq_set.title,
                description=eq_set.description,
                equations=eq_set.equations,
                position=set_position
            )
            db.add(new_set)
    
    db.commit()
    return {"status": "saved", "message": f"Saved {len(data.tabs)} tabs"}


@router.get("/custom-tabs/export/{tab_id}")
async def export_custom_tab(
    tab_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export a single custom tab for sharing."""
    tab = db.query(EquationTab).filter(
        EquationTab.user_id == current_user.id,
        EquationTab.tab_id == tab_id
    ).first()
    
    if not tab:
        raise HTTPException(status_code=404, detail=f"Tab with id '{tab_id}' not found")
    
    tabs_dict = tabs_to_dict([tab])
    return {"tab": tabs_dict[0]}


@router.post("/custom-tabs/import")
async def import_custom_tab(
    request: ImportTabRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Import a custom tab from shared data."""
    # Check tab limit
    existing_count = db.query(EquationTab).filter(
        EquationTab.user_id == current_user.id
    ).count()
    
    if existing_count >= MAX_TABS_PER_USER:
        raise HTTPException(
            status_code=400,
            detail=f"Maximum {MAX_TABS_PER_USER} tabs reached"
        )
    
    # Check for duplicate tab_id and make unique
    new_tab_id = request.tab.id
    existing_ids = set(
        t.tab_id for t in db.query(EquationTab).filter(
            EquationTab.user_id == current_user.id
        ).all()
    )
    
    counter = 1
    original_id = new_tab_id
    while new_tab_id in existing_ids:
        new_tab_id = f"{original_id}_{counter}"
        counter += 1
    
    # Create new tab
    new_tab = EquationTab(
        user_id=current_user.id,
        tab_id=new_tab_id,
        name=request.tab.name,
        icon=request.tab.icon,
        position=existing_count
    )
    db.add(new_tab)
    db.flush()
    
    for set_position, eq_set in enumerate(request.tab.equationSets):
        new_set = EquationSetModel(
            tab_id=new_tab.id,
            set_id=eq_set.id,
            title=eq_set.title,
            description=eq_set.description,
            equations=eq_set.equations,
            position=set_position
        )
        db.add(new_set)
    
    db.commit()
    
    # Return the tab as dict
    tabs_dict = tabs_to_dict([new_tab])
    return {"status": "imported", "tab": tabs_dict[0]}


# ============== User Preferences API ==============

class PreferencesSchema(BaseModel):
    theme_mode: Optional[str] = None
    accent_hue: Optional[int] = None
    accent_brightness: Optional[int] = None
    extra_settings: Optional[Dict[str, Any]] = None


@router.get("/preferences")
async def get_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user preferences."""
    prefs = db.query(UserPreferences).filter(
        UserPreferences.user_id == current_user.id
    ).first()
    
    if not prefs:
        # Create default preferences
        prefs = UserPreferences(user_id=current_user.id)
        db.add(prefs)
        db.commit()
        db.refresh(prefs)
    
    return {
        "theme_mode": prefs.theme_mode,
        "accent_hue": prefs.accent_hue,
        "accent_brightness": prefs.accent_brightness,
        "extra_settings": prefs.extra_settings or {}
    }


@router.put("/preferences")
async def update_preferences(
    prefs_data: PreferencesSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user preferences."""
    prefs = db.query(UserPreferences).filter(
        UserPreferences.user_id == current_user.id
    ).first()
    
    if not prefs:
        prefs = UserPreferences(user_id=current_user.id)
        db.add(prefs)
    
    if prefs_data.theme_mode is not None:
        prefs.theme_mode = prefs_data.theme_mode
    if prefs_data.accent_hue is not None:
        prefs.accent_hue = prefs_data.accent_hue
    if prefs_data.accent_brightness is not None:
        prefs.accent_brightness = prefs_data.accent_brightness
    if prefs_data.extra_settings is not None:
        prefs.extra_settings = prefs_data.extra_settings
    
    db.commit()
    
    return {
        "status": "updated",
        "theme_mode": prefs.theme_mode,
        "accent_hue": prefs.accent_hue,
        "accent_brightness": prefs.accent_brightness,
        "extra_settings": prefs.extra_settings or {}
    }
