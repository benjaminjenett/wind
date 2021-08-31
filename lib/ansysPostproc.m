function varargout = ansysPostproc(oper,varargin)
% ANSYSPOSTPROC  Perform postproc operations on exported Ansys data
%   s = ansysPostproc('append',s,s2) appends two sets of results into one
%   for easier plotting and management
%   s = ansysPostproc('import', filenames, inputset, labels) imports ansys
%   results from one or more files. filenames must be a cell of full file
%   paths, and inputset chooses from the various sets of data which to
%   import (see values in variable 'headers'). labels is optional
%   [nnum,x,y,z] = ansysPostproc('nodes',fullpath) imports node numbers and
%   x,y,z values from a selected nodes.lis file
%   ansysPostproc('plot', s, range, variable, xmin,xmax,ymin,ymax,zmin,zmax)
%   plots the chosen contained within the results set s, using the indices
%   in range. xmin-zmax are optional and filter the plot
    headers = {'    NODE     S1           S2           S3           SINT         SEQV    ', ... %1
        '    NODE     SX           SY           SZ           SXY          SYZ          SXZ     ', ... %2
        '    NODE       UX           UY           UZ           USUM  ', ...&3
        '    NODE       ROTX         ROTY         ROTZ         RSUM  ', ...%4
        '    NODE     EPELX        EPELY        EPELZ        EPELXY       EPELYZ       EPELXZ  ', ...%5
        '    NODE     EPEL1        EPEL2        EPEL3        EPELINT      EPELEQV ', ...%6
        ' PRINT F    ELEMENT SOLUTION PER ELEMENT', ... %Fx,Fy,Fz %7
        ' PRINT M    ELEMENT SOLUTION PER ELEMENT', ... %Mx,My,Mz %8
        ' PRINT SUMMED NODAL LOADS'
    };
    switch oper
        case 'append' % varargin = s,s2, where s and s2 are each a cell of results, or a single struct
            s = varargin{1};
            s2 = varargin{2};
            sout = cell([length(s) + length(s2),1]);
            if isstruct(s)
                sout{1} = s; 
            else
                for ii = 1:length(s)
                    sout{ii} = s{ii};
                end
            end
            if iscell(s2)
                for ii = 1:length(s2)
                    sout{length(s)+ii} = s2{ii};
                end
            else
                sout{length(s)+1} = s2;
            end
            varargout{1} = sout;
        case 'import' % varargin = filename(s), inputset (pick which items to inport from the headers), labels
            if iscell(varargin{1})
                filenames = varargin{1};
            else
                filenames = {varargin{1}};
            end
            importsets = varargin{2};
            if length(varargin) >=3
                if iscell(varargin{3})
                    labels = varargin{3};
                else
                    labels = repmat({varargin{3}},length(filenames),1);
                end
            end
            s = cell([length(filenames),1]);
            for ii=1:length(filenames)
                fullpath = fileparts(filenames{ii});%fullfile(ansysfolder,folders{ii});
                [nnum,x,y,z] = importNodes(fullpath);
                [~,s{ii}] = importResults(filenames{ii},headers,nnum,importsets);
                s{ii}.x = x;
                s{ii}.y = y;
                s{ii}.z = z;
                s{ii}.nnum = nnum;
                if exist('labels','var') == 1
                    s{ii}.title = labels{ii};
                else
                    s{ii}.title = filenames{ii};
                end
            end
            varargout{1} = s;
        case 'nodes' % varargin = fullpath
            fullpath = varargin{1};
            [nnum,x,y,z] = importNodes(fullpath);
            varargout{1} = nnum;
            varargout{2} = x;
            varargout{3} = y;
            varargout{4} = z;
        case 'plot' % varargin = s, range, plot variable, xmin,xmax,ymin,ymax,zmin,zmax
            s = varargin{1};
            range = varargin{2};
            plotvar = varargin{3};
            if length(varargin) >=9
                xmin = varargin{4};
                xmax = varargin{5};
                ymin = varargin{6};
                ymax = varargin{7};
                zmin = varargin{8};
                zmax = varargin{9};
            end
            figure;
            tiledlayout(1,length(range))
            cmaprange = [0,0];
            for jj = 1:length(range)
                ii = range(jj);
                if exist('xmin','var')
                    index = locationFilter(s{ii}.x,s{ii}.y,s{ii}.z,xmin,xmax,ymin,ymax,zmin,zmax);
                else
                    index = true(size(s{ii}.nnum));
                end
                ax(jj) = nexttile;
                variable = s{ii}.(plotvar);
                variable = variable(index);
                cmaprange = [min(min(variable),cmaprange(1)), max(max(variable),cmaprange(2))];
                scatter3(s{ii}.z(index),s{ii}.x(index),s{ii}.y(index),50,variable);
                title({s{ii}.title, [plotvar ', max=',num2str(max(variable)),', min=',num2str(min(variable))]});
                xlabel('z');
                ylabel('x');
                zlabel('y');
                colorbar;
            end
            for ii = 1:length(ax)
                ax(ii).CLim = cmaprange;
            end
            colormap;
            setappdata(gcf, 'StoreTheLink', linkprop(ax,{'CameraUpVector', 'CameraPosition', 'CameraTarget', 'XLim', 'YLim', 'ZLim'}));
            view(0,90);
            colorbar;
    end
