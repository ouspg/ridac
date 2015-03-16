%% Preprocessing (filter & treshold)
% bandpass filter (pass 64.25 kHz)

Fs = 500;  % Sampling Frequency

N             = 63;       % Order
Fc1           = 64.15;    % First Cutoff Frequency
Fc2           = 64.35;    % Second Cutoff Frequency
flag          = 'scale';  % Sampling Flag
SidelobeAtten = 70;       % Window Parameter
win = chebwin(N+1, SidelobeAtten);
bp  = fir1(N, [Fc1 Fc2]/(Fs/2), 'bandpass', win, flag);
%fvtool(bp)

% FIR Window Lowpass filter designed using the FIR1 function.
% All frequency values are normalized to 1.

N    = 63;       % Order
Fc   = 0.01;     % Cutoff Frequency
flag = 'scale';  % Sampling Flag
win = blackmanharris(N+1);
lpf  = fir1(N, Fc, 'low', win, flag);

sig = filter(bp, 1, ppmam);
sig2 = filter(lpf, 1, sig.^2);
sig2 = sig2 > max(sig2(1000:end))/2;

% Find rising edges by tresholding
sig2_offset = [sig2(2:end) NaN];
rising_edges = find(sig2 < 0.5 & sig2_offset > 0.5);

% The time difference between two pulses contains the
% information in the signal
rising_edges_o = [rising_edges(2:end) NaN];
deltas = rising_edges_o(1:end-1) - rising_edges(1:end-1);

%% Rising edge detection visualisation
figure
v = [ 1 4000 -0.1 1.1 ];
plot(sig2)
axis(v)
hold on
plot(rising_edges, 0.5, 'rx')
axis(v)
hold off

%% Demodulated data vs. original data
figure
b = 10
e = 20
t = b:e
v = [ b e -8 8];
subplot(311)
data_o = [data(2:end) NaN];
dr = (data_o(1:end-1) - data(1:end-1));
dr_max = max(dr);
dr_min = min(dr);
dr_mean = mean(dr);
bar(t, 7/0.4*(dr(t)-dr_mean)/(dr_max-dr_min))
title 'Modulation input data'
ylabel('Delta to previous symbol')
xlabel('Symbol #')
axis(v)

subplot(312)
d = deltas(2:end);
d_max = max(d);
d_min = min(d);
d_mean = mean(d);
bar(t, 7/0.4*(d(t)-d_mean)/(d_max-d_min))
title 'Demodulation output data'
ylabel('Delta to previous symbol')
xlabel('Symbol #')
axis(v)

subplot(313)
t = b : (e-b)/(rising_edges(e)-rising_edges(b)) : e;
plot(t, sig2(rising_edges(b):rising_edges(e)), 'r')
hold on
plot(t, sig(rising_edges(b):rising_edges(e)))
title 'Signal before demodulation (after filtering)'
ylabel('Amplitude')
xlabel('Symbol #')
