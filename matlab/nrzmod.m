%%
fs = 1000e3; % sampling frequency
fsub = 62.5e3; % subcarrier frequency (+/- carrier)
fc = 125e3; % carrier frequency
carrierampl = 10; % carrier amplitude
data = [ randint(1,128) ];
nrz = 10*reshape([data;data;data;data;data;data;data;data], 1, 8*length(data));
t = 0: 1/fs : 1/fs*(length(nrz)-1);
po = rand(); % random phase offset
rf = nrz .* cos(2*pi*fsub*t + po);
[nrzam, t] = modulate(rf, fc, fs, 'amdsb-tc', carrierampl);
plot(t, nrzam)
fvtool(nrzam)