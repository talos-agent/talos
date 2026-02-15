% ucd.m

function result = ucd_analyze(data)
    % data: matriz (linhas = variáveis, colunas = observações)
    [nvars, nobs] = size(data);
    if nvars > 1
        corr_mat = abs(corrcoef(data'));
        % extrair elementos acima da diagonal
        tri = triu(corr_mat, 1);
        C = mean(tri(tri~=0));
    else
        C = 0.5;
    end
    F = 1.0 - C;
    conservation = abs(C + F - 1.0) < 1e-10;
    if C > 0.8
        topology = 'toroidal';
    else
        topology = 'other';
    end
    if C > 0.7
        scaling = 'self-similar';
    else
        scaling = 'linear';
    end
    optimization = F * 0.5;
    result = struct('C', C, 'F', F, 'conservation', conservation, ...
                    'topology', topology, 'scaling', scaling, ...
                    'optimization', optimization);
end

% Exemplo
data = [1 2 3 4; 2 3 4 5; 5 6 7 8];
ucd_analyze(data)
