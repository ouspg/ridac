function t = read_complex_binary (filename, count)

  %% usage: read_complex_binary (filename, [count])
  %%
  %%  open filename and return the contents as a column vector, 
  %%  treating them as 32 bit complex numbers
  %%

  if (nargin < 2)
    count = Inf;
  end

  f = fopen (filename, 'rb');
  if (f < 0)
    v = 0;
  else
    t = fread (f, [2, count], 'float');
    fclose (f);
  end
