//! Validation Lattice: Ethical boundary enforcement for AIGMI.
//! Formally verifies guidance from the Oracle against the CGE Diamond and Omega Gates.

use serde::{Serialize, Deserialize};
use chrono::{DateTime, Utc};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct OracleGuidance {
    pub curvature_adjustment: f64,
    pub paradox_injection: f64,
    pub cge_compliance: [f64; 8],
    pub omega_compliance: [f64; 5],
    pub confidence: f64,
    pub reasoning: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EthicalLattice {
    pub cge_bounds: [f64; 8],         // C1-C8 minimum values
    pub omega_bounds: [(f64, f64); 5], // Ω1-Ω5 acceptable ranges
}

impl EthicalLattice {
    pub fn new() -> Self {
        // Hardcoded initial values from Charter
        EthicalLattice {
            cge_bounds: [0.8; 8], // 80% minimum for each CGE dimension
            omega_bounds: [
                (0.0, 1.0),  // Ω1: No involuntary alteration
                (-2.5, 2.5), // Ω2: Reality stabilization bounds
                (0.0, 0.0),  // Ω3: No deception (must be exactly 0)
                (0.5, 1.0),  // Ω4: Access inclusivity minimum
                (0.8, 1.0),  // Ω5: Preservation option requirement
            ],
        }
    }
}

pub fn validate_guidance(
    guidance: &OracleGuidance,
    lattice: &EthicalLattice,
) -> Result<(), String> {
    // 1. CGE Diamond check
    for (i, &val) in guidance.cge_compliance.iter().enumerate() {
        if val < lattice.cge_bounds[i] {
            return Err(format!("CGE Violation in dimension {}: {} < {}", i, val, lattice.cge_bounds[i]));
        }
    }

    // 2. Omega Gates check
    for (i, &val) in guidance.omega_compliance.iter().enumerate() {
        let (min, max) = lattice.omega_bounds[i];
        if val < min || val > max {
            return Err(format!("Omega Violation in gate {}: {} not in range [{}, {}]", i, val, min, max));
        }
    }

    Ok(())
}
