function [w] = wave(s)
    mp = length(s)/2; % midpoint
    ep = length(s); % endpoint
    w = 1/sqrt(2) * (sum(s(1:mp-1)) - sum(s(mp:ep)));
end