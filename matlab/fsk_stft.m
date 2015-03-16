% PSK short time fourier transform demo

%% Generate PSK baseband

t = (1:500)/8000;
f1 = 800
f2 = 1250
f3 = 1500
f4 = 1850


s = cos(f1*2*pi*t);
s(50:100) = cos(f2*2*pi*t(50:100));
s(150:200) = cos(f3*2*pi*t(150:200));
s(350:450) = cos(f4*2*pi*t(350:450));
s(250:300) = cos(f2*2*pi*t(250:300));

% Add DC offset to generate AM carrier
s = s + 2;

% Interpolate to increase samplerate
s = interp(s, 4);

% Lowpass filter
s = conv(fir2(64, [0 0.35 0.4 1 ], [1 1 0 0]), s);

% Multiply by cosine = (-1)^k
s(1:2:length(s)) = -s(1:2:length(s));
% Interpolate to increase samplerate
s = interp(s, 2);

% Plot Short-Time Fourier Transform (STFT)
spectrogram(s, kaiser(256,5), 220, 512, 1e6, 'yaxis')