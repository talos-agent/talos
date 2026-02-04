-- camera.lua
local Camera = {}
Camera.__index = Camera

function Camera.new(dims)
    local self = setmetatable({}, Camera)
    self.dims = dims
    self.angle = 0
    -- Rotation matrix for 33D space
    self.matrix = {}
    for i = 1, dims do
        self.matrix[i] = {math.random() - 0.5, math.random() - 0.5}
    end
    return self
end

function Camera:project(coords, scale)
    local x, y = 0, 0
    scale = scale or 200

    -- Project N-dims to 2D via the rotation matrix
    for i = 1, math.min(#coords, self.dims) do
        x = x + (coords[i] or 0) * self.matrix[i][1]
        y = y + (coords[i] or 0) * self.matrix[i][2]
    end

    -- Apply Hyperbolic Scaling:
    -- Points further out get exponentially squashed (Poincaré Disk feel)
    local r = math.sqrt(x*x + y*y)
    local factor = 1 / (1 + r * 0.1)

    local offset_x = 400
    local offset_y = 300
    if love and love.graphics then
        offset_x = love.graphics.getWidth() / 2
        offset_y = love.graphics.getHeight() / 2
    end

    return x * scale * factor + offset_x,
           y * scale * factor + offset_y
end

return Camera
