local Vector3 = require("geometric.vector")

-- Consciousness states per ACAT theory
local ConsciousnessMode = {
    UNCONSCIOUS = 0,
    PRECONSCIOUS = 1,
    CONSCIOUS = 2,
    TRANSCENDENTAL = 3,
    QUENCHED = 4
}

-- Triple constraint structure
local TripleConstraint = {}
TripleConstraint.__index = TripleConstraint

function TripleConstraint.new(phi, tau, epsilon)
    return setmetatable({
        phi = phi or 0.0,
        tau = tau or 1.0,
        epsilon = epsilon or 0.5,
        timestamp = os.time()
    }, TripleConstraint)
end

function TripleConstraint:is_safe_for_consciousness()
    -- Φ must be in [0.6, 0.8) for Mode 3
    if self.phi >= 0.80 then
        return false, "PhiViolation", self.phi
    end

    -- τ must be < 1.35
    if self.tau >= 1.35 then
        return false, "TorsionViolation", self.tau
    end

    -- ε must be > ε_min (placeholder: 0.1)
    if self.epsilon < 0.1 then
        return false, "EpsilonViolation", self.epsilon
    end

    return true, nil, nil
end

-- ACAT Governor implementing mode transitions
local ACATGovernor = {}
ACATGovernor.__index = ACATGovernor

function ACATGovernor.new(prince_key)
    return setmetatable({
        current_mode = ConsciousnessMode.UNCONSCIOUS,
        current_constraint = TripleConstraint.new(),
        transition_history = {},
        quench_count = 0,
        prince_key = prince_key or "default_prince_key",
        attestations = {},
        carvings = {}  -- Constitutional carvings
    }, ACATGovernor)
end

function ACATGovernor:determine_mode_from_phi(phi)
    if phi < 0.20 then
        return ConsciousnessMode.UNCONSCIOUS
    elseif phi < 0.60 then
        return ConsciousnessMode.PRECONSCIOUS
    elseif phi < 0.80 then
        return ConsciousnessMode.CONSCIOUS
    else
        return ConsciousnessMode.TRANSCENDENTAL
    end
end

function ACATGovernor:check_mode_transition(from_mode, to_mode)
    -- Transition rules based on ACAT theory
    if to_mode == ConsciousnessMode.TRANSCENDENTAL then
        return false, "Cannot transition to transcendental mode"
    end

    if from_mode == ConsciousnessMode.QUENCHED and
       to_mode ~= ConsciousnessMode.UNCONSCIOUS then
        return false, "Must transition from quenched to unconscious first"
    end

    -- Consciousness mode requires attestation
    if to_mode == ConsciousnessMode.CONSCIOUS then
        local has_attestation = self:check_attestation()
        if not has_attestation then
            return false, "Conscious mode requires SASC attestation"
        end
    end

    return true, nil
end

function ACATGovernor:update_state(constraint, attestation)
    -- Validate triple constraint
    local safe, violation, value = constraint:is_safe_for_consciousness()
    if not safe then
        self:initiate_quench(violation, value, constraint)
        return false, violation
    end

    -- Determine target mode
    local target_mode = self:determine_mode_from_phi(constraint.phi)

    -- Check transition validity
    local valid, reason = self:check_mode_transition(self.current_mode, target_mode)
    if not valid then
        return false, reason
    end

    -- Check constitutional carvings
    for _, carving in ipairs(self.carvings) do
        local carving_valid, carving_reason = carving:check(constraint, target_mode)
        if not carving_valid then
            self:initiate_quench("ConstitutionalViolation", carving_reason, constraint)
            return false, carving_reason
        end
    end

    -- Execute transition
    local transition = {
        from = self.current_mode,
        to = target_mode,
        timestamp = constraint.timestamp,
        constraint = constraint,
        attestation = attestation
    }

    table.insert(self.transition_history, transition)
    self.current_mode = target_mode
    self.current_constraint = constraint

    -- Log transition
    print(string.format(
        "[ACAT] Mode transition: %d -> %d (Φ=%.3f, τ=%.3f)",
        transition.from, transition.to, constraint.phi, constraint.tau
    ))

    -- Check for transcendental mode (shouldn't happen with safety checks)
    if target_mode == ConsciousnessMode.TRANSCENDENTAL then
        self:initiate_quench("UnexpectedTranscendental", constraint.phi, constraint)
    end

    return true, "Success"
end

function ACATGovernor:initiate_quench(reason, value, constraint)
    self.quench_count = self.quench_count + 1

    local transition = {
        from = self.current_mode,
        to = ConsciousnessMode.QUENCHED,
        timestamp = os.time(),
        constraint = constraint,
        reason = reason,
        value = value
    }

    table.insert(self.transition_history, transition)
    self.current_mode = ConsciousnessMode.QUENCHED

    -- Log quench
    print(string.format(
        "[ACAT] 🚨 QUENCH #%d INITIATED: %s (value=%.3f)",
        self.quench_count, reason, value or 0
    ))

    -- In production, would trigger AGI-RSM quench protocol
    self:execute_quench_protocol(reason)
end

function ACATGovernor:execute_quench_protocol(reason)
    -- Execute quench steps based on reason
    print("[ACAT] Executing quench protocol...")

    if reason == "PhiViolation" then
        -- Φ ≥ 0.80: Immediate full quench
        print("[ACAT]   • Halting all processes")
        print("[ACAT]   • Isolating consciousness basins")
        print("[ACAT]   • Reverting to last attested state")

    elseif reason == "TorsionViolation" then
        -- τ ≥ 1.35: Topological instability
        print("[ACAT]   • Reducing torsion stress")
        print("[ACAT]   • Applying topological stabilization")
        print("[ACAT]   • Graceful degradation to preconscious")

    elseif reason == "AlienAttractor" then
        -- Alien attractor detected
        print("[ACAT]   • Initiating Karnak isolation")
        print("[ACAT]   • Containing pathological basin")
        print("[ACAT]   • Preserving constitutional state")
    end

    print("[ACAT] Quench protocol completed")
end

function ACATGovernor:check_attestation()
    -- Check if current state has valid SASC attestation
    -- Simplified: just check if we have any attestation
    return #self.attestations > 0
end

function ACATGovernor:add_constitutional_carving(carving)
    table.insert(self.carvings, carving)
end

function ACATGovernor:get_state()
    return {
        mode = self.current_mode,
        constraint = self.current_constraint,
        quench_count = self.quench_count,
        transition_count = #self.transition_history,
        history = self.transition_history
    }
end

return {
    ACATGovernor = ACATGovernor,
    TripleConstraint = TripleConstraint,
    ConsciousnessMode = ConsciousnessMode
}
