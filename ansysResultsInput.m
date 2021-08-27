%% Using external library
currentpath = fileparts(matlab.desktop.editor.getActiveFilename);
fn = [currentpath filesep 'ansys' filesep 'IEAblade_nm03_lattice3x_optimized' filesep 'ansysresults_set06.txt'];
%addpath([currentpath filesep 'lib']) % add lib folder to path
%load('FEAresults_20210823.mat','s');
s = ansysPostproc('import', fn, 3); % filenames requires full path
%s = ansysPostproc('append',s,s2);
ansysPostproc('plot', s, 1, 'UY')
%[nnum,x,y,z] = ansysPostproc('nodes',fullpath);
%% Test
contents = fileread(fn);
contentarray = regexp(contents, '\r\n|\r|\n', 'split');
sc = cell(size(contentarray));
for ii = 1:length(contentarray)
    if isempty(contentarray{ii})
        continue
    else
        sc{ii} = textscan(contentarray{ii},'%f');
    end
end

%% Check labels
disp(' ')
for ii = 1:length(s);disp(s{ii}.title);end