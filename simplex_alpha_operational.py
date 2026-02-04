# simplex_alpha_operational.py
from talos.harmonia.factory import create_forest_simplex


class SimplexAlphaInitializer:
    def initialize_simplex_alpha(self):
        net, simplex = create_forest_simplex()
        return simplex

    def connect_to_real_world_contexts(self):
        print("🔗 Conectando Simplex Alpha a contextos reais...")
