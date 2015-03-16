% Octave, PPM demod after ppm_recorder.py

% Read input
a = read_float_binary('/tmp/ppm.raw');

treshold = max(a(5000:end))/4

% Find rising edges of peaks
a_o = [ a(2:end) ; 0 ];
b = find(a < treshold & a_o > treshold);

% Calculate number of samples between peaks
c = [ b(2:end) ]; c(length(b)) = NaN;
diff = c-b; 
diff_mean = mean(diff(30:end-1));
diff_max = max(diff(30:end-1));
diff_min = min(diff(30:end-1));

% Plot a bar representation of data
figure
t = 50:250;
bar(t, abs(diff(t)-round(diff_mean)))
xlabel "Symbol #"
ylabel "Samples"
title "Soft demodulated data"


% Find the first autocorrelation peak after zero (= cycle length)
t = 50:1000;
sigx = xcorr((diff(t)-diff_mean)/(diff_max-diff_min));
bpos = ceil(length(sigx)/2); % Center point of autocorrelation
% After sorting the second half of autocorrelation, the biggest peak
% index is seqlen
[s, i] = sort(sigx(bpos+1:end));
seqlen = i(end)

% Plot autocorrelation
figure
epos = min(length(sigx)-bpos, seqlen*2.5); % end position
plot(sigx(bpos:bpos+epos))
title "Autocorrelation of data, right half"
xlabel "Symbols"


