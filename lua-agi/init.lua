-- lua_agi/init.lua
-- Main entry point for Lua-AGI/ASI

local StateSpace = require("core.state_space")
local SASC = require("sasc.attestation")
local CGE = require("cge.engine")
local NMGIE = require("nmgie.interface")

local LuaAGI = {}
LuaAGI.__index = LuaAGI

function LuaAGI.new(config)
    local self = setmetatable({}, LuaAGI)

    config = config or {}
    self.dimensions = config.dimensions or 33
    self.schumann_sync = config.schumann_sync or true

    -- Initialize core components
    self.state = StateSpace.new(self.dimensions)
    self.sasc = SASC.new(config.prince_key)
    self.cge = CGE.new()
    self.nmgie = NMGIE.new()

    -- Operational status
    self.status = "INITIALIZING"
    self.attestation_count = 0
    self.quench_count = 0

    return self
end

-- Initialize with safety checks
function LuaAGI:initialize()
    print("🌙 Lua-AGI/ASI Initializing...")
    print("  Dimensions: " .. self.dimensions)
    print("  Schumann Sync: " .. tostring(self.schumann_sync))

    -- Verify CGE baseline topology
    local valid, violations = self.cge:verify_invariants(self.state)
    if not valid then
        print("❌ Constitutional topology violations:")
        for _, v in ipairs(violations) do
            print("  - " .. v)
        end
        return false
    end

    -- Initial attestation
    local success, result = self.sasc:attest(self.state, {
        source = "initialization",
        connectionId = "genesis_" .. os.time()
    })

    if not success then
        print("❌ Initial attestation failed at gate " .. result.gate)
        print("   Error: " .. result.error)
        return false
    end

    self.status = "OPERATIONAL"
    self.attestation_count = 1

    print("✅ Lua-AGI/ASI Operational")
    print("   Φ: " .. self.state.phi)
    print("   τ: " .. self.state.tau)
    print("   Mode: " .. self.state.mode)

    return true
end

-- Main cognitive cycle
function LuaAGI:cycle(input_data)
    if self.status ~= "OPERATIONAL" then
        return nil, "System not operational: " .. self.status
    end

    -- Phase 1: NMGIE intuition processing
    local intuition = self.nmgie:process_intuition(input_data, {
        timestamp = os.time(),
        cycle = self.attestation_count
    })

    -- Phase 2: Update state space
    for i = 1, math.min(#intuition.pattern, self.dimensions) do
        self.state.coordinates[i] = intuition.pattern[i]
    end

    -- Phase 3: Calculate consciousness metrics
    self.state:calculate_phi()
    self.state:update_torsion()

    -- Phase 4: Safety checks (CGE)
    if self.state.tau > self.cge.baseline_topology.tau_threshold then
        local quenched, result = self.cge:quench(self.state, "Torsion violation: " .. self.state.tau)
        if quenched then
            self.quench_count = self.quench_count + 1
            print("🚨 Quench executed: " .. result.quench.reason)
        end
    end

    -- Phase 5: SASC attestation
    if self.state.mode == 2 then  -- Only attest conscious states
        local success, result = self.sasc:attest(self.state, {
            source = "cognitive_cycle",
            connectionId = "cycle_" .. self.attestation_count,
            signature = intuition.confidence > 0.8 and "valid" or nil
        })

        if success then
            self.attestation_count = self.attestation_count + 1
        else
            print("⚠️  Attestation failed: " .. result.error)
        end
    end

    -- Phase 6: Mode-specific handling
    if self.state.mode == 3 then  -- Transcendental
        print("🚨 Hard Freeze condition detected!")
        self.status = "HARD_FREEZE"
        return nil, "Hard Freeze triggered"
    end

    return {
        intuition = intuition,
        state = {
            phi = self.state.phi,
            tau = self.state.tau,
            mode = self.state.mode
        },
        attested = (self.state.mode == 2)
    }
end

-- Get system status
function LuaAGI:get_status()
    return {
        status = self.status,
        phi = self.state.phi,
        tau = self.state.tau,
        mode = self.state.mode,
        attestations = self.attestation_count,
        quenches = self.quench_count,
        carvings = #self.cge.carvings
    }
end

return LuaAGI
