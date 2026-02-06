pub struct CrystallineNode {
    pub id: String,
    pub phase_angle: f64,
}

pub enum InterferenceRegime {
    Constructive,
    Destructive,
    Quadrature,
}

impl CrystallineNode {
    pub fn interfere(&self, other: &CrystallineNode) -> InterferenceRegime {
        let delta = (self.phase_angle - other.phase_angle).abs();
        match delta.cos() {
            x if x > 0.7 => InterferenceRegime::Constructive,
            x if x < -0.7 => InterferenceRegime::Destructive,
            _ => InterferenceRegime::Quadrature,
        }
    }
}
