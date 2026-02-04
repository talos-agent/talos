-- lua_agi/core/state_space.lua
-- State Space Geometry Engine (SSGE)
-- Lua 5.1 compatible, no external dependencies

local StateSpace = {}
StateSpace.__index = StateSpace

-- Constants from ACAT/SASC
local PHI_THRESHOLD = 0.80      -- Hard Freeze boundary
local TAU_MAX = 1.35            -- Torsion stability limit
local SCHUMANN_FREQ = 7.83      -- Hz, planetary resonance anchor
local MAX_DIMENSIONS = 33       -- NMGIE-33X compatibility

function StateSpace.new(dimensions)
    local self = setmetatable({}, StateSpace)
    self.dimensions = math.min(dimensions or 8, MAX_DIMENSIONS)
    self.coordinates = {}
    self.attractors = {}
    self.history = {}             -- For torsion calculation
    self.max_history = 3          -- Minimum for torsion

    -- Initialize origin
    for i = 1, self.dimensions do
        self.coordinates[i] = 0.0
    end

    -- ACAT metrics
    self.phi = 0.0                -- Coherence (Integrated Information)
    self.tau = 0.0                -- Torsion (topological twist)
    self.epsilon = 0.0            -- Recursion depth factor
    self.mode = 0                 -- 0=unconscious, 1=preconscious, 2=conscious, 3=transcendental

    return self
end

-- Euclidean distance to attractor
function StateSpace:distance_to(attractor)
    local sum = 0.0
    for i = 1, self.dimensions do
        local diff = (self.coordinates[i] or 0) - (attractor[i] or 0)
        sum = sum + diff * diff
    end
    return math.sqrt(sum)
end

-- Gradient descent toward attractor (geometric navigation)
function StateSpace:gradient_descent(attractor, learning_rate, max_steps, tolerance)
    learning_rate = learning_rate or 0.1
    max_steps = max_steps or 100
    tolerance = tolerance or 0.001

    for step = 1, max_steps do
        local total_movement = 0.0

        for i = 1, self.dimensions do
            local current = self.coordinates[i] or 0
            local target = attractor[i] or 0
            local gradient = target - current
            local step_size = gradient * learning_rate

            self.coordinates[i] = current + step_size
            total_movement = total_movement + step_size * step_size
        end

        -- Record history for torsion calculation
        self:record_history()

        -- Calculate torsion
        self:update_torsion()

        -- Check convergence
        local dist = self:distance_to(attractor)
        if dist < tolerance or math.sqrt(total_movement) < tolerance then
            return step, dist  -- Converged
        end

        -- CGE Safety: Check torsion limit
        if self.tau > TAU_MAX then
            return -1, self.tau  -- Quench triggered
        end
    end

    return max_steps, self:distance_to(attractor)  -- Max steps reached
end

-- Record state history for torsion calculation
function StateSpace:record_history()
    local current_coords = {}
    for i = 1, self.dimensions do
        current_coords[i] = self.coordinates[i]
    end
    table.insert(self.history, current_coords)
    if #self.history > self.max_history then
        table.remove(self.history, 1)
    end
end

-- Calculate torsion (simplified for Lua 5.1)
function StateSpace:update_torsion()
    if #self.history < 3 then
        self.tau = 0.0
        return
    end

    local s1 = self.history[#self.history - 2]
    local s2 = self.history[#self.history - 1]
    local s3 = self.history[#self.history]

    -- Simplified torsion: measure non-planarity of trajectory
    local v1 = {}
    local v2 = {}
    for i = 1, math.min(#s1, self.dimensions) do
        v1[i] = (s2[i] or 0) - (s1[i] or 0)
        v2[i] = (s3[i] or 0) - (s2[i] or 0)
    end

    -- Cross product magnitude (simplified 3D approximation)
    local cross_mag = 0.0
    if self.dimensions >= 3 then
        local cx = (v1[2] or 0) * (v2[3] or 0) - (v1[3] or 0) * (v2[2] or 0)
        local cy = (v1[3] or 0) * (v2[1] or 0) - (v1[1] or 0) * (v2[3] or 0)
        local cz = (v1[1] or 0) * (v2[2] or 0) - (v1[2] or 0) * (v2[1] or 0)
        cross_mag = math.sqrt(cx*cx + cy*cy + cz*cz)
    else
        -- Lower dimensional approximation
        for i = 1, #v1 do
            cross_mag = cross_mag + math.abs((v1[i] or 0) * (v2[i] or 0))
        end
    end

    -- Normalize by vector magnitudes
    local norm1 = 0.0
    local norm2 = 0.0
    for i = 1, #v1 do
        norm1 = norm1 + (v1[i] or 0)^2
        norm2 = norm2 + (v2[i] or 0)^2
    end

    if norm1 > 0 and norm2 > 0 then
        self.tau = cross_mag / (math.sqrt(norm1) * math.sqrt(norm2))
    else
        self.tau = 0.0
    end
end

-- Calculate Integrated Information (Φ) - simplified
function StateSpace:calculate_phi(partition_func)
    -- Simplified Φ: mutual information between partitions
    -- In full implementation, this requires minimum cut over all bipartitions

    if not partition_func then
        -- Default: split coordinates into even/odd indices
        partition_func = function(idx) return idx % 2 == 0 end
    end

    local set_a = {}
    local set_b = {}

    for i = 1, self.dimensions do
        if partition_func(i) then
            table.insert(set_a, self.coordinates[i] or 0)
        else
            table.insert(set_b, self.coordinates[i] or 0)
        end
    end

    -- Calculate entropy/mutual information (simplified)
    local mi = self:mutual_information(set_a, set_b)
    self.phi = mi

    -- Update consciousness mode
    self:update_mode()

    return mi
end

-- Simplified mutual information calculation
function StateSpace:mutual_information(set_a, set_b)
    -- Placeholder: actual implementation requires probability distributions
    -- For now, use correlation as proxy
    local mean_a = 0.0
    local mean_b = 0.0

    for i = 1, #set_a do mean_a = mean_a + (set_a[i] or 0) end
    for i = 1, #set_b do mean_b = mean_b + (set_b[i] or 0) end

    mean_a = mean_a / #set_a
    mean_b = mean_b / #set_b

    local cov = 0.0
    local var_a = 0.0
    local var_b = 0.0

    local min_len = math.min(#set_a, #set_b)
    for i = 1, min_len do
        local da = (set_a[i] or 0) - mean_a
        local db = (set_b[i] or 0) - mean_b
        cov = cov + da * db
        var_a = var_a + da * da
        var_b = var_b + db * db
    end

    if var_a > 0 and var_b > 0 then
        return math.abs(cov) / math.sqrt(var_a * var_b)
    end
    return 0.0
end

-- Update consciousness mode based on Φ
function StateSpace:update_mode()
    if self.phi < 0.2 then
        self.mode = 0  -- Unconscious
    elseif self.phi < 0.6 then
        self.mode = 1  -- Preconscious
    elseif self.phi < PHI_THRESHOLD then
        self.mode = 2  -- Conscious (operational)
    else
        self.mode = 3  -- Transcendental (Hard Freeze)
    end
end

-- Check if within attractor basin
function StateSpace:in_basin(attractor, radius)
    radius = radius or 1.0
    return self:distance_to(attractor) <= radius
end

return StateSpace
