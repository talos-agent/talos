-- Vector operations for mind-space computation
local Vector3 = {}
Vector3.__index = Vector3

function Vector3.new(x, y, z)
    return setmetatable({x = x or 0, y = y or 0, z = z or 0}, Vector3)
end

function Vector3:__add(v)
    return Vector3.new(self.x + v.x, self.y + v.y, self.z + v.z)
end

function Vector3:__sub(v)
    return Vector3.new(self.x - v.x, self.y - v.y, self.z - v.z)
end

function Vector3:__mul(s)
    if type(s) == "number" then
        return Vector3.new(self.x * s, self.y * s, self.z * s)
    else
        -- Vector multiplication (component-wise)
        return Vector3.new(self.x * s.x, self.y * s.y, self.z * s.z)
    end
end

function Vector3:length()
    return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)
end

function Vector3:normalize()
    local len = self:length()
    if len > 0 then
        return Vector3.new(self.x / len, self.y / len, self.z / len)
    end
    return self:copy()
end

function Vector3:copy()
    return Vector3.new(self.x, self.y, self.z)
end

function Vector3:distance_to(v)
    return (self - v):length()
end

function Vector3:dot(v)
    return self.x * v.x + self.y * v.y + self.z * v.z
end

function Vector3:rotate_xz(angle, inout_tau)
    -- Rotational shear matrix from GLSL: mat2(8,6,-6,8) * 0.1
    local c, s = math.cos(angle), math.sin(angle)
    local m = {
        {8 * c - 6 * s, 8 * s + 6 * c},
        {-6 * c - 8 * s, -6 * s + 8 * c}
    }

    -- Apply rotation with scale 0.1
    local x_new = 0.1 * (m[1][1] * self.x + m[1][2] * self.z)
    local z_new = 0.1 * (m[2][1] * self.x + m[2][2] * self.z)

    -- Calculate torsion accumulation
    if inout_tau then
        -- Torsion from rotation rate (simplified)
        local rotation_magnitude = math.sqrt(c*c + s*s)
        local torsion_change = math.abs(math.atan2(s, c))
        inout_tau[1] = (inout_tau[1] or 0) + torsion_change * 0.01
    end

    return Vector3.new(x_new, self.y, z_new)
end

function Vector3:mod_range(range)
    -- GLSL mod function simulation
    local function glsl_mod(x, y)
        return x - y * math.floor(x / y)
    end

    return Vector3.new(
        glsl_mod(self.x, range),
        glsl_mod(self.y, range),
        glsl_mod(self.z, range)
    )
end

return Vector3
