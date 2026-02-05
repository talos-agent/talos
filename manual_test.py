from talos.core.identity import EntropyGenerator, IdentityManager
from talos.geometric_core.core import GeometricIntelligenceCore
from talos.geometric_core.manifold import GeometricManifold


def test_manual():
    print("Testing Identity...")
    entropy, seed = EntropyGenerator.generate_unique_seed("test")
    print(f"Seed generated: {seed[:20]}...")
    identity = IdentityManager(seed_phrase=seed)
    print(f"Arweave key (partial): {identity.get_arweave_key().hex()[:10]}...")

    print("\nTesting Geometric Core...")
    manifold = GeometricManifold(dimension=11)
    core = GeometricIntelligenceCore(manifold=manifold)
    res = core.process("Test concept")
    print(f"Insights: {res['insights']}")

    val = core.validate_safety()
    print(f"Validation: {[v.passed for v in val]}")


if __name__ == "__main__":
    test_manual()
