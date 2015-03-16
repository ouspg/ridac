% sig = input baseband signal
% sps = samples per symbol
% N = samples to plot
function [sig_r] = eyediagram(sig, sps, N)
        symbols = 3; % how many symbols visible

        N = symbols*min(floor(N/symbols), floor(length(sig)/sps/symbols));
        sig_r = reshape(sig(1:N*sps), symbols*sps, N/symbols);
        
        subplot(211)
        plot(real(sig_r))
        title 'Eye diagram / I channel'

        subplot(212)
        plot(imag(sig_r))
        title 'Eye diagram / Q channel'
end

