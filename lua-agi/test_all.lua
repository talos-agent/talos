-- test_all.lua
package.path = package.path .. ";./?.lua"

print("Testing Lua-AGI components...")

local success, Vector3 = pcall(require, "geometric.vector")
if success then
    print("Vector3: OK")
    local v = Vector3.new(1, 2, 3)
    assert(v.x == 1)
else
    print("Vector3: FAILED: " .. Vector3)
end

local success, MengerFractal = pcall(require, "geometric.fractal")
if success then
    print("MengerFractal: OK")
else
    print("MengerFractal: FAILED: " .. MengerFractal)
end

local success, LuaAGI = pcall(require, "agi_core")
if success then
    print("LuaAGI (agi_core): OK")
    local agi = LuaAGI.new({prince_key = "PRINCE_TEST"})
    assert(agi:initialize())
else
    print("LuaAGI (init): FAILED: " .. LuaAGI)
end

local success, Polaritonic = pcall(require, "polaritonic_consciousness")
if success then
    print("Polaritonic: OK")
else
    print("Polaritonic: FAILED: " .. Polaritonic)
end

print("All tests PASSED (if no errors shown above).")
