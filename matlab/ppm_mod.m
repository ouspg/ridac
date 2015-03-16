
%%
pulsewidth = 0.60;
fs = 1000e3; % sampling frequency
fsub = 62.5e3; % subcarrier frequency (+/- carrier)
fc = 125e3; % carrier frequency
carrierampl = 20; % carrier amplitude
data = [ randint(1,128) ] * 0.05;
ppm = modulate(data, 6e3, fs, 'ppm', pulsewidth);
t = 0: 1/fs : 1/fs*(length(ppm)-1);
po = rand(); % random phase offset
rf = ppm .* cos(2*pi*fsub*t + po);
[ppmam, t] = modulate(rf, fc, fs, 'amdsb-tc', carrierampl);
plot(t, ppmam)
fvtool(ppmam)