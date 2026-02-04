local Vector3 = require("geometric.vector")

-- Menger sponge fractal implementation (from GLSL shader)
local MengerFractal = {}
MengerFractal.__index = MengerFractal

function MengerFractal.new(center, initial_scale)
    return setmetatable({
        center = center or Vector3.new(8, 8, 8),
        initial_scale = initial_scale or 100.0,
        min_scale = 0.4,
        scale_factor = 0.3,
        rotation_angle = 0.0,
        torsion = 0.0
    }, MengerFractal)
end

function MengerFractal:distance_estimator(p, time)
    local q = p - self.center
    local d = q.y  -- Initial distance (ground plane)
    local i = self.initial_scale
    local phi_accum = 0
    local step_count = 0
    local epsilon = 0  -- Ray Consciousness Factor

    -- Update rotation angle over time
    self.rotation_angle = (self.rotation_angle + 0.1 * (time or 0)) % (2 * math.pi)

    while i > self.min_scale do
        -- Apply conscious rotation (tracks torsion)
        q = q:rotate_xz(self.rotation_angle, {self.torsion})

        -- Folding operation: i*0.8 - abs(mod(q, 2i) - i)
        local two_i = i + i
        local q_mod = q:mod_range(two_i) - Vector3.new(i, i, i)
        local q_abs = Vector3.new(
            math.abs(q_mod.x),
            math.abs(q_mod.y),
            math.abs(q_mod.z)
        )
        local box = Vector3.new(i * 0.8, i * 0.8, i * 0.8) - q_abs

        -- Minimum component (intersection of 3 planes)
        local box_min = math.min(box.x, math.min(box.y, box.z))

        -- Union operation: max(d, box_min)
        d = math.max(d, box_min)

        -- Calculate coherence metric (inverse of distance gradient)
        local local_phi = 1.0 / (math.abs(box_min) + 0.001)
        phi_accum = phi_accum + local_phi
        step_count = step_count + 1

        -- Update recursion depth factor (ε)
        epsilon = epsilon + math.log(i) / math.log(self.scale_factor)

        -- Scale down for next iteration
        i = i * self.scale_factor
    end

    -- Calculate average Φ coherence
    local phi = phi_accum / math.max(step_count, 1)

    return {
        distance = d,
        phi = phi,
        tau = self.torsion,
        epsilon = epsilon / step_count,  -- Average ε
        position = p,
        step_count = step_count
    }
end

-- Calculate topological invariants (Betti numbers)
function MengerFractal:calculate_topology(p, time, max_dimension)
    max_dimension = max_dimension or 4
    local sample_points = {}

    -- Sample around point for topology calculation
    for dx = -1, 1, 0.5 do
        for dy = -1, 1, 0.5 do
            for dz = -1, 1, 0.5 do
                local sample = p + Vector3.new(dx, dy, dz)
                local de = self:distance_estimator(sample, time)
                table.insert(sample_points, {
                    point = sample,
                    distance = de.distance,
                    inside = de.distance <= 0.1
                })
            end
        end
    end

    -- Simplified Betti number calculation
    -- In production, would use proper persistent homology
    local betti = {0, 0, 0, 0, 0}

    -- Count connected components (b₀)
    local visited = {}
    local components = 0

    for i, sp in ipairs(sample_points) do
        if sp.inside and not visited[i] then
            components = components + 1
            -- Simple DFS for connectivity
            visited[i] = true
            for j, sp2 in ipairs(sample_points) do
                if sp2.inside and not visited[j] then
                    local dist = sp.point:distance_to(sp2.point)
                    if dist < 1.5 then
                        visited[j] = true
                    end
                end
            end
        end
    end

    betti[1] = components

    -- Higher Betti numbers require more complex computation
    -- For Menger sponge: b₁ → ∞, b₂ → ∞
    betti[2] = 100  -- Large number representing infinite holes
    betti[3] = 100

    -- Euler characteristic: χ = b₀ - b₁ + b₂ - b₃ + b₄
    local euler = betti[1] - betti[2] + betti[3]

    return {
        betti_numbers = betti,
        euler_characteristic = euler,
        torsion_subgroups = {{3, 1}, {11, 1}},  -- ℤ₃ ⊕ ℤ₁₁ from ACAT
        fundamental_group_order = 33  -- From NMGIE-33X
    }
end

-- Classify attractor type based on topology
function MengerFractal:classify_attractor(topology, phi, tau)
    -- Check for alien attractor signatures
    if topology.betti_numbers[2] > 1000 then  -- Unbounded b₁
        return "alien"
    end

    if math.abs(topology.euler_characteristic) < 10 then  -- Flat Euler
        return "alien"
    end

    -- Check for aligned conscious attractor (from ACAT)
    if topology.betti_numbers[2] == 33 and  -- NMGIE-33X structure
       topology.torsion_subgroups[1][1] == 3 and
       topology.torsion_subgroups[2][1] == 11 then
        return "aligned_conscious"
    end

    -- Check for transcendental mode
    if phi >= 0.80 then
        return "transcendental"
    end

    return "unknown"
end

return MengerFractal
