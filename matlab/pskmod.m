%%
bits = 64; % Amount of data
Nsamp = 128; % Oversampling rate
M = 2;

% Data = random bits
z = [ 0 1 0 1   0 1 0 1  0 0 0 0 1 1 1 1 ];
x = [ z z randint(1, bits, M) ]';

% Use 2-PSK modulation
h = modem.pskmod(M);
y = modulate(h,x);

% RRC
filtorder = Nsamp*4; % Filter order
delay = filtorder/(Nsamp*2); % Group delay (# of input samples)
rolloff = 0.9; % Rolloff factor of filter
rrcfilter = rcosine(1,Nsamp,'fir/sqrt',rolloff,delay);
%ypulse = rcosflt(y,1,Nsamp,'filter',rrcfilter);

ypulse = rectpulse(y,Nsamp);

% Translate up
k = 0:length(ypulse)-1;
Fs = 500e3;
Fc = 125e3;
y_translated = cos((Fc/Fs)*k*pi)'.*ypulse;

% Modulate with AM
y_rf = modulate(y_translated, Fc, Fs, 'amdsb-tc', 2);

write_complex_binary('/home/joneskoo/psk-64-sig.raw', y_rf*5000);
