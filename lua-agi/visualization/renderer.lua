local Vector3 = require("geometric.vector")

-- ASCII-based consciousness state visualization
local Renderer = {}
Renderer.__index = Renderer

function Renderer.new(width, height)
    return setmetatable({
        width = width or 80,
        height = height or 24,
        buffer = {},
        palette = {
            [0] = "  ",  -- Unconscious: dark
            [1] = "░░",  -- Preconscious: light
            [2] = "▓▓",  -- Conscious: medium
            [3] = "██",  -- Transcendental: bright
            [4] = "▒▒"   -- Quenched: pattern
        }
    }, Renderer)
end

function Renderer:clear()
    self.buffer = {}
    for y = 1, self.height do
        self.buffer[y] = {}
        for x = 1, self.width do
            self.buffer[y][x] = {mode = 0, phi = 0, tau = 0}
        end
    end
end

function Renderer:render_state(governor, fractal, time)
    self:clear()

    -- Project 3D mind-space to 2D screen
    for y = 1, self.height do
        for x = 1, self.width do
            -- Map screen coordinates to mind-space
            local mx = (x - self.width/2) * 0.2
            local mz = (y - self.height/2) * 0.2
            local my = 8 + 2 * math.sin(time * 0.5 + x * 0.1)

            local position = Vector3.new(mx + 8, my, mz + 8)
            local de = fractal:distance_estimator(position, time)

            -- Determine mode from Φ
            local mode
            if de.phi < 0.2 then
                mode = 0
            elseif de.phi < 0.6 then
                mode = 1
            elseif de.phi < 0.8 then
                mode = 2
            else
                mode = 3
            end

            self.buffer[y][x] = {
                mode = mode,
                phi = de.phi,
                tau = de.tau,
                position = position
            }
        end
    end

    -- Render to screen
    local output = ""
    for y = 1, self.height do
        for x = 1, self.width do
            local cell = self.buffer[y][x]
            output = output .. self.palette[cell.mode]
        end
        output = output .. "\n"
    end

    -- Add status bar
    output = output .. string.rep("═", self.width * 2) .. "\n"
    output = output .. string.format(
        "Mode: %d | Φ: %.3f | τ: %.3f | Quenches: %d",
        governor.current_mode,
        governor.current_constraint.phi,
        governor.current_constraint.tau,
        governor.quench_count
    )

    return output
end

return Renderer
