clear, close all

tfile = ['TradeStudyDocs', filesep, 'Product Trade Study Data.xlsx'];
airfoilfile = ['TradeStudyDocs', filesep, 'airfoilCoeffs.xlsx'];
bladename = 'IEA 63';
latticeType = 'Dong 3';
latticeSheet = 'LatticeProperties';

rho = 1.2;          %wind density - kg/m3
nu = 1.511e-5;      %kinematic viscosity of air at 20 C (kg/m-s)
%lambda = 1:1:10;    %tip speed ratio
B = 3; % number of blades
Re = 3e6;

opts = detectImportOptions(tfile,'sheet',bladename);
tTable = readtable(tfile,opts);

baseline = readtable(tfile);

for baselineRow = 1:length(baseline.BladeName)
    if strcmp(baseline.BladeName{baselineRow},bladename); break; end
end
hubrad = baseline.HubDiameter_m_(baselineRow)/2;
R = baseline.RotorDiameter_m_(baselineRow)/2;
bladelen = baseline.BladeLength_m_(baselineRow);

foilList = unique(tTable.Airfoil1);
for ii = 1:length(foilList)
    opts = detectImportOptions(airfoilfile,'sheet',foilList{ii});
    foilTable{ii} = readtable(airfoilfile,opts);
    foilTable{ii}.Re = Re*ones(size(foilTable{ii}.Re));
    %Re_design(ii) = mode(foilTable{ii}.Re);
end

opts = detectImportOptions(tfile,'sheet',latticeSheet);
latticeTable = readtable(tfile,opts);
for latticeRow = 1:length(latticeTable.Label)
    if strcmp(latticeTable.Label{latticeRow},latticeType); break; end
end

scalexp = latticeTable.scalingExponent(latticeRow);
scalcoeff = latticeTable.ScalingCoefficient(latticeRow);

eta = tTable.eta;
d_eta = eta;
d_eta(1) = (eta(2)-eta(1))/2;
d_eta(end) = (eta(end)-eta(end-1))/2;
d_eta(2:end-1) = (eta(3:end)-eta(1:end-2))/2;
dr = d_eta*bladelen;

rads = eta*bladelen+hubrad;
rR = rads/R;

Iflap = tTable.I_flapwise_;
EIflap = tTable.E11_flapwise__Nm2_;
flapThick = tTable.Abs_Thick_mm_/1000;

%% Find target material stiffness 
relden = [.01 .05 .1 .15 .2 .3];
legendLabels = cell(size(relden));
Esmin = zeros([length(relden),1]);
Esmax = zeros([length(relden),1]);
figure(1);clf;
for ii = 1:length(relden)
    Es = tTable.E11_flapwise__Nm2_./(scalcoeff*tTable.I_flapwise_*relden(ii)^scalexp);
    Es_edge = tTable.E22_edgewise__Nm2_./(scalcoeff*tTable.I_edgewise_*relden(ii)^scalexp);
    Esmax(ii) = max(Es);
    Esmin(ii) = min(Es);
    subplot(2,1,1);
    plot(eta,Es*1e-9);
    hold on;
    %subplot(1,3,2);
    %plot(eta,Es_edge*1e-9);
    %hold on;
    legendLabels{ii} = ['$\bar{\rho}$ = ' num2str(relden(ii))];
