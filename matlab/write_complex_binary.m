function v = write_complex_binary (filename, data)

%% usage: write_complex_binary (filename, data)
%%
%%  open filename and write a list of complex numbers
%%  as floats
  
  f = fopen (filename, 'wb');
  if (f < 0)
    v = 0;
  else
    for i=1:length(data)
        fwrite (f, real(data(i)), 'float');
        fwrite (f, imag(data(i)), 'float');
    end;
    fclose (f);
  end
end


