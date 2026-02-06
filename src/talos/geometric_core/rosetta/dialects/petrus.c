#include <math.h>

typedef struct {
    char* id;
    double phase_angle; // Ângulo de Bragg
} PetrusNode;

// A física bruta da interferência
double calculate_interference(PetrusNode a, PetrusNode b) {
    double delta_phi = fabs(a.phase_angle - b.phase_angle);
    // I = |A|^2 + |B|^2 + 2|A||B|cos(Δφ), assumindo amplitude unitária
    return 2.0 + 2.0 * cos(delta_phi);
}