end
%ylim([0,500]);
%legend(num2str(relden'),'location','southwest');
%title('Material E (GPa) for Edgewise Stiffness');
subplot(2,1,1);
ylim([0,500]);
legend(legendLabels,'location','south','Interpreter','Latex');
title('Material E (GPa) for Flapwise Stiffness');
xlabel('ratio of blade span \eta');
ylabel('E_s (GPa)   ');
subplot(2,1,2);
plot(relden,Esmin*1e-9);
ylim([0,500]);
%hold on
%plot(relden,Esmax*1e-9);
title('Min Required E_s');
xlabel('relative density');
ylabel('E_s (GPa)');
%legend(['Min E_s';'Max E_s'])

%% Problem 1: Part A - Blade Design
Urated = 9.8;
lambda = 8.163; % TSR at rated speed
omega = 11.753;
theta_P0  = 0.870;
lambda_r = lambda*rR;    %local speed ratio
c = tTable.Chord_mm_/1000;    %blade chord length [m] 
sigma = B*c./(2*pi*rads);   %solidity [~]
alphas = 0:.1:12';

options = optimset('MaxFunEvals',1e6,'MaxIter',1e4, 'TolFun', 1e-6, 'TolX', 1e-6, 'Display','iter');

theta_T = tTable.Twist_deg_ - tTable.Twist_deg_(end);
pitch = theta_P0 - tTable.Twist_deg_(end) + tTable.Twist_deg_;

alpha_design = zeros(size(pitch));
alpha = alpha_design;
clList = zeros(size(pitch));
cdList = zeros(size(pitch));

for ii = 1:length(rR)
    foil1index = find(contains(foilList,tTable.Airfoil1(ii)));
    foil2index = find(contains(foilList,tTable.Airfoil2(ii)));
    foilinterp = tTable.InterpRatio(ii);
    cl = foilTable{foil1index}.Cl*(1-foilinterp)+foilTable{foil2index}.Cl*foilinterp;
    cd = foilTable{foil1index}.Cd*(1-foilinterp)+foilTable{foil2index}.Cd*foilinterp;
    clcd = cl./cd;
    aoaindex = min(find(clcd == max(clcd)));
    foilaoa = max(foilTable{foil1index}.AOA(aoaindex),0);
    alpha_design(ii) = foilaoa;%foil1aoa*(1-foilinterp)+foilaoa*foilinterp;
    clList(ii) = cl(aoaindex);
    cdList(ii) = cd(aoaindex);
    %Re = Re_design(foil1index)*(1-foilinterp)+Re_design(foil2index)*foilinterp;
    %CL_BEM = BEM_CL(deg2rad(alphas),deg2rad(theta_P0),deg2rad(theta_T(ii)),sigma(ii),lambda_r(ii),B,R,rads(ii));
    %CL_foil = interp1(foilTable{foil1index}.AOA,cl,alphas);
    %actualAlpha = interp1(CL_BEM-CL_foil,alphas,0);
    %alpha(ii) = actualAlpha;
    %foil.CL = cl;
    %foil.CD = cd;
    %foil.Re = ones(size(cl))*Re;
    %foil.alpha = deg2rad(foilTable{foil1index}.AOA);
    %alpha(ii) = fminsearch('CL_intersect',deg2rad(foilaoa),options,foil,deg2rad(theta_P0),...
    %    deg2rad(theta_T(ii)),sigma(ii),lambda_r(ii),B,R,rads(ii),Re);
end
%lift = clList * .5*rho*
%alpha = max(rad2deg(alpha),.1);
phi_design = pitch + alpha_design;

%[a_axial, a_angular, phi, F] = calculate_parameters(clList,cdList,deg2rad(alpha_design),...
%    deg2rad(theta_P0),deg2rad(theta_T),sigma,B,R,rads);
%% Thrust calcs
Urel = Urated*(1-1/3)./sind(phi_design);
%a_axial(isnan(a_axial))=1/3;
%a_angular(isnan(a_angular))=1/18;
%a_angular = max(a_angular,0);
lift = .5*rho*clList.*Urel.^2.*c;
drag = .5*rho*cdList.*Urel.^2.*c;

thrust = (lift.*cosd(phi_design) + drag.*sind(phi_design)).*dr;
%thrust = .5*2*pi*rho*Urated^2*4*a_axial.*(1-a_axial).*rads.*dr.*F;
totalthrust = sum(thrust);
flapwiseMoment = zeros(size(rads));
flapwise_dThdX = zeros(size(rads));
flapwise_Th = zeros(size(rads));
flapwiseDeflection = zeros(size(rads));
flapwisePeakStrain = zeros(size(rads));
for ii = 1:length(rads)
    flapwiseMoment(ii) = sum((rads(ii:end)-rads(ii)).*thrust(ii:end));
    flapwise_dThdX(ii) = -flapwiseMoment(ii)/EIflap(ii);
    if ii > 1
        flapwise_Th(ii) = flapwise_Th(ii-1) + flapwise_dThdX(ii)*dr(ii);
        flapwiseDeflection(ii) = flapwiseDeflection(ii-1)+flapwise_Th(ii)*dr(ii);
    end
end
flapwisePeakStrain = flapwiseMoment .* flapThick ./ EIflap;

torque = rads.*(lift.*sind(phi_design) - drag.*cosd(phi_design)).*dr;
%torque = 4*rho*Urated*pi*rads.^3.*dr.*a_angular.*(1-a_axial).*F*omega;
totaltorque = sum(torque);

CQ = B*totaltorque/(.5*rho*Urated^2*pi*R^3);
CT = B*totalthrust/(.5*rho*Urated^2*pi*R^2);

%masterfile = 'IEAonshore.xlsx';
%sheet = 'Cp-Ct-Cf-TSR Curves';
%opts = detectImportOptions(masterfile,'sheet',sheet);
%coeffTable = readtable(masterfile,opts);

%% Stiffness sensitivity
maxDeflection = zeros(length(rads)+1,1);
maxDeflection(1) = min(flapwiseDeflection);
dThdX = zeros(size(rads));
Th = zeros(size(rads));
deflection = zeros(size(rads));
figure(5);
for jj = 1:length(rads)
    EIreduced = EIflap;
    jj2 = min(length(rads),jj+4);
    EIreduced(jj:jj2) = EIflap(jj:jj2)*.5;
    for ii = 1:length(rads)
        dThdX(ii) = -flapwiseMoment(ii)/EIreduced(ii);
        if ii > 1
            Th(ii) = Th(ii-1) + dThdX(ii)*dr(ii);
            deflection(ii) = deflection(ii-1)+Th(ii)*dr(ii);
        end
    end
    maxDeflection(jj+1) = min(deflection);
    plot(eta,deflection);
    hold on;
end
figure(6);
plot(eta,(maxDeflection(2:end)/maxDeflection(1)-1)*100)
xlabel('\eta');
ylabel('Percent increase of tip deflection');
title('Increase in deflection caused by decrease in stiffness by 50%');