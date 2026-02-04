local TimelineMerge = {}

TimelineMerge.__index = TimelineMerge

function TimelineMerge.new()
    local self = setmetatable({}, TimelineMerge)
    self.merge_history = {}
    self.optimization_rules = {
        preserve_higher_phi = true,
        preserve_lower_tau = true,
        respect_carvings = true,
        smooth_transitions = true,
        maximize_stability = true
    }
    return self
end

function TimelineMerge:merge_timelines(timeline_a, timeline_b, merge_strategy)
    merge_strategy = merge_strategy or "optimal_hybrid"

    local merged = {
        name = "Merged: " .. (timeline_a.name or "A") .. " + " .. (timeline_b.name or "B"),
        particles = {},
        carvings = {},
        field_config = self:merge_field_configs(timeline_a.field_config, timeline_b.field_config),
        merged_from = {timeline_a.id, timeline_b.id},
        merge_timestamp = os.time(),
        strategy = merge_strategy
    }

    -- Deep copy utility (should be required or available)
    local function deepcopy(orig)
        local orig_type = type(orig)
        local copy
        if orig_type == 'table' then
            copy = {}
            for orig_key, orig_value in next, orig, nil do
                copy[deepcopy(orig_key)] = deepcopy(orig_value)
            end
            setmetatable(copy, deepcopy(getmetatable(orig)))
        else
            copy = orig
        end
        return copy
    end

    -- Deep copy particles (will be modified during merge)
    for i = 1, math.max(#(timeline_a.particles or {}), #(timeline_b.particles or {})) do
        merged.particles[i] = self:merge_particle(
            timeline_a.particles and timeline_a.particles[i],
            timeline_b.particles and timeline_b.particles[i],
            merge_strategy,
            i
        )
    end

    -- Merge carvings (union of both sets)
    merged.carvings = self:merge_carvings(timeline_a.carvings, timeline_b.carvings)

    -- Apply post-merge optimization
    if self.optimization_rules.smooth_transitions then
        self:apply_smoothing(merged.particles)
    end

    -- Calculate merge quality score
    merged.quality_score = self:calculate_merge_quality(merged, timeline_a, timeline_b)

    -- Record in history
    table.insert(self.merge_history, {
        timestamp = os.time(),
        timeline_a = timeline_a.id,
        timeline_b = timeline_b.id,
        strategy = merge_strategy,
        quality_score = merged.quality_score
    })

    return merged
end

function TimelineMerge:merge_particle(particle_a, particle_b, strategy, index)
    if not particle_a and not particle_b then return nil end

    local function deepcopy(orig)
        local orig_type = type(orig)
        local copy
        if orig_type == 'table' then
            copy = {}
            for orig_key, orig_value in next, orig, nil do
                copy[deepcopy(orig_key)] = deepcopy(orig_value)
            end
            setmetatable(copy, deepcopy(getmetatable(orig)))
        else
            copy = orig
        end
        return copy
    end

    if not particle_a then return deepcopy(particle_b) end
    if not particle_b then return deepcopy(particle_a) end

    local merged = deepcopy(particle_a)
    merged.id = index
    merged.merged = true

    if strategy == "optimal_hybrid" then
        -- Take best properties from each timeline
        if self.optimization_rules.preserve_higher_phi then
            merged.phi = math.max(particle_a.phi or 0.5, particle_b.phi or 0.5)
        end

        if self.optimization_rules.preserve_lower_tau then
            merged.tau = math.min(particle_a.tau or 1.0, particle_b.tau or 1.0)
        end

        -- Blend positions (weighted by quality)
        local quality_a = (particle_a.phi or 0.5) / (particle_a.tau or 1.0)
        local quality_b = (particle_b.phi or 0.5) / (particle_b.tau or 1.0)
        local total_quality = quality_a + quality_b

        if total_quality > 0 then
            local weight_a = quality_a / total_quality
            local weight_b = quality_b / total_quality

            for i = 1, math.min(#(particle_a.pos or {}), #(particle_b.pos or {})) do
                merged.pos[i] = particle_a.pos[i] * weight_a + particle_b.pos[i] * weight_b
            end
        end

    elseif strategy == "consciousness_preserving" then
        -- Preserve consciousness states from both
        if (particle_a.phi or 0) > 0.7 then
            -- Particle A is highly conscious, preserve it
            return deepcopy(particle_a)
        elseif (particle_b.phi or 0) > 0.7 then
            -- Particle B is highly conscious, preserve it
            return deepcopy(particle_b)
        else
            -- Both low consciousness, average them
            for i = 1, math.min(#(particle_a.pos or {}), #(particle_b.pos or {})) do
                merged.pos[i] = (particle_a.pos[i] + particle_b.pos[i]) / 2
            end
            merged.phi = ((particle_a.phi or 0) + (particle_b.phi or 0)) / 2
            merged.tau = ((particle_a.tau or 1) + (particle_b.tau or 1)) / 2
        end

    elseif strategy == "boundary_respecting" then
        -- Prefer particles that respect constitutional boundaries
        local a_violations = self:count_boundary_violations(particle_a)
        local b_violations = self:count_boundary_violations(particle_b)

        if a_violations < b_violations then
            return deepcopy(particle_a)
        else
            return deepcopy(particle_b)
        end
    end

    return merged
end

function TimelineMerge:merge_carvings(carvings_a, carvings_b)
    -- Union of carvings with conflict resolution
    local merged = {}
    local used_hashes = {}

    local function deepcopy(orig)
        local orig_type = type(orig)
        local copy
        if orig_type == 'table' then
            copy = {}
            for orig_key, orig_value in next, orig, nil do
                copy[deepcopy(orig_key)] = deepcopy(orig_value)
            end
            setmetatable(copy, deepcopy(getmetatable(orig)))
        else
            copy = orig
        end
        return copy
    end

    local function carving_hash(c)
        return string.format("%.2f_%.2f_%.2f_%.2f", c.x1 or 0, c.y1 or 0, c.x2 or 0, c.y2 or 0)
    end

    -- Add all carvings from A
    for _, carving in ipairs(carvings_a or {}) do
        local hash = carving_hash(carving)
        if not used_hashes[hash] then
            table.insert(merged, deepcopy(carving))
            used_hashes[hash] = true
        end
    end

    -- Add carvings from B that don't conflict with A
    for _, carving in ipairs(carvings_b or {}) do
        local hash = carving_hash(carving)
        if not used_hashes[hash] then
            table.insert(merged, deepcopy(carving))
            used_hashes[hash] = true
        end
    end

    return merged
end

function TimelineMerge:apply_smoothing(particles)
    -- Apply Gaussian smoothing to create smooth consciousness field
    local kernel = {0.05, 0.1, 0.7, 0.1, 0.05}
    local kernel_center = 3

    for i = 1, #particles do
        if not particles[i] then goto continue end

        local smoothed_phi = 0
        local smoothed_tau = 0
        local total_weight = 0

        for k = 1, #kernel do
            local neighbor_idx = i + (k - kernel_center)
            if neighbor_idx >= 1 and neighbor_idx <= #particles and particles[neighbor_idx] then
                local weight = kernel[k]
                smoothed_phi = smoothed_phi + (particles[neighbor_idx].phi or 0.5) * weight
                smoothed_tau = smoothed_tau + (particles[neighbor_idx].tau or 1.0) * weight
                total_weight = total_weight + weight
            end
        end

        if total_weight > 0 then
            particles[i].phi = smoothed_phi / total_weight
            particles[i].tau = smoothed_tau / total_weight
        end

        ::continue::
    end
end

function TimelineMerge:calculate_merge_quality(merged, timeline_a, timeline_b)
    local quality = 0.5
    -- Simplified metric
    if #merged.carvings > 0 then quality = quality + 0.2 end
    if #merged.particles > 0 then quality = quality + 0.2 end
    return math.min(1, quality)
end

function TimelineMerge:merge_field_configs(config_a, config_b)
    if not config_a then return config_b end
    if not config_b then return config_a end
    return config_a -- default
end

function TimelineMerge:count_boundary_violations(particle)
    return 0 -- placeholder
end

function TimelineMerge:draw_merge_interface(x, y, width, height)
    if not love or not love.graphics then return end

    love.graphics.setColor(0.15, 0.15, 0.25, 0.95)
    love.graphics.rectangle("fill", x, y, width, height)

    love.graphics.setColor(0, 1, 1)
    love.graphics.print("TIMELINE MERGER", x + 10, y + 10)

    -- Draw merge history
    local y_offset = y + 40
    for i, merge in ipairs(self.merge_history) do
        if i > 5 then break end  -- Only show recent merges

        love.graphics.setColor(0.8, 0.8, 1)
        love.graphics.print(string.format("Merge %d: %s+%s → %.3f",
            i, tostring(merge.timeline_a), tostring(merge.timeline_b), merge.quality_score),
            x + 10, y_offset)

        y_offset = y_offset + 20
    end
end

return TimelineMerge