end

function nodevalue = returnvalue(mats,itemnum,nnum)
    nodevalue = zeros([length(nnum),1]);
    for ii = 1:length(nnum)
        index = mats(:,1)==nnum(ii);
        if any(index)
            nodevalue(ii) = mats(index,itemnum+1);
        end
    end
end

function [topvalue,bottomvalue] = returntopbottom(mats,itemnum,nnum)
    topvalue = zeros([length(nnum),1]);
    bottomvalue = zeros([length(nnum),1]);
    for ii = 1:length(nnum)
        index = mats(:,1)==nnum(ii);
        if any(index)
            nodevalues = mats(index,itemnum+1);
            topvalue(ii) = nodevalues(1);
            bottomvalue(ii) = nodevalues(2);
        end
    end
end

function nodevalue = returnvaluesum(mats,itemnum,nnum)
    nodevalue = zeros([length(nnum),1]);
    for ii = 1:length(nnum)
        index = mats(:,1)==nnum(ii);
        nodevalue(ii) = sum(mats(index,itemnum+1));
    end
end

function [xVal,yVal,zVal] = returnFMsubset(lines,elements,nodes)
    index = 1;
    for ii = 1:length(lines)
        line = split(lines(ii),' ');
        line = line(~cellfun(@isempty, line));
        if ~isempty(line) && strcmp(line{1},'ELEM=')
            elemnum = str2double(line{2});
            continue
        else
            linenum = str2double(line);
            if isempty(linenum) || isnan(linenum(1))
                continue
            end
        end
        elementList(index) = elemnum;
        nodeList(index) = linenum(1);
        xList(index) = linenum(2);
        yList(index) = linenum(3);
        zList(index) = linenum(4);
        index = index + 1;
    end
    eIndex = zeros(size(elementList));
    for ii = 1:length(elements)
        eIndex = eIndex | elementList == elements(ii);
    end
    for ii = 1:length(nodes)
        index = eIndex & nodeList == nodes(ii);
        xVal(ii) = sum(xList(index));
        yVal(ii) = sum(yList(index));
        zVal(ii) = sum(zList(index));
    end
end

function filter = locationFilter(x,y,z,xmin,xmax,ymin,ymax,zmin,zmax)
    filter = x <= xmax;
    filter = filter & x >= xmin;
    filter = filter & y <= ymax;
    filter = filter & y >= ymin;
    filter = filter & z <= zmax;
    filter = filter & z >= zmin;
end

