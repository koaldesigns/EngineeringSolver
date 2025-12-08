import CoolProp.CoolProp as CP

class ThermoProps:
    """
    Wrapper for CoolProp to retrieve thermodynamic properties.
    """
    
    def get_prop(self, fluid: str, output_prop: str, input_prop1: str, value1: float, input_prop2: str, value2: float) -> float:
        """
        Calculates a property using CoolProp.
        Example: get_prop('Water', 'H', 'T', 300, 'P', 101325) returns Enthalpy.
        """
        try:
            # CoolProp expects uppercase for properties usually, but let's ensure
            return CP.PropsSI(output_prop.upper(), input_prop1.upper(), value1, input_prop2.upper(), value2, fluid)
        except Exception as e:
            raise ValueError(f"CoolProp Error: {e}")

    def get_fluid_list(self):
        return CP.get_global_param_string("fluids_list").split(',')
