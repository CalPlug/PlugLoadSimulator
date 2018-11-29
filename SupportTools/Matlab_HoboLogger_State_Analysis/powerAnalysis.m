% Quick histogram for power usage in multiple states of operation for a
% single device

%Usage - import data in, this script assumes 1 sec integration time per
%reading.  Variables for inputted data should be in a set of variables of
%identical length for the collected dataset.
%To do this, Import the logger file into Excel so that each column
%represents a 
%++++++++++++++++++++++
%   Index  - incremented identifying number for the sample
%   DateTime - this needs to be in excel DateTime format!
%   ActivePowerWh
%   ActiveEnergyVA
%   ApparentPowerVA
%   PowerFactor
%   RMSCurrent
%   RMSVoltage
%   PowerFactorPF
%++++++++++++++++++++++

figure (1) % Open Figure Window for the first generated figure
MATLABDateTime = x2mdate(DateTime, 1);
plot (MATLABDateTime, ActivePowerW)
datetick('x', 'HH', 'keeplimits')
xlabel('Date/Time (Hr)')
ylabel('Power Consumption (Watts)')

ActivePowerWSorted = sort(ActivePowerW); 
figure (2) % Open Figure Window for the second generated figure
plot (Index, ActivePowerWSorted)
ylabel('Power Consumption (Watts)')
xlabel('Ordered Data Points')

clusters=5;
[idx,C,sumd,D] = kmeans(ActivePowerW,clusters,'MaxIter',100000,'Replicates',2);
%Display clusters
fprintf ('A Total of %s clusters were selected by choice, here are the boundaries:\n',num2str(clusters))
C  %Display the clusters

ActivePowerkmeanscombinedTEMP = {Index, MATLABDateTime, ActivePowerW, idx};
ActivePowerkmeanscombined = cat(2,ActivePowerkmeanscombinedTEMP{:}); %concatonate with cluster info
clear ActivePowerkmeanscombinedTEMP %Clear the temp variable
ActivePowerkmeanscombinedSorted = sortrows(ActivePowerkmeanscombined,3);
ActivePowerkmeanscombinedSortedCluster = sortrows(ActivePowerkmeanscombined,4);

figure (3);
nbins=100;
hist(ActivePowerkmeanscombined(:,3),nbins);
ylabel('Number of Samples')
xlabel('Power Consumption (Watts)')
hold on
%histfit(ActivePowerkmeanscombined(:,3),nbins); %Enable to overlay fitting
%function on histogram
hold off

figure (4); % Open Figure Window for the first generated figure
plot (ActivePowerkmeanscombined(:,2), ActivePowerkmeanscombined(:,3))
datetick('x', 'HH', 'keeplimits')
xlabel('Date/Time (Hr)')

hold on

%Plot Symbols for the points represented by the clusters
for i=1:length(ActivePowerkmeanscombined)
    if (ActivePowerkmeanscombined(i,4)==5)
        plot (ActivePowerkmeanscombined(i,2),ActivePowerkmeanscombined(i,3),'mo');
    elseif(ActivePowerkmeanscombined(i,4)==4)
        plot (ActivePowerkmeanscombined(i,2),ActivePowerkmeanscombined(i,3),'m+');
    elseif(ActivePowerkmeanscombined(i,4)==3)
        plot (ActivePowerkmeanscombined(i,2),ActivePowerkmeanscombined(i,3),'ms');
    elseif(ActivePowerkmeanscombined(i,4)==2)
        plot (ActivePowerkmeanscombined(i,2),ActivePowerkmeanscombined(i,3),'mx');
    elseif(ActivePowerkmeanscombined(i,4)==1)
        plot (ActivePowerkmeanscombined(i,2),ActivePowerkmeanscombined(i,3),'m*');
    end
end 
%Reference Lines for the determined clusters
hlineC1 = refline(0,C(1));
hlineC2 = refline(0,C(2));
hlineC3 = refline(0,C(3));
hlineC4 = refline(0,C(4));
hlineC5 = refline(0,C(5));

hold off

MeanPower = mean ((ActivePowerkmeanscombined(:,3)))
StdDeviation= std(ActivePowerkmeanscombined(:,3))

%Threshold Calculation of Mean - Used to find values for power states where
%min/max wattage values are known
Data = (ActivePowerkmeanscombined(:,3)); %specify data to process
mask = (ActivePowerkmeanscombined(:,3) > 0 && ActivePowerkmeanscombined(:,3) < 200); %Limiting expression to mask relevent values in the data set
Data(~mask) = 0;
ThresholdedMean = sum(Data, 1) ./ sum(mask, 1)
ThresholdedStdDeviation = std(Data)
clear Data %Clear the temp variable
clear mask %Clear the temp variable

