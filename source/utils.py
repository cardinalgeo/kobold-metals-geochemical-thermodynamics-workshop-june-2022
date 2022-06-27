import reaktoro as rkt

def add_element_concentration_constraint(specs, element): 
    def get_element_concentration(props, element):
        element_concentration = 1e6 * props.elementMassInPhase(element, "AqueousPhase") / props.phaseProps("AqueousPhase").mass() # [ppm]

        return element_concentration

    idx_element_conc = specs.addInput(f"{element} concentration")  # add symbol for a new input condition to the equilibrium problem

    element_conc_constraint = rkt.ConstraintEquation()
    element_conc_constraint.id = f"{element} concentration"  # give some identification name to the constraint
    element_conc_constraint.fn = lambda props, w: get_element_concentration(props, element) - w[idx_element_conc]  # the residual function 

    specs.addConstraint(element_conc_constraint)

    return specs

def add_salinity_constraint(specs): 

    def get_NaCl_concentration(props):
        NaCl_concentration = 100 * (props.elementMassInPhase("Na", "AqueousPhase") + props.elementMassInPhase("Cl", "AqueousPhase")) / props.phaseProps("AqueousPhase").mass() # [wt %]

        return NaCl_concentration

    idx_salinity = specs.addInput("salinity")  # add symbol for a new input condition to the equilibrium problem

    salinity_constraint = rkt.ConstraintEquation()
    salinity_constraint.id = "salinity"  # give some identification name to the constraint
    salinity_constraint.fn = lambda props, w: get_NaCl_concentration(props) - w[idx_salinity]  # the residual function 

    specs.addConstraint(salinity_constraint)

    return specs


class EquilibriumSpecs(rkt.EquilibriumSpecs): 
    def elementConcentration(self, element, units, titrant): 
        def get_element_concentration(props, element, units):
            if units == "ppm": 
                concentration = 1e6 * props.elementMassInPhase(element, "AqueousPhase") / props.phaseProps("AqueousPhase").mass() # [ppm]
            elif units == "molal": 
                aq_props = rkt.AqueousProps(props)
                concentration = aq_props.elementMolality(element) 
            return concentration

        idx_element_conc = specs.addInput(f"{element} concentration")  # add symbol for a new input condition to the equilibrium problem

        element_conc_constraint = rkt.ConstraintEquation()
        element_conc_constraint.id = f"{element} concentration"  # give some identification name to the constraint
        element_conc_constraint.fn = lambda props, w: get_element_concentration(props, element, units) - w[idx_element_conc]  # the residual function 

        self.addConstraint(element_conc_constraint)
        self.openTo(titrant)
    
    def pH(self, titrant): 
        idx_pH = self.addInput("pH")

        pH_constraint = rkt.ConstraintEquation()
        pH_constraint.id = "pH"
        pH_constraint.fn = lambda props, w : w[idx_pH] - rkt.AqueousProps(props).pH()
        self.addConstraint(pH_constraint)
        self.openTo(titrant)

    def electroneutrality(self, titrant): 
        self.charge()
        self.openTo(titrant)


class EquilibriumConditions(rkt.EquilibriumConditions): 
    def elementConcentration(self, element, amount): 
        self.set(f"{element} concentration", amount)
    
    def electroneutrality(self): 
        self.charge(0)