% PSK short time fourier transform demo

%% Generate PSK baseband

% Random binary data
data = 2*(randint(1,32,[0,1])-0.5);

% Convert into PSK sinewave by interpolating
s = interp([ 0 data 0 ], 32);

% Multiply by cosine = (-1)^k
s(1:2:length(s)) = -s(1:2:length(s));

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