clear, close all

currentpath = fileparts(matlab.desktop.editor.getActiveFilename);
tfile = [currentpath filesep 'TradeStudyDocs', filesep, 'Product Trade Study Data.xlsx'];
bladename = 'IEA 63';

scalingCoef = 0.064042242801839;
scalingExp = 1.01;
rhobar = [.01 .05 .1 .15 .2 .25 .3];
matDensity = 1390;
E_s = 20685e6;
bladelen = 63;

opts = detectImportOptions(tfile,'sheet',bladename);
tTable = readtable(tfile,opts);

eta = tTable.eta;
dr = eta;
dr(1) = bladelen*(eta(2)-eta(1))/2;
dr(end) = bladelen*(eta(end)-eta(end-1))/2;
dr(2:end-1) = bladelen*(eta(3:end)-eta(1:end-2))/2;

bladeStiffness = tTable.E11_flapwise__Nm2_;
blademass = tTable.Mass_kg_m_;
bladeSecAr = tTable.sectionArea_m2_;
bladeDensity = blademass./bladeSecAr;

latticeI = tTable.I_flapwise_;

figure(1);
semilogy(eta,bladeStiffness);
hold on;
leg = cell([length(rhobar)+1,1]);
leg{1} = 'Actual Blade Stiffness';

for ii = 1:length(rhobar)
    %effDensity = rhobar(ii)*matDensity;
    latticeE = E_s*scalingCoef*rhobar(ii)^scalingExp;
    latticeEI = latticeI*latticeE;
    semilogy(eta,latticeEI);
    leg{ii+1} = ['$\bar{\rho}$ = ' num2str(rhobar(ii))];
end
xlabel('\eta');
ylabel('Flapwise EI stiffness (Nm^2)')
legend(leg,'Interpreter','Latex','location','southwest');