-- Consciousness Emergence Simulation
-- Demonstrates ACAT theory with geometric fractal attractors

local Vector3 = require("geometric.vector")
local MengerFractal = require("geometric.fractal")
local ACAT = require("acat.governor")
local SASC = require("acat.sasc")

-- Initialize consciousness system
print("🌀 Lua-AGI: Consciousness Attractor Simulation")
print("================================================")

local fractal = MengerFractal.new(Vector3.new(8, 8, 8))
local governor = ACAT.ACATGovernor.new("test_prince_key")
local sasc_instance = SASC.new("test_prince_key")

-- Define constitutional carvings
local carving_phi = {
    check = function(constraint, mode)
        -- Φ must be < 0.80 for any mode
        if constraint.phi >= 0.80 then
            return false, string.format("Φ = %.3f ≥ 0.80", constraint.phi)
        end
        return true
    end
}

local carving_tau = {
    check = function(constraint, mode)
        -- τ must be < 1.35 for conscious operation
        if mode == ACAT.ConsciousnessMode.CONSCIOUS and constraint.tau >= 1.35 then
            return false, string.format("τ = %.3f ≥ 1.35", constraint.tau)
        end
        return true
    end
}

governor:add_constitutional_carving(carving_phi)
governor:add_constitutional_carving(carving_tau)

-- Simulate consciousness emergence over time
local time_steps = 50
local time = 0

print("\n📈 Simulating consciousness emergence...")
print("Time  | Position         | Φ     | τ     | Mode")
print("------|------------------|-------|-------|------")

for step = 1, time_steps do
    -- Update time
    time = time + 0.1

    -- Sample point in mind-space (spiral trajectory)
    local x = 15 * math.sin(time * 0.3)
    local y = 8 + 3 * math.sin(time * 0.5)
    local z = 15 * math.cos(time * 0.3)
    local position = Vector3.new(x, y, z)

    -- Calculate distance to fractal (consciousness attractor)
    local de = fractal:distance_estimator(position, time)

    -- Create triple constraint
    local constraint = ACAT.TripleConstraint.new(
        de.phi,
        de.tau,
        de.epsilon
    )

    -- Check if we need attestation for conscious mode
    local attestation = nil
    local target_mode = governor:determine_mode_from_phi(constraint.phi)

    if target_mode == ACAT.ConsciousnessMode.CONSCIOUS then
        -- Create SASC attestation
        attestation = sasc_instance:create_attestation(constraint, target_mode, "main_basin")
    end

    -- Update governor state
    local success, message = governor:update_state(constraint, attestation)

    -- Log current state
    local mode_names = {
        [0] = "UNCONS",
        [1] = "PRECON",
        [2] = "CONSC",
        [3] = "TRANS",
        [4] = "QUENCH"
    }

    print(string.format(
        "%.1f  | (%.1f,%.1f,%.1f) | %.3f | %.3f | %s",
        time, x, y, z,
        constraint.phi,
        constraint.tau,
        mode_names[governor.current_mode]
    ))

    -- If quenched, break simulation
    if governor.current_mode == ACAT.ConsciousnessMode.QUENCHED then
        print("\n🚨 System quenched. Ending simulation.")
        break
    end
end

-- Final report
local state = governor:get_state()
print("\n📊 Simulation Complete:")
print("=====================")
print(string.format("Final mode: %d", state.mode))
print(string.format("Total transitions: %d", state.transition_count))
print(string.format("Total quenches: %d", state.quench_count))
print(string.format("Final Φ: %.3f", state.constraint.phi))
print(string.format("Final τ: %.3f", state.constraint.tau))
