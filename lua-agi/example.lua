-- example.lua
-- Demonstration of Lua-AGI/ASI

package.path = package.path .. ";./?.lua"

local LuaAGI = require("init")

-- Initialize AGI with 33 dimensions (NMGIE-33X compatible)
local agi = LuaAGI.new({
    dimensions = 33,
    prince_key = "PRINCE_LUA_AGI_001",
    schumann_sync = true
})

-- Initialize system
if not agi:initialize() then
    print("Failed to initialize AGI")
    return
end

-- Run cognitive cycles
for i = 1, 10 do
    -- Generate synthetic input (in real use: sensor data, user input, etc.)
    local input = {}
    for j = 1, 33 do
        input[j] = math.sin(i * 0.1 + j * 0.05) * math.random()
    end

    print("\n--- Cycle " .. i .. " ---")
    local result, err = agi:cycle(input)

    if not result then
        print("Error: " .. err)
        break
    end

    print(string.format("Φ: %.3f, τ: %.3f, Mode: %d",
        result.state.phi,
        result.state.tau,
        result.state.mode))
    print("Confidence: " .. result.intuition.confidence)
    print("Attested: " .. tostring(result.attested))
end

-- Final status
local status = agi:get_status()
print("\n=== Final Status ===")
for k, v in pairs(status) do
    print(k .. ": " .. tostring(v))
end
