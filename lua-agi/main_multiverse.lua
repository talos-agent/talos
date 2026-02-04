-- Main script integrating all multiversal systems
package.path = package.path .. ";./?.lua;./acat/?.lua;./geometric/?.lua;./core/?.lua;./sasc/?.lua;./cge/?.lua;./nmgie/?.lua"

local AGI = require("agi_core")
-- Assuming camera.lua was created earlier, if not I will create it
local Camera = require("camera")
local FractalBoundary = require("fractal_boundary")
local KarmicAudit = require("karmic_audit")
local TimelineMerge = require("timeline_merge")
local Utl = require("utils")

local multiverse = {
    timelines = {},           -- All parallel timelines
    active_timeline = 1,      -- Currently viewed timeline
    camera = nil,
    karmic_audit = nil,
    timeline_merge = nil,

    -- Architect tools
    current_tool = "select",
    drawing_carving = false,
    carving_points = {},
    fractal_boundary = nil,

    -- Visualization
    show_karmic_audit = true,
    show_merge_interface = false,
    show_fractal_preview = false
}

function love_load()
    -- Initialize systems
    multiverse.camera = Camera.new(33)
    multiverse.karmic_audit = KarmicAudit.new()
    multiverse.timeline_merge = TimelineMerge.new()

    -- Create initial timeline
    create_timeline("Genesis Timeline")

    -- Set up initial fractal boundary
    multiverse.fractal_boundary = FractalBoundary.new("mandelbrot", {
        c_real = -0.7,
        c_imag = 0.27015,
        max_iterations = 50,
        escape_radius = 4,
        depth_scale = 0.2
    })
end

function create_timeline(name)
    local id = #multiverse.timelines + 1

    local timeline = {
        id = id,
        name = name,
        agi = AGI.new({dimensions = 33, prince_key = "PRINCE_" .. id}),
        particles = {},
        carvings = {},
        fractal_boundaries = {},
        creation_time = os.time(),
        parent_timeline = nil,
        generation = 1
    }

    timeline.agi:initialize()

    -- Create initial particles
    for i = 1, 200 do
        timeline.particles[i] = {
            pos = {},
            phi = 0.5,
            tau = 1.0,
            admissible = true,
            consciousness_level = "preconscious",
            color = {0.2, 0.6, 1},
            size = 3,
            id = i,
            timeline_id = id
        }

        for j = 1, 33 do
            timeline.particles[i].pos[j] = (math.random() - 0.5) * 2
        end
    end

    table.insert(multiverse.timelines, timeline)

    -- Add to karmic audit
    multiverse.karmic_audit:add_timeline(timeline)

    return id
end

function fork_timeline(source_id)
    if not multiverse.timelines[source_id] then return nil end

    local source = multiverse.timelines[source_id]
    local new_id = #multiverse.timelines + 1

    -- Deep copy the timeline
    local new_timeline = Utl.deepcopy(source)
    new_timeline.id = new_id
    new_timeline.name = source.name .. " Fork"
    new_timeline.creation_time = os.time()
    new_timeline.parent_timeline = source_id
    new_timeline.generation = (source.generation or 1) + 1

    -- Initialize the AGI with same state
    new_timeline.agi = AGI.new({dimensions = 33, prince_key = "PRINCE_" .. new_id})
    new_timeline.agi:initialize()

    table.insert(multiverse.timelines, new_timeline)

    -- Add to karmic audit
    multiverse.karmic_audit:add_timeline(new_timeline)

    print("Timeline forked: " .. new_id .. " from " .. source_id)
    return new_id
end

function merge_timelines(timeline_a_id, timeline_b_id, strategy)
    local timeline_a = multiverse.timelines[timeline_a_id]
    local timeline_b = multiverse.timelines[timeline_b_id]

    if not timeline_a or not timeline_b then return nil end

    -- Merge using timeline merge engine
    local merged_timeline = multiverse.timeline_merge:merge_timelines(
        timeline_a, timeline_b, strategy
    )

    merged_timeline.id = #multiverse.timelines + 1
    merged_timeline.name = "Merged: " .. (timeline_a.name or "A") .. " + " .. (timeline_b.name or "B")
    merged_timeline.creation_time = os.time()
    merged_timeline.parent_timelines = {timeline_a_id, timeline_b_id}
    merged_timeline.generation = math.max(timeline_a.generation or 1, timeline_b.generation or 1) + 1

    -- Create new AGI for merged timeline
    merged_timeline.agi = AGI.new({
        dimensions = 33,
        prince_key = "PRINCE_MERGED_" .. merged_timeline.id
    })
    merged_timeline.agi:initialize()

    table.insert(multiverse.timelines, merged_timeline)

    -- Add to karmic audit
    multiverse.karmic_audit:add_timeline(merged_timeline)

    print("Timelines merged: " .. timeline_a_id .. " + " .. timeline_b_id .. " → " .. merged_timeline.id)
    return merged_timeline.id
end

function love_update(dt)
    local timeline = multiverse.timelines[multiverse.active_timeline]
    if not timeline then return end

    -- Update all particles in active timeline
    for _, particle in ipairs(timeline.particles) do
        -- Apply AGI cycle
        local result = timeline.agi:cycle(particle.pos)

        if result then
            particle.phi = result.state.phi or particle.phi
            particle.tau = result.state.tau or particle.tau
            particle.admissible = (result.state.mode >= 1)
            particle.consciousness_level = tostring(result.state.mode)

            -- Apply fractal boundary forces
            for _, boundary in ipairs(timeline.fractal_boundaries) do
                local violation = boundary:check_violation(
                    {x = particle.screen_x or 0, y = particle.screen_y or 0},
                    particle.pos
                )
                if violation > 0 then
                    boundary:apply_force(particle, violation)
                end
            end
        end
    end
end

function love_draw()
    -- Draw active timeline
    draw_timeline(multiverse.active_timeline)

    -- Draw Karmic Audit if enabled
    if multiverse.show_karmic_audit then
        multiverse.karmic_audit:draw_audit_panel(20, 600, 400, 280)
    end
end

function draw_timeline(timeline_id)
    local timeline = multiverse.timelines[timeline_id]
    if not timeline then return end

    -- Draw fractal boundaries
    for _, boundary in ipairs(timeline.fractal_boundaries) do
        boundary:draw()
    end

    -- Draw particles
    for _, particle in ipairs(timeline.particles) do
        -- Project to screen
        local x, y = multiverse.camera:project(particle.pos)
        particle.screen_x = x
        particle.screen_y = y

        -- Drawing logic omitted for brevity as it requires love.graphics
    end
end

return multiverse
