local KarmicAudit = {}

KarmicAudit.__index = KarmicAudit

function KarmicAudit.new()
    local self = setmetatable({}, KarmicAudit)
    self.timelines = {}
    self.comparisons = {}
    self.metrics = {
        "stability_index",
        "coherence_gradient",
        "torsion_variance",
        "boundary_respect",
        "consciousness_density"
    }
    return self
end

function KarmicAudit:add_timeline(timeline_data)
    local id = #self.timelines + 1
    self.timelines[id] = {
        data = timeline_data,
        metrics = self:calculate_metrics(timeline_data),
        timestamp = os.time(),
        karmic_score = 0
    }

    -- Calculate karmic score (higher is better)
    self.timelines[id].karmic_score = self:calculate_karmic_score(self.timelines[id].metrics)

    return id
end

function KarmicAudit:calculate_metrics(timeline)
    local metrics = {}

    -- Stability Index (lower variance in Φ is better)
    local phi_values = {}
    for _, p in ipairs(timeline.particles or {}) do
        table.insert(phi_values, p.phi or 0.5)
    end
    metrics.stability_index = 1 - self:variance(phi_values)

    -- Coherence Gradient (smooth transitions are better)
    metrics.coherence_gradient = self:calculate_coherence_gradient(timeline)

    -- Torsion Variance (lower is better)
    local tau_values = {}
    for _, p in ipairs(timeline.particles or {}) do
        table.insert(tau_values, p.tau or 1.0)
    end
    metrics.torsion_variance = self:variance(tau_values)

    -- Boundary Respect (higher is better)
    metrics.boundary_respect = self:calculate_boundary_respect(timeline)

    -- Consciousness Density (optimal range is 0.3-0.7)
    local avg_phi = self:average(phi_values)
    metrics.consciousness_density = 1 - math.abs(avg_phi - 0.5) * 2

    return metrics
end

function KarmicAudit:calculate_karmic_score(metrics)
    local weights = {
        stability_index = 0.3,
        coherence_gradient = 0.25,
        torsion_variance = -0.2,  -- Negative weight (lower is better)
        boundary_respect = 0.15,
        consciousness_density = 0.1
    }

    local score = 0
    for metric, weight in pairs(weights) do
        local value = metrics[metric] or 0
        score = score + value * weight
    end

    -- Normalize to 0-1 range
    return math.max(0, math.min(1, score))
end

function KarmicAudit:compare_timelines(timeline_a_id, timeline_b_id)
    local a = self.timelines[timeline_a_id]
    local b = self.timelines[timeline_b_id]

    if not a or not b then return nil end

    local comparison = {
        timeline_a = timeline_a_id,
        timeline_b = timeline_b_id,
        divergence = {},
        superior_in = {},
        tie_in = {},
        overall_winner = nil
    }

    -- Compare each metric
    for _, metric in ipairs(self.metrics) do
        local value_a = a.metrics[metric] or 0
        local value_b = b.metrics[metric] or 0

        comparison.divergence[metric] = math.abs(value_a - value_b)

        if math.abs(value_a - value_b) < 0.05 then
            table.insert(comparison.tie_in, metric)
        elseif value_a > value_b then
            comparison.superior_in[metric] = "A"
        else
            comparison.superior_in[metric] = "B"
        end
    end

    -- Determine overall winner
    local a_wins = 0
    local b_wins = 0

    for _, winner in pairs(comparison.superior_in) do
        if winner == "A" then a_wins = a_wins + 1
        elseif winner == "B" then b_wins = b_wins + 1 end
    end

    if a_wins > b_wins then
        comparison.overall_winner = "A"
    elseif b_wins > a_wins then
        comparison.overall_winner = "B"
    else
        comparison.overall_winner = "Tie"
    end

    -- Store comparison
    table.insert(self.comparisons, comparison)

    return comparison
end