function [nnum,x,y,z] = importNodes(fullpath)
    filename = [fullpath filesep 'NLIST.lis'];
    nodestr = fileread(filename);
    nodelines = regexp(nodestr, '\r\n|\r|\n', 'split');
    index = 1;
    for ii = 1:length(nodelines)
        line = split(nodelines(ii),' ');
        line = line(~cellfun(@isempty, line));
        linenum = str2double(line);
        if isempty(linenum) || isnan(linenum(1))
            continue
        end
        nnum(index) = linenum(1);
        x(index) = linenum(2);
        y(index) = linenum(3);
        z(index) = linenum(4);
        index = index + 1;
    end
end

function [mats,s] = importResults(filename,headers,nodes,returnvalues)
    tbList = {'S1top' 'S1bot' 'S2top' 'S2bot' 'S3top' 'S3bot' 'SINTtop' 'SINTbot' 'SEQVtop' 'SEQVbot' 'SXtop' 'SXbot' ...
        'SYtop' 'SYbot' 'SZtop' 'SZbot' 'SXYtop' 'SXYbot' 'SYZtop' 'SYZbot' 'SXZtop' 'SXZbot' 'EPELXtop' 'EPELXbot' ...
        'EPELYtop' 'EPELYbot' 'EPELZtop' 'EPELZbot' 'EPELXYtop' 'EPELXYbot' 'EPELYZtop' 'EPELYZbot' 'EPELXZtop' 'EPELXZbot' ...
        'EPEL1top' 'EPEL1bot' 'EPEL2top' 'EPEL2bot' 'EPEL3top' 'EPEL3bot' 'EPELINTtop' 'EPELINTbot' 'EPELEQVtop' 'EPELEQVbot'};
    valueList = {'UX' 'UY' 'UZ' 'USUM' 'ROTX' 'ROTY' 'ROTZ' 'RSUM'};

    inputstr = fileread(filename);
    inputstr = strrep(inputstr,'-',' -');
    inputstr = strrep(inputstr,'E -','E-');
    lines = regexp(inputstr, '\r\n|\r|\n', 'split');
    splitlocs = zeros([length(headers)+1,1]);
    for ii = 1:length(headers)
        firstline = find(strcmp(lines, headers{ii}));
        splitlocs(ii) = firstline(1);
    end
    splitlocs(end) = length(lines);
    s = struct();
    mats = cell(size(returnvalues));
    for ii = 1:length(returnvalues)
        val = returnvalues(ii);
        hkeys = regexp(headers{val}, ' ', 'split');
        hkeys = hkeys(~cellfun(@isempty,hkeys));
        inputnums = cell([splitlocs(val+1)-splitlocs(val),1]);
        for jj = splitlocs(val):splitlocs(val+1)
            if isempty(lines{jj})
                continue
            else
                inputnums(jj+1-splitlocs(val)) = textscan(lines{jj},'%f');
            end
            %line = split(lines(jj),' ');
            %line = line(~cellfun(@isempty, line));
            %linenum = str2double(line);
            %if isempty(linenum) || isnan(linenum(1))
            %    continue
            %end
            %inputnums{jj+1-splitlocs(val)} = linenum;
        end
        tempdataset = inputnums(~cellfun(@isempty, inputnums));
        lendataset = length(tempdataset{1});
        mat = reshape(cell2mat(tempdataset),lendataset,length(tempdataset))';
        for jj = 2:lendataset
            if cell2mat(strfind(tbList,hkeys{jj})) == 1
                [s.([hkeys{jj} 'top']),s.([hkeys{jj} 'bot'])] = returntopbottom(mat,jj-1,nodes);
            elseif cell2mat(strfind(valueList,hkeys{jj})) == 1
                s.(hkeys{jj}) = returnvalue(mat,jj-1,nodes);
            else
                s.(hkeys{jj}) = returnvaluesum(mat,jj-1,nnum);
            end
        end
        mats{ii} = mat;
    end
end