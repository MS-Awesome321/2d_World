function NI_USB_TC01(obj, event, probe,handles)

global Temperature;
global Power 

%figure(fig);
Temperature.time(1,end+1) = datenum(event.Data.time);
Temperature.data(1,end+1) = inputSingleScan(probe);


% % Yanyu Edit 10/28/22 to save temperature log, 
% Temp_YJ = Temperature.data';
% Time_YJ = Temperature.time';
% data = [Time_YJ(end),Temp_YJ(end)];
% % Write data to text file
% my_directory = 'D:\Dropbox (Princeton)\Wu Lab\Yanyu Project\SC Squid Pi-Phase Shift\Paper\Video\';  
% directory_YJ = [my_directory 'Temperature.csv'];
% % csvwrite(directory_YJ,data );
% dlmwrite(directory_YJ,data,'delimiter',',','-append');

%Read the current Temperature
handles.Temperature_Temperature.String = num2str(Temperature.data(1,end));

%Read the current power
handles.Power_Real.String = [num2str(Power.Pread(),'%.2f'),'W'];

if size(Temperature.time,2) > Temperature.windowsize  
    cla();
    plot(handles.Temperature_Axe,Temperature.time(end-Temperature.windowsize:end),Temperature.data(end-Temperature.windowsize:end),'bo-','MarkerSize',2);
    xlim([Temperature.time(end-Temperature.windowsize) inf]);
else
    plot(handles.Temperature_Axe,Temperature.time,Temperature.data,'bo-','MarkerSize',2);
end
xlabel('Time'); ylabel('Temperature(C)');title('Temperature vs Time');
dateFormat = 13;datetick('x',dateFormat);
hold on;
end