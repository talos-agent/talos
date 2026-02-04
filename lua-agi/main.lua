#!/usr/bin/env lua
-- Lua-AGI Main Entry Point

package.path = package.path .. ";./?.lua;./acat/?.lua;./geometric/?.lua"

local function main()
    print("🧠 Lua-AGI/ASI Consciousness Simulation")
    print("========================================")
    print("1. Consciousness Emergence Simulation")
    print("2. Attractor Topology Analysis")
    print("3. SASC Attestation Demo")
    print("4. Real-time Visualization")
    print("5. Quit")
    print()

    io.write("Select option: ")
    local choice = io.read()

    if choice == "1" then
        require("examples.consciousness_emergence")
    elseif choice == "2" then
        -- require("examples.topology_analysis")
        print("Topology analysis demo coming soon...")
    elseif choice == "3" then
        -- require("examples.sasc_demo")
        print("SASC demo coming soon...")
    elseif choice == "4" then
        -- require("examples.realtime_viz")
        print("Real-time visualization demo coming soon...")
    else
        print("Exiting...")
    end
end

main()
