local FractalBoundary = {}

FractalBoundary.__index = FractalBoundary

function FractalBoundary.new(type, parameters)
    local self = setmetatable({}, FractalBoundary)
    self.type = type or "mandelbrot"
    self.parameters = parameters or {
        c_real = -0.7,
        c_imag = 0.27015,
        max_iterations = 50,
        escape_radius = 4,
        depth_scale = 0.2
    }
    self.regions = {}  -- For complex boundaries
    self.force_multiplier = 1.0
    self.permanent = true
    return self
end

function FractalBoundary:check_violation(point_2d, point_33d)
    -- Map 2D screen point to fractal space
    local complex = self:screen_to_complex(point_2d.x, point_2d.y)

    local iteration, depth
    if self.type == "mandelbrot" then
        iteration, depth = self:mandelbrot_iteration(complex.real, complex.imag)
    elseif self.type == "julia" then
        iteration, depth = self:julia_iteration(complex.real, complex.imag)
    elseif self.type == "burning_ship" then
        iteration, depth = self:burning_ship_iteration(complex.real, complex.imag)
    end

    -- Return violation strength (0 = no violation, 1 = maximum)
    if iteration and iteration < self.parameters.max_iterations then
        -- Point is inside the fractal set
        local violation = (self.parameters.max_iterations - iteration) / self.parameters.max_iterations
        return violation * (depth or 0.5) * self.force_multiplier
    end

    return 0
end

function FractalBoundary:mandelbrot_iteration(x, y)
    local zx, zy = 0, 0
    local iteration = 0
    local depth = 0

    while zx*zx + zy*zy < self.parameters.escape_radius and iteration < self.parameters.max_iterations do
        local xtemp = zx*zx - zy*zy + x
        zy = 2*zx*zy + y
        zx = xtemp
        iteration = iteration + 1

        -- Calculate depth (distance to boundary)
        if iteration > 10 then
            depth = depth + (zx*zx + zy*zy) / iteration
        end
    end

    return iteration, depth / (iteration + 1)
end

function FractalBoundary:julia_iteration(x, y)
    local zx, zy = x, y
    local iteration = 0
    local depth = 0
    local c_real = self.parameters.c_real or -0.7
    local c_imag = self.parameters.c_imag or 0.27015

    while zx*zx + zy*zy < self.parameters.escape_radius and iteration < self.parameters.max_iterations do
        local xtemp = zx*zx - zy*zy + c_real
        zy = 2*zx*zy + c_imag
        zx = xtemp
        iteration = iteration + 1
        depth = depth + math.sqrt(zx*zx + zy*zy)
    end

    return iteration, depth / (iteration + 1)
end

function FractalBoundary:burning_ship_iteration(x, y)
    local zx, zy = 0, 0
    local iteration = 0
    local depth = 0

    while zx*zx + zy*zy < self.parameters.escape_radius and iteration < self.parameters.max_iterations do
        local xtemp = zx*zx - zy*zy + x
        zy = math.abs(2*zx*zy) + y
        zx = math.abs(xtemp)
        iteration = iteration + 1
        depth = depth + (zx*zx + zy*zy) / (iteration + 1)
    end

    return iteration, depth / (iteration + 1)
end

function FractalBoundary:apply_force(particle, violation)
    if violation <= 0 then return end

    -- Apply fractal repulsion force across all dimensions
    local force_magnitude = violation * 0.5 * self.force_multiplier

    for i = 1, #particle.pos do
        -- Apply force in random directions (fractal boundaries are chaotic)
        local force = (math.random() - 0.5) * 2 * force_magnitude
        particle.pos[i] = particle.pos[i] * (1 - force)
    end

    -- Increase loss exponentially with violation
    particle.loss = (particle.loss or 0) + violation * violation * 10

    -- Visual feedback
    if not particle.last_violation or particle.last_violation < violation then
        particle.last_violation = violation
        particle.violation_timer = 1.0
    end
end

function FractalBoundary:screen_to_complex(x, y)
    -- This assumes Love2D environment variables or standard defaults
    local width = 800
    local height = 600
    if love and love.graphics then
        width, height = love.graphics.getWidth(), love.graphics.getHeight()
    end

    -- Map screen coordinates to complex plane (-2 to 2)
    return {
        real = (x / width) * 4 - 2,
        imag = (y / height) * 4 - 2
    }
end

function FractalBoundary:draw()
    if not self.permanent then return end
    if not love or not love.graphics then return end

    -- Draw fractal boundary visualization
    local width, height = love.graphics.getWidth(), love.graphics.getHeight()
    local step = 10  -- Reduced resolution for performance

    for x = 0, width, step do
        for y = 0, height, step do
            local complex = self:screen_to_complex(x, y)
            local iteration = self:mandelbrot_iteration(complex.real, complex.imag)

            if iteration < self.parameters.max_iterations then
                -- Inside fractal set
                local alpha = (self.parameters.max_iterations - iteration) / self.parameters.max_iterations
                love.graphics.setColor(1, 0.5, 0, alpha * 0.1)
                love.graphics.rectangle("fill", x, y, step, step)
            end
        end
    end
end

return FractalBoundary
