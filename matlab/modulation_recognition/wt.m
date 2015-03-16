
%% Cell 1

len = 5000;
f = 250;
t = (1:len)/1000;
s = sin(f*pi/16*t);
s(len-3000:len-2000) = -sin(f*pi/16*t(len-3000:len-2000));

a = 2;
length(s);
wt = [];
win = 512
for i=1:5000-win
    wt(i) = wave(s(i:win-1+i));
end
subplot(211)
plot(t, s)
title('signal s(k)')
subplot(212)
plot(t(1+win/2:len-win/2), wt)
title('WT(s(k))')