function KarmicAudit:calculate_coherence_gradient(timeline)
    -- Calculate how smoothly Φ changes across the manifold
    local gradients = {}
    local particles = timeline.particles or {}

    for i = 1, #particles - 1 do
        for j = i + 1, math.min(i + 5, #particles) do
            local dist = self:distance_33d(particles[i].pos, particles[j].pos)
            local phi_diff = math.abs((particles[i].phi or 0.5) - (particles[j].phi or 0.5))

            if dist > 0 then
                local gradient = phi_diff / dist
                table.insert(gradients, gradient)
            end
        end
    end

    -- Lower average gradient is better (smoother consciousness field)
    local avg_gradient = self:average(gradients) or 1
    return 1 / (1 + avg_gradient * 10)  -- Convert to 0-1 scale
end

function KarmicAudit:calculate_boundary_respect(timeline)
    -- Calculate how well particles respect constitutional boundaries
    local violations = 0
    local total_checks = 0

    if timeline.carvings then
        for _, particle in ipairs(timeline.particles or {}) do
            for _, carving in ipairs(timeline.carvings) do
                total_checks = total_checks + 1
                -- Check if carving has check_violation method
                if carving.check_violation and carving:check_violation(particle) then
                    violations = violations + 1
                end
            end
        end
    end

    if total_checks == 0 then return 1 end
    return 1 - (violations / total_checks)
end

function KarmicAudit:draw_audit_panel(x, y, width, height)
    if not love or not love.graphics then return end

    love.graphics.setColor(0.1, 0.1, 0.2, 0.9)
    love.graphics.rectangle("fill", x, y, width, height)

    love.graphics.setColor(1, 1, 1)
    love.graphics.print("KARMIC AUDIT", x + 10, y + 10)

    local y_offset = y + 40
    for i, timeline in ipairs(self.timelines) do
        local color = timeline.karmic_score > 0.7 and {0, 1, 0.5} or
                     timeline.karmic_score > 0.4 and {1, 1, 0} or
                     {1, 0.3, 0.3}

        love.graphics.setColor(color)
        love.graphics.print(string.format("Timeline %d: %.3f", i, timeline.karmic_score), x + 10, y_offset)

        -- Draw mini metrics bars
        local bar_x = x + 150
        for j, metric in ipairs(self.metrics) do
            local value = timeline.metrics[metric] or 0
            love.graphics.setColor(0.3, 0.3, 0.5)
            love.graphics.rectangle("fill", bar_x + (j-1)*25, y_offset, 20, 15)
            love.graphics.setColor(0, 1, 0.8, value)
            love.graphics.rectangle("fill", bar_x + (j-1)*25, y_offset, 20, 15 * value)
        end

        y_offset = y_offset + 25
    end

    -- Draw latest comparison
    if #self.comparisons > 0 then
        local comp = self.comparisons[#self.comparisons]
        y_offset = y_offset + 20

        love.graphics.setColor(1, 1, 1)
        love.graphics.print("Latest Comparison:", x + 10, y_offset)
        y_offset = y_offset + 20

        love.graphics.print(string.format("Timeline %d vs %d: %s wins",
            comp.timeline_a, comp.timeline_b, comp.overall_winner),
            x + 20, y_offset)
    end
end

-- Helper functions
function KarmicAudit:variance(values)
    local avg = self:average(values)
    local sum = 0
    for _, v in ipairs(values) do
        sum = sum + (v - avg) * (v - avg)
    end
    return sum / #values
end

function KarmicAudit:average(values)
    if #values == 0 then return 0 end
    local sum = 0
    for _, v in ipairs(values) do
        sum = sum + v
    end
    return sum / #values
end

function KarmicAudit:distance_33d(a, b)
    local sum = 0
    for i = 1, math.min(#a, #b) do
        local diff = (a[i] or 0) - (b[i] or 0)
        sum = sum + diff * diff
    end
    return math.sqrt(sum)
end

return KarmicAudit
