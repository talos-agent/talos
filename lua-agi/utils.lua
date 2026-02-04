-- utils.lua
local Utils = {}

function Utils.deepcopy(o, seen)
    seen = seen or {}
    if type(o) ~= 'table' then return o end
    if seen[o] then return seen[o] end
    local res = setmetatable({}, getmetatable(o))
    seen[o] = res
    for k, v in pairs(o) do res[Utils.deepcopy(k, seen)] = Utils.deepcopy(v, seen) end
    return res
end

return Utils
