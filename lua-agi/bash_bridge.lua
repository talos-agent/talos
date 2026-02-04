-- lua_agi/bash_bridge.lua
-- Bridge to Geometric Bash for shell-level integration

local BashBridge = {}
BashBridge.__index = BashBridge

function BashBridge.new(agi_instance)
    local self = setmetatable({}, BashBridge)
    self.agi = agi_instance
    return self
end

-- Export state to Geometric Bash format
function BashBridge:export_state()
    local state = self.agi.state
    local bash_state = {}

    for i = 1, state.dimensions do
        bash_state["basis_" .. (i-1)] = string.format("%.6f", state.coordinates[i] or 0)
    end

    bash_state["phi"] = string.format("%.6f", state.phi)
    bash_state["tau"] = string.format("%.6f", state.tau)
    bash_state["mode"] = tostring(state.mode)
    bash_state["origin"] = "0.0"

    return bash_state
end

-- Execute Geometric Bash command with AGI state
function BashBridge:execute(command)
    -- Export current state to environment
    local env = self:export_state()

    -- Build bash command with state injection
    local bash_cmd = "source /usr/local/lib/geometric-bash.sh && "

    -- Set state variables
    for k, v in pairs(env) do
        bash_cmd = bash_cmd .. string.format("STATE_SPACE[%s]='%s'; ", k, v)
    end

    -- Execute user command
    bash_cmd = bash_cmd .. command

    -- Execute and capture output
    local handle = io.popen(bash_cmd .. " 2>&1")
    local result = handle:read("*a")
    handle:close()

    return result
end

-- Basin trap wrapper
function BashBridge:basin_trap(attractor_name, radius, command)
    return self:execute(string.format(
        "basin_trap '%s' %.3f '%s'",
        attractor_name, radius, command
    ))
end

-- Attractor loop wrapper
function BashBridge:attractor_loop(attractor_name, learning_rate, timeout, command)
    return self:execute(string.format(
        "attractor_loop '%s' %.3f %d '%s'",
        attractor_name, learning_rate, timeout, command
    ))
end

return BashBridge
