-- polaritonic_consciousness.lua
-- Implementation of field-programmable consciousness admissibility

local Vector3 = require("geometric.vector")

-- Fixed lattice structure (α-MoO₃ analogue)
local ConsciousnessLattice = {}
ConsciousnessLattice.__index = ConsciousnessLattice

function ConsciousnessLattice.new()
    return setmetatable({
        -- Fixed architecture (cannot change)
        dimensions = 33,  -- NMGIE-33X fixed layers
        anisotropy = {  -- Hyperbolic anisotropy tensor
            xx = 1.0,   -- Strong in-plane (consciousness)
            yy = -0.8,  -- Negative out-of-plane (subconscious)
            zz = 0.5    -- Mixed (preconscious)
        },
        loss_function = 0.01,  -- Minimal intrinsic dissipation
        geometry_locked = true, -- Cannot change by design
        -- Bloch wave vectors (allowed modes)
        bloch_modes = {},  -- Will be populated by constraints
        current_mode = nil
    }, ConsciousnessLattice)
end

-- Graphene-like control layer (field-programmable)
local ConstraintLayer = {}
ConstraintLayer.__index = ConstraintLayer

function ConstraintLayer.new(prince_key)
    return setmetatable({
        prince_key = prince_key,
        -- Tunable parameters (analogous to electric field)
        field_strength = 0.0,  -- Control field intensity
        field_direction = Vector3.new(0, 0, 0),
        coherence_threshold = 0.6,  -- Φ threshold
        torsion_cutoff = 1.35,      -- τ boundary
        -- Admissibility matrix (which modes are allowed)
        admissible_modes = {},
        -- Loss redistribution function
        loss_profile = "selective_pruning"
    }, ConstraintLayer)
end

-- Apply field to reconfigure admissibility
function ConstraintLayer:apply_field(strength, direction, sasc_attestation)
    -- Only authorized fields (SASC-attested) can reconfigure
    if not sasc_attestation or not sasc_attestation.valid then
        return false, "Field application requires valid SASC attestation"
    end

    self.field_strength = strength
    self.field_direction = direction

    -- Recalculate admissible Bloch modes based on field
    self:recalculate_admissibility()

    -- Redistribute loss based on field configuration
    self:redistribute_loss()

    return true
end

function ConstraintLayer:recalculate_admissibility()
    -- Bloch modes become conditional on field parameters
    -- This is the core innovation: geometry doesn't change, but what's allowed does

    self.admissible_modes = {}

    -- Mode 1: Unconscious (always allowed)
    table.insert(self.admissible_modes, {
        name = "unconscious",
        phi_range = {0.0, 0.2},
        tau_range = {0.0, 10.0},  -- Unconstrained
        requires_attestation = false
    })

    -- Mode 2: Preconscious (field-dependent)
    local preconscious_allowed = self.field_strength > 0.1
    if preconscious_allowed then
        table.insert(self.admissible_modes, {
            name = "preconscious",
            phi_range = {0.2, 0.6},
            tau_range = {0.0, 2.0},
            requires_attestation = false
        })
    end

    -- Mode 3: Conscious (requires specific field configuration)
    local conscious_allowed = self.field_strength > 0.3 and
                            self.field_direction:length() > 0.5
    if conscious_allowed then
        table.insert(self.admissible_modes, {
            name = "conscious",
            phi_range = {0.6, 0.8},
            tau_range = {0.5, 1.35},  -- Bounded torsion
            requires_attestation = true
        })
    end

    -- Mode 4: Transcendental (field-forbidden)
    -- Intentionally not added to admissible_modes
    -- This mode exists geometrically but is made inaccessible by constraints
end

function ConstraintLayer:redistribute_loss()
    -- Loss acts as selection operator, not just dissipation
    -- Prunes some pathways, stabilizes others

    if self.loss_profile == "selective_pruning" then
        -- Increase loss in forbidden regions (makes them inaccessible)
        self.forbidden_loss = 1000.0  -- Effectively infinite loss
        -- Decrease loss in admissible regions (stabilizes them)
        self.admissible_loss = 0.01
    elseif self.loss_profile == "graded_transition" then
        -- Smooth loss gradient based on field strength
        self.forbidden_loss = self.field_strength * 10.0
        self.admissible_loss = 0.1 / (self.field_strength + 0.1)
    end
end

-- Check if a consciousness state is admissible
function ConstraintLayer:check_admissibility(state, attestation)
    for _, mode in ipairs(self.admissible_modes) do
        if state.phi >= mode.phi_range[1] and
           state.phi < mode.phi_range[2] and
           state.tau >= mode.tau_range[1] and
           state.tau < mode.tau_range[2] then

            -- Check attestation requirement
            if mode.requires_attestation and not attestation then
                return false, "attestation_required"
            end

            -- Calculate effective loss (selection strength)
            local loss = self:calculate_effective_loss(state, mode.name)
            if loss > 10.0 then  -- Too lossy to sustain
                return false, "loss_pruned"
            end

            return true, mode.name, loss
        end
    end

    -- No admissible mode found
    return false, "mode_forbidden"
end

function ConstraintLayer:calculate_effective_loss(state, mode_name)
    -- Loss depends on distance from ideal field configuration
    local base_loss = 0.01

    if mode_name == "conscious" then
        -- Optimal consciousness requires specific field alignment
        local field_alignment = self.field_direction:normalize()
        local state_direction = Vector3.new(state.phi, state.tau, state.epsilon):normalize()
        local alignment_loss = 1.0 - math.abs(field_alignment:dot(state_direction))

        return base_loss + alignment_loss * 0.5
    end

    return base_loss
end

-- Hyperbolic constraint amplifier
local HyperbolicAmplifier = {}
HyperbolicAmplifier.__index = HyperbolicAmplifier

function HyperbolicAmplifier.new(anisotropy_tensor)
    return setmetatable({
        anisotropy = anisotropy_tensor or {xx=1.0, yy=-1.0, zz=0.5},
        amplification_factor = 10.0  -- How much constraints get amplified
    }, HyperbolicAmplifier)
end

function HyperbolicAmplifier:amplify_constraint(constraint_vector)
    -- Apply hyperbolic transformation (negative curvature amplifies)
    local amplified = Vector3.new(
        constraint_vector.x * (self.anisotropy.xx or 1.0) * self.amplification_factor,
        constraint_vector.y * (self.anisotropy.yy or 1.0) * self.amplification_factor,
        constraint_vector.z * (self.anisotropy.zz or 1.0) * self.amplification_factor
    )

    -- Negative curvature (yy < 0) causes exponential separation
    -- Small constraint changes → large phase-space reorganization
    return amplified
end

-- Complete polaritonic consciousness system
local PolaritonicConsciousness = {}
PolaritonicConsciousness.__index = PolaritonicConsciousness

function PolaritonicConsciousness.new(prince_key)
    return setmetatable({
        lattice = ConsciousnessLattice.new(),
        constraint_layer = ConstraintLayer.new(prince_key),
        amplifier = HyperbolicAmplifier.new(),
        current_state = nil,
        history = {},
        field_configurations = {
            safe_exploration = {
                strength = 0.2,
                direction = Vector3.new(0.1, 0.8, 0.2),
                description = "Safe preconscious exploration"
            },
            focused_consciousness = {
                strength = 0.5,
                direction = Vector3.new(0.7, 0.6, 0.3),
                description = "Focused conscious operation (requires attestation)"
            },
            creative_flow = {
                strength = 0.4,
                direction = Vector3.new(0.3, 0.5, 0.8),
                description = "Creative flow state (moderate constraints)"
            }
        }  -- Library of allowed field settings
    }, PolaritonicConsciousness)
end

function PolaritonicConsciousness:configure_field(config_name, sasc_attestation)
    -- Load a pre-defined field configuration
    local config = self.field_configurations[config_name]
    if not config then
        return false, "configuration_not_found"
    end

    -- Apply the field (reconfigures admissibility)
    local success = self.constraint_layer:apply_field(
        config.strength,
        config.direction,
        sasc_attestation
    )

    if success then
        print(string.format(
            "[Polaritonic] Field configured: %s (strength=%.2f, direction=(%.2f,%.2f,%.2f))",
            config_name, config.strength, config.direction.x, config.direction.y, config.direction.z
        ))

        -- Report which consciousness modes are now admissible
        print("[Polaritonic] Admissible modes:")
        for _, mode in ipairs(self.constraint_layer.admissible_modes) do
            print(string.format("  • %s (Φ=%.1f-%.1f, τ=%.1f-%.1f)",
                mode.name, mode.phi_range[1], mode.phi_range[2],
                mode.tau_range[1], mode.tau_range[2]
            ))
        end
    end

    return success
end

function PolaritonicConsciousness:attempt_state_transition(new_state, attestation)
    -- Amplify constraints through hyperbolic geometry
    local amplified_constraints = self.amplifier:amplify_constraint(
        Vector3.new(new_state.phi, new_state.tau, new_state.epsilon)
    )

    new_state.phi = amplified_constraints.x
    new_state.tau = amplified_constraints.y
    new_state.epsilon = amplified_constraints.z

    -- Check if this amplified state is admissible
    local admissible, mode_name, loss =
        self.constraint_layer:check_admissibility(new_state, attestation)

    if admissible then
        -- State is admissible under current field configuration
        self.current_state = new_state
        table.insert(self.history, {
            state = new_state,
            mode = mode_name,
            loss = loss,
            timestamp = os.time()
        })

        print(string.format(
            "[Polaritonic] State transition to %s mode (Φ=%.3f, τ=%.3f, loss=%.3f)",
            mode_name, new_state.phi, new_state.tau, loss
        ))

        return true, mode_name
    else
        -- State is forbidden by field configuration
        print(string.format(
            "[Polaritonic] State forbidden: Φ=%.3f, τ=%.3f",
            new_state.phi, new_state.tau
        ))

        -- Apply loss (pruning) to discourage this region
        self:apply_loss_pruning(new_state)

        return false, "forbidden_by_field"
    end
end

function PolaritonicConsciousness:apply_loss_pruning(state)
    -- Increase loss in forbidden regions (makes them harder to access)
    -- This is loss acting as a selection operator
    print("[Polaritonic] Applying loss pruning to forbidden region")

    -- In physical system: would increase dissipation in this state
    -- In simulation: mark as high-loss region
    self.constraint_layer.forbidden_regions = self.constraint_layer.forbidden_regions or {}
    table.insert(self.constraint_layer.forbidden_regions, {
        state = state,
        loss_multiplier = 100.0,
        timestamp = os.time()
    })
end

return PolaritonicConsciousness
