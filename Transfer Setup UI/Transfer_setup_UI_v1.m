function varargout = Transfer_setup_UI_v1(varargin)
% TRANSFER_SETUP_UI_V1 MATLAB code for Transfer_setup_UI_v1.fig
%      TRANSFER_SETUP_UI_V1, by itself, creates a new TRANSFER_SETUP_UI_V1 or raises the existing
%      singleton*.
%
%      H = TRANSFER_SETUP_UI_V1 returns the handle to a new TRANSFER_SETUP_UI_V1 or the handle to
%      the existing singleton*.
%
%      TRANSFER_SETUP_UI_V1('CALLBACK',hObject,eventData,handles,...) calls the local
%      function named CALLBACK in TRANSFER_SETUP_UI_V1.M with the given input arguments.
%
%      TRANSFER_SETUP_UI_V1('Property','Value',...) creates a new TRANSFER_SETUP_UI_V1 or raises the
%      existing singleton*. 
%      Starting from the left, property value pairs are
%      applied to the GUI before Transfer_setup_UI_v1_OpeningFcn gets called.  An
%      unrecognized property name or invalid value makes property application
%      stop.  All inputs are passed to Transfer_setup_UI_v1_OpeningFcn via varargin.
%
%      *See GUI Options on GUIDE's Tools menu.  Choose "GUI allows only one
%      instance to run (singleton)".
%
% See also: GUIDE, GUIDATA, GUIHANDLES

% Edit the above text to modify the response to help Transfer_setup_UI_v1

% Last Modified by GUIDE v2.5 21-Jan-2019 12:32:05

% Begin initialization code - DO NOT EDIT
gui_Singleton = 1;
gui_State = struct('gui_Name',       mfilename, ...
                   'gui_Singleton',  gui_Singleton, ...
                   'gui_OpeningFcn', @Transfer_setup_UI_v1_OpeningFcn, ...
                   'gui_OutputFcn',  @Transfer_setup_UI_v1_OutputFcn, ...
                   'gui_LayoutFcn',  [] , ...
                   'gui_Callback',   []);
if nargin && ischar(varargin{1})
    gui_State.gui_Callback = str2func(varargin{1});
end

if nargout
    [varargout{1:nargout}] = gui_mainfcn(gui_State, varargin{:});
else
    gui_mainfcn(gui_State, varargin{:});
end
% End initialization code - DO NOT EDIT


% --- Executes just before Transfer_setup_UI_v1 is made visible.
function Transfer_setup_UI_v1_OpeningFcn(hObject, eventdata, handles, varargin)
% This function has no output args, see OutputFcn.
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
% varargin   command line arguments to Transfer_setup_UI_v1 (see VARARGIN)

% Choose default command line output for Transfer_setup_UI_v1
handles.output = hObject;

global Motor_Sample_x Motor_Sample_y fc Joy_Control_Sample Motor_Sample_Info Joy_Sample_Info;
global Motor_GLS_x Motor_GLS_y Motor_GLS_z Joy_Control_GLS Motor_GLS_Info Joy_GLS_Info;
global Temperature;
global FileRename;
global Power;
global Turret;

%%Initialize the Turret 
Turret = TurretControl();
%%Initialize the power supply
Power = PowerControl();
PrintInCommand(handles,'Power Supply is Ready to Use');

%% initialize the control for Sample and Focus Drive
%Create the UI for Sample 
fpos_sample = [100,100,450,750];
f_sample = figure('Position', fpos_sample,...
           'Menu','None',...
           'Name','Sample Side',...
           'visible','off');
Motor_Sample_x = actxcontrol('MGMotor.MGMotorCtrl.1',[20 500 400 200 ], f_sample);
Motor_Sample_y = actxcontrol('MGMotor.MGMotorCtrl.1',[20 250 400 200 ], f_sample);
%Initialize Motors of Sample
Motor_Sample_x.StartCtrl;
Motor_Sample_y.StartCtrl;
% Set the Serial Number for Sample Motor
SN_Sample_x = 27503936;
set(Motor_Sample_x,'HWSerialNum', SN_Sample_x);
SN_Sample_y = 27503951;
set(Motor_Sample_y,'HWSerialNum', SN_Sample_y);
% Indentify the device

Motor_Sample_y.Identify;
Motor_Sample_x.Identify;
%home the device 
Motor_Sample_x.SetHomeParams(0,2,1,0.449992,1);
Motor_Sample_y.SetHomeParams(0,2,1,0.449992,1);
Motor_Sample_x.MoveHome(0,0); 
Motor_Sample_y.MoveHome(0,0);
%set the jog mode
Motor_Sample_x.SetJogMode(0,1,1);
Motor_Sample_y.SetJogMode(0,1,1);

% Configure the Focus control
fc = FocusControl();%Initialize the focus drive
fc.setZero();

%% initialize the control for Glass Slide Motor
% Create the UI for glass slide motor 
fpos = [1400,100,450,750];
f_GLS = figure('Position', fpos,...
           'Menu','None',...
           'Name','Glass Slide Stage XYZ Control',...
           'visible','off');
Motor_GLS_x = actxcontrol('MGMOTOR.MGMotorCtrl.1',[20 500 400 200 ], f_GLS);
Motor_GLS_y = actxcontrol('MGMOTOR.MGMotorCtrl.1',[20 250 400 200 ], f_GLS);
Motor_GLS_z = actxcontrol('MGMOTOR.MGMotorCtrl.1',[20 20 400 200 ], f_GLS);
%% Initialize the three motors of Glass Slide
Motor_GLS_x.StartCtrl;
Motor_GLS_y.StartCtrl;
Motor_GLS_z.StartCtrl;
% Set the Serial Number for Glass slide
SN_GLS_x = 26001791;
set(Motor_GLS_x,'HWSerialNum', SN_GLS_x);
SN_GLS_y = 26001655;
set(Motor_GLS_y,'HWSerialNum', SN_GLS_y);
SN_GLS_z = 26001674;
set(Motor_GLS_z,'HWSerialNum', SN_GLS_z);
%Indentify the device
Motor_GLS_x.Identify;
Motor_GLS_y.Identify;
Motor_GLS_z.Identify;
%home the device 
Motor_GLS_x.SetHomeParams(0,1,4,1,0.0999998);
Motor_GLS_y.SetHomeParams(0,1,4,1,0.0999998);
Motor_GLS_z.SetHomeParams(0,1,4,1,0.0999998);
Motor_GLS_z.MoveHome(0,0);
Motor_GLS_x.MoveHome(0,0); 
Motor_GLS_y.MoveHome(0,0);
% 
while  (~IsHomed(Motor_Sample_x,0)) || (~IsHomed(Motor_Sample_y,0))
% wait while the motor is active; timeout to avoid dead loop
      pause(0.05);
end
PrintInCommand(handles,'Home Completed......')



%% Configure the Joystick for Sample Motor control
ID = 2; 
Joy_Control_Sample = vrjoystick(ID);
% Threshhold for joystick control being registered 
Joy_Sample_Info.thd_dcouple_Sample = 0.5;
Joy_Sample_Info.thd_move_Sample = 0.1;

%% Configure the joystick
ID = 1; 
Joy_Control_GLS = vrjoystick(ID);
% Threshhold for joystick control being registered 
Joy_GLS_Info.thd_dcouple_GLS = 0.5;
Joy_GLS_Info.thd_move_GLS = 0.1;
% Update handles structure
guidata(hObject, handles);

% UIWAIT makes Transfer_setup_UI_v1 wait for user response (see UIRESUME)
% uiwait(handles.figure1);


% --- Outputs from this function are returned to the command line.
function varargout = Transfer_setup_UI_v1_OutputFcn(hObject, eventdata, handles) 
% varargout  cell array for returning output args (see VARARGOUT);
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Get default command line output from handles structure
varargout{1} = handles.output;


% --- Executes on selection change in pop_mode.
function pop_mode_Callback(hObject, eventdata, handles)
% hObject    handle to pop_mode (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: contents = cellstr(get(hObject,'String')) returns pop_mode contents as cell array
%        contents{get(hObject,'Value')} returns selected item from pop_mode


% --- Executes during object creation, after setting all properties.
function pop_mode_CreateFcn(hObject, eventdata, handles)
% hObject    handle to pop_mode (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: popupmenu controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end







function X_Pos_Callback(hObject, eventdata, handles)
% hObject    handle to X_Pos (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of X_Pos as text
%        str2double(get(hObject,'String')) returns contents of X_Pos as a double


% --- Executes during object creation, after setting all properties.
function X_Pos_CreateFcn(hObject, eventdata, handles)
% hObject    handle to X_Pos (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end










function edit3_Callback(hObject, eventdata, handles)
% hObject    handle to edit3 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of edit3 as text
%        str2double(get(hObject,'String')) returns contents of edit3 as a double


% --- Executes during object creation, after setting all properties.
function edit3_CreateFcn(hObject, eventdata, handles)
% hObject    handle to edit3 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end




function edit4_Callback(hObject, eventdata, handles)
% hObject    handle to edit4 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of edit4 as text
%        str2double(get(hObject,'String')) returns contents of edit4 as a double


% --- Executes during object creation, after setting all properties.
function edit4_CreateFcn(hObject, eventdata, handles)
% hObject    handle to edit4 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function Sample_Vx_Callback(hObject, eventdata, handles)
% hObject    handle to Sample_Vx (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of Sample_Vx as text
%        str2double(get(hObject,'String')) returns contents of Sample_Vx as a double


% --- Executes during object creation, after setting all properties.
function Sample_Vx_CreateFcn(hObject, eventdata, handles)
% hObject    handle to Sample_Vx (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function Sample_Vy_Callback(hObject, eventdata, handles)
% hObject    handle to Sample_Vy (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of Sample_Vy as text
%        str2double(get(hObject,'String')) returns contents of Sample_Vy as a double


% --- Executes during object creation, after setting all properties.
function Sample_Vy_CreateFcn(hObject, eventdata, handles)
% hObject    handle to Sample_Vy (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



% --- Executes on button press in Set.
function Set_Callback(hObject, eventdata, handles)
% hObject    handle to Set (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
global Motor_Sample_x Motor_Sample_y fc Joy_Control_Sample Motor_Sample_Info Joy_Sample_Info;
global Motor_GLS_x Motor_GLS_y Motor_GLS_z Joy_Control_GLS Motor_GLS_Info Joy_GLS_Info;
global Temperature;
global FileRename;
global Turret;
% velocity for different Megnification 
Sample_Speed_M5 = 0.8; Sample_Acc_M5 = 0.8;
Sample_Speed_M20= 0.55; Sample_Acc_M20 = 0.55;
Sample_Speed_M50 = 0.449992/2.5; Sample_Acc_M50 = 0.449992/(2.5)^2;
Sample_Speed_M100 = 0.449992/5; Sample_Acc_M100= 0.449992/(5)^2;

% % % Sample_Speed_M5 = 0.6; Sample_Acc_M5 = 0.6;
% % % Sample_Speed_M20= 0.6; Sample_Acc_M20 = 0.6;
% % % Sample_Speed_M50 = 0.6/2.5; Sample_Acc_M50 = 0.6/(2.5)^2;
% % % Sample_Speed_M100 = 0.6/5; Sample_Acc_M100= 0.6/(5)^2;

% focus jog stepsize in um
Sample_Focus_M100 =0.25; 
Sample_Focus_M50 = 1;
Sample_Focus_M20 = 2.5;
Sample_Focus_M5 = 20;

%Choose the Moving Mode
Moving = handles.pop_mode.Value;
if Moving == 2
    Motor_Sample_Info(1).Acc = Sample_Acc_M5 ;
    Motor_Sample_Info(1).Speed = Sample_Speed_M5;
    Motor_Sample_Info(2).Acc = Sample_Acc_M5 ;
    Motor_Sample_Info(2).Speed = Sample_Speed_M5;
    fc.Speed = Sample_Focus_M5;
    PrintInCommand(handles,'Sample Motor Set to Objective 5* Mode');
elseif Moving == 3
    Motor_Sample_Info(1).Acc = Sample_Acc_M20 ;
    Motor_Sample_Info(1).Speed = Sample_Speed_M20;
    Motor_Sample_Info(2).Acc = Sample_Acc_M20 ;
    Motor_Sample_Info(2).Speed = Sample_Speed_M20;
    fc.Speed = Sample_Focus_M20;
        PrintInCommand(handles,'Sample Motor Set to Objective 20* Mode');
elseif Moving == 4
    Motor_Sample_Info(1).Acc = Sample_Acc_M50 ;
    Motor_Sample_Info(1).Speed = Sample_Speed_M50;
    Motor_Sample_Info(2).Acc = Sample_Acc_M50 ;
    Motor_Sample_Info(2).Speed = Sample_Speed_M50;
    fc.Speed = Sample_Focus_M50;
    PrintInCommand(handles,'Sample Motor Set to Objective 50* Mode');
elseif Moving == 5
    Motor_Sample_Info(1).Acc = Sample_Acc_M100 ;
    Motor_Sample_Info(1).Speed = Sample_Speed_M100;
    Motor_Sample_Info(2).Acc = Sample_Acc_M100 ;
    Motor_Sample_Info(2).Speed = Sample_Speed_M100;
    fc.Speed = Sample_Focus_M100;  
    PrintInCommand(handles,'Sample Motor Set to Objective 100* Mode');
elseif Moving == 6
    Motor_Sample_Info(1).Acc = str2double(handles.Sample_Vx.String) ;
    Motor_Sample_Info(1).Speed = str2double(handles.Sample_Accx.String);
    Motor_Sample_Info(2).Acc = str2double(handles.Sample_Vy.String) ;
    Motor_Sample_Info(2).Speed = str2double(handles.Sample_Accy.String);
    fc.Speed = str2double(handles.Focus_JogStepSize.String);  
    PrintInCommand(handles,'Sample Motor Set to Cunstom Designed Mode ');
else
    PrintInCommand(handles,'Please Choose One Mode');
end

%Choose the objective magnification 
Objective = handles.Objective_Pop.Value;
if Objective == 2
    Response = Turret.RotateToPosition(1);
    PrintInCommand(handles,Response);
elseif Objective == 3
    Response = Turret.RotateToPosition(2);
    PrintInCommand(handles,Response);
elseif Objective == 4
    Response = Turret.RotateToPosition(3);
    PrintInCommand(handles,Response);
elseif Objective == 5
    Response = Turret.RotateToPosition(4);
    PrintInCommand(handles,Response);
end

%display the chosen velocify and accelaraion
handles.Sample_Vx.String = num2str(Motor_Sample_Info(1).Speed,'%4.3f');
handles.Sample_Accx.String = num2str(Motor_Sample_Info(1).Acc,'%4.3f');
handles.Sample_Vy.String = num2str(Motor_Sample_Info(2).Speed,'%4.3f');
handles.Sample_Accy.String = num2str(Motor_Sample_Info(2).Acc,'%4.3f');
handles.Focus_JogStepSize.String = num2str(fc.Speed);
handles.X_Pos.String = num2str(Motor_Sample_x.GetPosition_Position(0));
handles.Y_Pos.String = num2str(Motor_Sample_y.GetPosition_Position(0));
handles.Z_Pos.String = '0';





%Get the speed and Acc by the fourth axis
Motor_GLS_Info.Speed = (axis(Joy_Control_GLS,4)+1)/2*1;
Motor_GLS_Info.Acc = ((axis(Joy_Control_GLS,4)+1)/2)^2*0.99;
%jog step size
Motor_GLS_Info.JogStepSize_Small = str2double(handles.GLS_JogStepSize_Small.String);
Motor_GLS_Info.JogStepSize_Big = str2double(handles.GLS_JogStepSize_Big.String);
Motor_GLS_Info.JogStepSize_Medium = str2double(handles.GLS_JogStepSize_Medium.String);
%Display the parameter
handles.GLS_X_Pos.String = num2str(Motor_GLS_x.GetPosition_Position(0));
handles.GLS_Y_Pos.String = num2str(Motor_GLS_y.GetPosition_Position(0));
handles.GLS_Z_Pos.String = num2str(Motor_GLS_z.GetPosition_Position(0));
handles.GLS_V.String = num2str(Motor_GLS_Info.Speed,'%5.4f');
handles.GLS_Acc.String = num2str(Motor_GLS_Info.Acc,'%5.4f');




% --- Executes on selection change in Command_Window.
function Command_Window_Callback(hObject, eventdata, handles)
% hObject    handle to Command_Window (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: contents = cellstr(get(hObject,'String')) returns Command_Window contents as cell array
%        contents{get(hObject,'Value')} returns selected item from Command_Window


% --- Executes during object creation, after setting all properties.
function Command_Window_CreateFcn(hObject, eventdata, handles)
% hObject    handle to Command_Window (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: listbox controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes on button press in Start.
function Start_Callback(hObject, eventdata, handles)
global Motor_Sample_x Motor_Sample_y fc Joy_Control_Sample Motor_Sample_Info Joy_Sample_Info;
global Motor_GLS_x Motor_GLS_y Motor_GLS_z Joy_Control_GLS Motor_GLS_Info Joy_GLS_Info;
global Temperature;
global FileRename;
global Power
global Turret
global Joy_Sample_x Joy_Sample_y Joy_Sample_focus Joy_Control_Sample

if handles.Start.Value == 1
    PrintInCommand(handles,'Joy Stick Control Start......');
    pause(1);
else 
    PrintInCommand(handles,'Joy Stick Control Stop......');
    pause(1);

end
while true && handles.Start.Value
%% Sample and Focus Control
    %Get the signal from joystick
    
    count = 0;
    try
        Joy_Sample_x = axis(Joy_Control_Sample,1);
        Joy_Sample_y = axis(Joy_Control_Sample,2);
%         Joy_Sample_focus = axis(Joy_Control_Sample,3);
    
    
    catch
        Motor_Sample_x.StopImmediate(0); 
        Motor_Sample_y.StopImmediate(0); 
        Motor_GLS_x.StopImmediate(0);
        Motor_GLS_y.StopImmediate(0);
        Motor_GLS_z.StopImmediate(0);
        PrintInCommand(handles,'Joy Stick Disconnected......');
        ReconnectJoystick(Joy_Control_Sample,count)
        PrintInCommand(handles,'Joy Stick Reconnected......');
        
        
        
        
    end


%     Joy_Sample_x = axis(Joy_Control_Sample,1);
%     Joy_Sample_y = axis(Joy_Control_Sample,2);
%     Joy_Sample_focus = axis(Joy_Control_Sample,3);
        
    

    
    
    
    %Choose Different Moving Mode by buttons 1,3,5,7; 3,2,8,7
    if button (Joy_Control_Sample,3) == 1
%         3
        handles.pop_mode.Value = 2;
        Set_Callback(hObject, eventdata, handles);
    elseif button (Joy_Control_Sample,2) == 1
%         2
        handles.pop_mode.Value = 3;
        Set_Callback(hObject, eventdata, handles);
    elseif button (Joy_Control_Sample,8) == 1
%         8
        handles.pop_mode.Value = 4;
        Set_Callback(hObject, eventdata, handles);
    elseif button (Joy_Control_Sample,7) == 1
        handles.pop_mode.Value = 5;
        Set_Callback(hObject, eventdata, handles);  
        
    %Choose Different Microscope Objective by buttons 2,4,6,8; 4,1,6,5
    elseif button (Joy_Control_Sample,4) == 1
%         4
        handles.Objective_Pop.Value = 2;
        Set_Callback(hObject, eventdata, handles);          
    elseif button (Joy_Control_Sample,1) == 1
%         1
        handles.Objective_Pop.Value = 3;
        Set_Callback(hObject, eventdata, handles);          
    elseif button (Joy_Control_Sample,6) == 1
        handles.Objective_Pop.Value = 4;
        Set_Callback(hObject, eventdata, handles);          
    elseif button (Joy_Control_Sample,5) == 1
%         5
        handles.Objective_Pop.Value = 5;
        Set_Callback(hObject, eventdata, handles);          
    end
    
    %Drive X stage continuously
     if Motor_Sample_x.GetPosition_Position(0) >= -0.1 && Motor_Sample_x.GetPosition_Position(0)<= 50.1
         %Continuously move wrp the seting velocity and accelation
         if abs(Joy_Sample_x) >= Joy_Sample_Info.thd_dcouple_Sample 
            Motor_Sample_x.SetVelParams(0,0,Motor_Sample_Info(1).Acc,Motor_Sample_Info(1).Speed);
             if Joy_Sample_x > Joy_Sample_Info.thd_move_Sample
                 Motor_Sample_x.MoveVelocity(0,2);
             elseif Joy_Sample_x < -Joy_Sample_Info.thd_move_Sample
                 Motor_Sample_x.MoveVelocity(0,1);
             end
         else
               Motor_Sample_x.StopImmediate(0); 
         end 
     elseif Motor_Sample_x.GetPosition_Position(0) < -0.1
         PrintInCommand(handles,'Sample X position < 0 is out of limit');
         Motor_Sample_x.SetAbsMovePos(0,0);
         Motor_Sample_x.MoveAbsolute(0,0);
         pause(0.1);
     elseif Motor_Sample_x.GetPosition_Position(0) > 50.1
         PrintInCommand(handles,'Sample X position >50 is out of limit');
         Motor_Sample_x.SetAbsMovePos(0,13);
         Motor_Sample_x.MoveAbsolute(0,0);
         pause(0.1);
     end

     
        %Drive Y stage continuously
      if Motor_Sample_y.GetPosition_Position(0) >= -0.1 && Motor_Sample_y.GetPosition_Position(0)<= 50.1
         %Continuously move wrp the seting velocity and accelation
         if abs(Joy_Sample_y) >= Joy_Sample_Info.thd_dcouple_Sample 
            Motor_Sample_y.SetVelParams(0,0,Motor_Sample_Info(2).Acc,Motor_Sample_Info(2).Speed);
             if Joy_Sample_y > Joy_Sample_Info.thd_move_Sample
                 Motor_Sample_y.MoveVelocity(0,2);
             elseif Joy_Sample_y < -Joy_Sample_Info.thd_move_Sample
                 Motor_Sample_y.MoveVelocity(0,1);
             end
         else
               Motor_Sample_y.StopImmediate(0); 
         end 
     elseif Motor_Sample_y.GetPosition_Position(0) < -0.1
         PrintInCommand(handles,'Sample Y position < 0 is out of limit');
         Motor_Sample_y.SetAbsMovePos(0,0);
         Motor_Sample_y.MoveAbsolute(0,0);
         pause(0.1);
     elseif Motor_Sample_y.GetPosition_Position(0) > 50.1
         PrintInCommand(handles,'Sample X position >50 is out of limit');
         Motor_Sample_y.SetAbsMovePos(0,13);
         Motor_Sample_y.MoveAbsolute(0,0); 
         pause(0.1);
      end
     
      
     %Drive the focus motor
      if Joy_Sample_focus > Joy_Sample_Info.thd_move_Sample
        fc.rotateRelative(fc.Speed); 
      elseif Joy_Sample_focus<-Joy_Sample_Info.thd_move_Sample
        fc.rotateRelative(-fc.Speed);
      elseif button(Joy_Control_Sample,9)
        fc.rotateRelative(fc.Speed);
      elseif button(Joy_Control_Sample,10)
        fc.rotateRelative(-fc.Speed);
      end
      
      %% Glass Slide Control
 
    Joy_GLS_x = axis(Joy_Control_GLS, 1);
    Joy_GLS_y = axis(Joy_Control_GLS,2);
    Joy_GLS_z = axis(Joy_Control_GLS,3);
    Motor_GLS_Info.Speed = (axis(Joy_Control_GLS,4)+1)/2*1;
    Motor_GLS_Info.Acc = ((axis(Joy_Control_GLS,4)+1)/2)^2*0.99;
    
%     Motor_GLS_Info.JogStepSize_Small = str2double(handles.GLS_JogStepSize_Small.String);
%     Motor_GLS_Info.JogStepSize_Big = str2double(handles.GLS_JogStepSize_Big.String);
    
    
    %set the motor into continous mode
%     Motor_GLS_x.SetJogMode(0,1,1);
%     Motor_GLS_y.SetJogMode(0,1,1); 
%     Motor_GLS_z.SetJogMode(0,1,1); 
%       
    % Move the stage 
    %Continously move x stage
    %if the current position of out of limit the return it back to the
    %neareast end 
    if Motor_GLS_x.GetPosition_Position(0) >= -0.1 && Motor_GLS_x.GetPosition_Position(0)<= 13.1
         %Continuously move wrp the seeting velocity and accelation
         if abs(Joy_GLS_x) >= Joy_GLS_Info.thd_dcouple_GLS 
            Motor_GLS_x.SetVelParams(0,0,Motor_GLS_Info.Acc,Motor_GLS_Info.Speed);
             if Joy_GLS_x > Joy_GLS_Info.thd_move_GLS
                 Motor_GLS_x.MoveVelocity(0,1);
             elseif Joy_GLS_x < -Joy_GLS_Info.thd_move_GLS
                 Motor_GLS_x.MoveVelocity(0,2);
             end
         %or else jog with two stepsize 1um or 25um
         elseif button(Joy_Control_GLS,5) == 1
               Motor_GLS_x.SetJogMode(0,2,1); 
               Motor_GLS_x.SetJogStepSize(0,Motor_GLS_Info.JogStepSize_Big);
               Motor_GLS_x.MoveJog(0,1);  
               %stop moving until the last jogging be finished
               while IsMoving(Motor_GLS_x)
                  pause(0.005) 
               end
         elseif button(Joy_Control_GLS,10) == 1
               Motor_GLS_x.SetJogMode(0,2,1); 
               Motor_GLS_x.SetJogStepSize(0,Motor_GLS_Info.JogStepSize_Big);
               Motor_GLS_x.MoveJog(0,2);  
                while IsMoving(Motor_GLS_x)
                  pause(0.005) 
               end
         elseif button(Joy_Control_GLS,11) == 1
               Motor_GLS_x.SetJogMode(0,2,1); 
               Motor_GLS_x.SetJogStepSize(0,Motor_GLS_Info.JogStepSize_Small);
               Motor_GLS_x.MoveJog(0,1);
                while IsMoving(Motor_GLS_x)
                  pause(0.005) 
               end
         elseif button(Joy_Control_GLS,16) == 1
               Motor_GLS_x.SetJogMode(0,2,1); 
               Motor_GLS_x.SetJogStepSize(0,Motor_GLS_Info.JogStepSize_Small);
               Motor_GLS_x.MoveJog(0,2);
                while IsMoving(Motor_GLS_x)
                  pause(0.005) 
               end
         else
               Motor_GLS_x.StopImmediate(0);
         end 
     elseif Motor_GLS_x.GetPosition_Position(0) < -0.1
         PrintInCommand(handles,'Glass Slide X position < 0 is out of limit');
         Motor_GLS_x.SetAbsMovePos(0,0);
         Motor_GLS_x.MoveAbsolute(0,0);   
         pause(0.1);
     elseif Motor_GLS_x.GetPosition_Position(0) > 13.1
         PrintInCommand(handles,'Glass Slide X position >13 is out of limit');
         Motor_GLS_x.SetAbsMovePos(0,13);
         Motor_GLS_x.MoveAbsolute(0,0);
         pause(0.1);
    end
    
    
    % Moving GLS_Y Stage
    if Motor_GLS_y.GetPosition_Position(0) >= -0.1 && Motor_GLS_y.GetPosition_Position(0)<= 13.1
         %Continuously move wrp the seeting velocity and accelation
         if abs(Joy_GLS_y) >= Joy_GLS_Info.thd_dcouple_GLS 
            Motor_GLS_y.SetVelParams(0,0,Motor_GLS_Info.Acc,Motor_GLS_Info.Speed);
             if Joy_GLS_y > Joy_GLS_Info.thd_move_GLS
                 Motor_GLS_y.MoveVelocity(0,2);
             elseif Joy_GLS_y < -Joy_GLS_Info.thd_move_GLS
                 Motor_GLS_y.MoveVelocity(0,1);
             end
         %or else jog with two stepsize 1um or 25um
         elseif button(Joy_Control_GLS,6) == 1
               Motor_GLS_y.SetJogMode(0,2,1); 
               Motor_GLS_y.SetJogStepSize(0,Motor_GLS_Info.JogStepSize_Big);
               Motor_GLS_y.MoveJog(0,1);  
               %stop moving until the last jogging be finished
               while IsMoving(Motor_GLS_y)
                  pause(0.005) 
               end
         elseif button(Joy_Control_GLS,9) == 1
               Motor_GLS_y.SetJogMode(0,2,1); 
               Motor_GLS_y.SetJogStepSize(0,Motor_GLS_Info.JogStepSize_Big);
               Motor_GLS_y.MoveJog(0,2);  
                while IsMoving(Motor_GLS_y)
                  pause(0.005) 
               end
         elseif button(Joy_Control_GLS,12) == 1
               Motor_GLS_y.SetJogMode(0,2,1); 
               Motor_GLS_y.SetJogStepSize(0,Motor_GLS_Info.JogStepSize_Small);
               Motor_GLS_y.MoveJog(0,1);
                while IsMoving(Motor_GLS_y)
                  pause(0.005) 
               end
         elseif button(Joy_Control_GLS,15) == 1
               Motor_GLS_y.SetJogMode(0,2,1); 
               Motor_GLS_y.SetJogStepSize(0,Motor_GLS_Info.JogStepSize_Small);
               Motor_GLS_y.MoveJog(0,2);
                while IsMoving(Motor_GLS_y)
                  pause(0.005) 
               end
         else
               Motor_GLS_y.StopImmediate(0);
         end 
     elseif Motor_GLS_y.GetPosition_Position(0) < -0.1
         PrintInCommand(handles,'Glass Slide Y position < 0 is out of limit');
         Motor_GLS_y.SetAbsMovePos(0,0);
         Motor_GLS_y.MoveAbsolute(0,0); 
         pause(0.1);
     elseif Motor_GLS_y.GetPosition_Position(0) > 13.1
         PrintInCommand(handles,'Glass Slide Y position >13 is out of limit');
         Motor_GLS_y.SetAbsMovePos(0,13);
         Motor_GLS_y.MoveAbsolute(0,0);
         pause(0.1);
    end      
     
    
    % Moving GLS_Z Stage
    if Motor_GLS_z.GetPosition_Position(0) >= -0.1 && Motor_GLS_z.GetPosition_Position(0)<= 13.1
         %Continuously move wrp the seeting velocity and accelation
         if abs(Joy_GLS_z) >= Joy_GLS_Info.thd_dcouple_GLS 
            Motor_GLS_z.SetVelParams(0,0,Motor_GLS_Info.Acc,Motor_GLS_Info.Speed);
             if Joy_GLS_z > Joy_GLS_Info.thd_move_GLS
                 Motor_GLS_z.MoveVelocity(0,2);
             elseif Joy_GLS_z < -Joy_GLS_Info.thd_move_GLS
                 Motor_GLS_z.MoveVelocity(0,1);
             end
         %or else jog with two stepsize 1um or 5um or  25um
         elseif button(Joy_Control_GLS,1) == 1
               Motor_GLS_z.SetJogMode(0,2,1); 
               Motor_GLS_z.SetJogStepSize(0,Motor_GLS_Info.JogStepSize_Medium);
               Motor_GLS_z.MoveJog(0,1);  
               %stop moving until the last jogging be finished
               while IsMoving(Motor_GLS_z)
                  pause(0.005) 
               end         
         elseif button(Joy_Control_GLS,2) == 1
               Motor_GLS_z.SetJogMode(0,2,1); 
               Motor_GLS_z.SetJogStepSize(0,Motor_GLS_Info.JogStepSize_Medium);
               Motor_GLS_z.MoveJog(0,2);  
               %stop moving until the last jogging be finished
               while IsMoving(Motor_GLS_z)
                  pause(0.005) 
               end         
         elseif button(Joy_Control_GLS,7) == 1
               Motor_GLS_z.SetJogMode(0,2,1); 
               Motor_GLS_z.SetJogStepSize(0,Motor_GLS_Info.JogStepSize_Big);
               Motor_GLS_z.MoveJog(0,1);  
               %stop moving until the last jogging be finished
               while IsMoving(Motor_GLS_z)
                  pause(0.005) 
               end
         elseif button(Joy_Control_GLS,8) == 1
               Motor_GLS_z.SetJogMode(0,2,1); 
               Motor_GLS_z.SetJogStepSize(0,Motor_GLS_Info.JogStepSize_Big);
               Motor_GLS_z.MoveJog(0,2);  
                while IsMoving(Motor_GLS_z)
                  pause(0.005) 
               end
         elseif button(Joy_Control_GLS,13) == 1
               Motor_GLS_z.SetJogMode(0,2,1); 
               Motor_GLS_z.SetJogStepSize(0,Motor_GLS_Info.JogStepSize_Small);
               Motor_GLS_z.MoveJog(0,1);
                while IsMoving(Motor_GLS_z)
                  pause(0.005) 
               end
         elseif button(Joy_Control_GLS,14) == 1
               Motor_GLS_z.SetJogMode(0,2,1); 
               Motor_GLS_z.SetJogStepSize(0,Motor_GLS_Info.JogStepSize_Small);
               Motor_GLS_z.MoveJog(0,2);
                while IsMoving(Motor_GLS_z)
                  pause(0.005) 
               end
         else
               Motor_GLS_z.StopImmediate(0);
         end 
     elseif Motor_GLS_z.GetPosition_Position(0) < -0.1
         PrintInCommand(handles,'Glass Slide Z position < 0 is out of limit');
         Motor_GLS_z.SetAbsMovePos(0,0);
         Motor_GLS_z.MoveAbsolute(0,0);  
         pause(0.1);
     elseif Motor_GLS_z.GetPosition_Position(0) > 13.1
         PrintInCommand(handles,'Glass Slide Z position >13 is out of limit');
         Motor_GLS_z.SetAbsMovePos(0,13);
         Motor_GLS_z.MoveAbsolute(0,0);
         pause(0.1);
    end      
    
      %Update the paprameters to UI 
      handles.X_Pos.String = num2str(Motor_Sample_x.GetPosition_Position(0));
      handles.Y_Pos.String = num2str(Motor_Sample_y.GetPosition_Position(0));
      handles.Z_Pos.String = num2str(fc.getPos());
      
      handles.GLS_X_Pos.String = num2str(Motor_GLS_x.GetPosition_Position(0));
      handles.GLS_Y_Pos.String = num2str(Motor_GLS_y.GetPosition_Position(0));
      handles.GLS_Z_Pos.String = num2str(Motor_GLS_z.GetPosition_Position(0));
      handles.GLS_V.String = num2str( Motor_GLS_Info.Speed,'%5.4f');
      handles.GLS_Acc.String = num2str(Motor_GLS_Info.Acc,'%5.4f');
      pause(0.005);

      

end


% hObject    handle to Start (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)




function edit9_Callback(hObject, eventdata, handles)
% hObject    handle to edit9 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of edit9 as text
%        str2double(get(hObject,'String')) returns contents of edit9 as a double


% --- Executes during object creation, after setting all properties.
function edit9_CreateFcn(hObject, eventdata, handles)
% hObject    handle to edit9 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end




function edit10_Callback(hObject, eventdata, handles)
% hObject    handle to edit10 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of edit10 as text
%        str2double(get(hObject,'String')) returns contents of edit10 as a double


% --- Executes during object creation, after setting all properties.
function edit10_CreateFcn(hObject, eventdata, handles)
% hObject    handle to edit10 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function Y_Pos_Callback(hObject, eventdata, handles)
% hObject    handle to Y_Pos (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of Y_Pos as text
%        str2double(get(hObject,'String')) returns contents of Y_Pos as a double


% --- Executes during object creation, after setting all properties.
function Y_Pos_CreateFcn(hObject, eventdata, handles)
% hObject    handle to Y_Pos (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function Sample_Accx_Callback(hObject, eventdata, handles)
% hObject    handle to Sample_Accx (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of Sample_Accx as text
%        str2double(get(hObject,'String')) returns contents of Sample_Accx as a double


% --- Executes during object creation, after setting all properties.
function Sample_Accx_CreateFcn(hObject, eventdata, handles)
% hObject    handle to Sample_Accx (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function Sample_Accy_Callback(hObject, eventdata, handles)
% hObject    handle to Sample_Accy (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of Sample_Accy as text
%        str2double(get(hObject,'String')) returns contents of Sample_Accy as a double


% --- Executes during object creation, after setting all properties.
function Sample_Accy_CreateFcn(hObject, eventdata, handles)
% hObject    handle to Sample_Accy (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end




function Z_Pos_Callback(hObject, eventdata, handles)
% hObject    handle to Z_Pos (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of Z_Pos as text
%        str2double(get(hObject,'String')) returns contents of Z_Pos as a double


% --- Executes during object creation, after setting all properties.
function Z_Pos_CreateFcn(hObject, eventdata, handles)
% hObject    handle to Z_Pos (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function Focus_JogStepSize_Callback(hObject, eventdata, handles)
% hObject    handle to Focus_JogStepSize (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of Focus_JogStepSize as text
%        str2double(get(hObject,'String')) returns contents of Focus_JogStepSize as a double


% --- Executes during object creation, after setting all properties.
function Focus_JogStepSize_CreateFcn(hObject, eventdata, handles)
% hObject    handle to Focus_JogStepSize (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes during object deletion, before destroying properties.
function figure1_DeleteFcn(hObject, eventdata, handles)
% hObject    handle to figure1 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
global Motor_Sample_x Motor_Sample_y fc Joy_Control_Sample Motor_Sample_Info Joy_Sample_Info;
global Motor_GLS_x Motor_GLS_y Motor_GLS_z Joy_Control_GLS Motor_GLS_Info Joy_GLS_Info;
global Temperature;
global FileRename;
global Power
global Turret

Power.OutputOff();
Power.Kill();
Turret.Kill();
fc.KillFC(fc.serialPort);
delete(Temperature.t);
close all;





% --- If Enable == 'on', executes on mouse press in 5 pixel border.
% --- Otherwise, executes on mouse press in 5 pixel border or over Start.
function Start_ButtonDownFcn(hObject, eventdata, handles)
% hObject    handle to Start (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)



function GLS_X_Pos_Callback(hObject, eventdata, handles)
% hObject    handle to GLS_X_Pos (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of GLS_X_Pos as text
%        str2double(get(hObject,'String')) returns contents of GLS_X_Pos as a double


% --- Executes during object creation, after setting all properties.
function GLS_X_Pos_CreateFcn(hObject, eventdata, handles)
% hObject    handle to GLS_X_Pos (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function GLS_Y_Pos_Callback(hObject, eventdata, handles)
% hObject    handle to GLS_Y_Pos (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of GLS_Y_Pos as text
%        str2double(get(hObject,'String')) returns contents of GLS_Y_Pos as a double


% --- Executes during object creation, after setting all properties.
function GLS_Y_Pos_CreateFcn(hObject, eventdata, handles)
% hObject    handle to GLS_Y_Pos (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function GLS_Z_Pos_Callback(hObject, eventdata, handles)
% hObject    handle to GLS_Z_Pos (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of GLS_Z_Pos as text
%        str2double(get(hObject,'String')) returns contents of GLS_Z_Pos as a double


% --- Executes during object creation, after setting all properties.
function GLS_Z_Pos_CreateFcn(hObject, eventdata, handles)
% hObject    handle to GLS_Z_Pos (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function GLS_V_Callback(hObject, eventdata, handles)
% hObject    handle to GLS_V (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of GLS_V as text
%        str2double(get(hObject,'String')) returns contents of GLS_V as a double


% --- Executes during object creation, after setting all properties.
function GLS_V_CreateFcn(hObject, eventdata, handles)
% hObject    handle to GLS_V (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function GLS_JogStepSize_Big_Callback(hObject, eventdata, handles)
% hObject    handle to GLS_JogStepSize_Big (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of GLS_JogStepSize_Big as text
%        str2double(get(hObject,'String')) returns contents of GLS_JogStepSize_Big as a double


% --- Executes during object creation, after setting all properties.
function GLS_JogStepSize_Big_CreateFcn(hObject, eventdata, handles)
% hObject    handle to GLS_JogStepSize_Big (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function GLS_Acc_Callback(hObject, eventdata, handles)
% hObject    handle to GLS_Acc (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of GLS_Acc as text
%        str2double(get(hObject,'String')) returns contents of GLS_Acc as a double


% --- Executes during object creation, after setting all properties.
function GLS_Acc_CreateFcn(hObject, eventdata, handles)
% hObject    handle to GLS_Acc (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function GLS_JogStepSize_Small_Callback(hObject, eventdata, handles)
% hObject    handle to GLS_JogStepSize_Small (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of GLS_JogStepSize_Small as text
%        str2double(get(hObject,'String')) returns contents of GLS_JogStepSize_Small as a double


% --- Executes during object creation, after setting all properties.
function GLS_JogStepSize_Small_CreateFcn(hObject, eventdata, handles)
% hObject    handle to GLS_JogStepSize_Small (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes on button press in pushbutton4.
function pushbutton4_Callback(hObject, eventdata, handles)
% hObject    handle to pushbutton4 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
global Motor_Sample_x Motor_Sample_y fc Joy_Control_Sample Motor_Sample_Info Joy_Sample_Info;
global Motor_GLS_x Motor_GLS_y Motor_GLS_z Joy_Control_GLS Motor_GLS_Info Joy_GLS_Info;
global Temperature;
global FileRename;
global Power;

Temperature.data = [];
Temperature.time = [];
Temperature.windowsize = str2double(handles.Temperature_WindowSize.String);%/s
Temperature.period = str2double(handles.Temperature_Period.String) ;%update every one seconds
Temperature.TaskToExcute = 30*24*60*60;

if get(hObject,'Value') == 1
    Power.OutputOn();
    PrintInCommand(handles,'Power Supply is On');
    pause(0.1);
    %find the device list
    devices = daq.getDevices;
    %create a session
    TC01 = daq.createSession('ni');
    %add the input channel
    addAnalogInputChannel(TC01,'Dev1',0, 'Thermocouple');
    %specify the channel and its parameters
    TC01_1 = TC01.Channels(1);
    TC01_1.ThermocoupleType = 'K';
    TC01_1.Units = 'Celsius';
    PrintInCommand(handles,'Temperature Sensor is On');
    
    %set up the timer
    t = timer( 'Period', Temperature.period, 'TasksToExecute', Temperature.TaskToExcute, 'ExecutionMode', 'fixedRate');
    t.TimerFcn = {@NI_USB_TC01,TC01,handles};
    start(t);
    Temperature.t = t;  
    
else
    

    
    Power.OutputOff();
    PrintInCommand(handles,'Power Supply is Off');
    stop(Temperature.t);
    cla(handles.Temperature_Axe);
    PrintInCommand(handles,'Temperature Sensor is Off');
    pause(0.1);
    

    
    
end




% Hint: get(hObject,'Value') returns toggle state of pushbutton4


% --- Executes on button press in Power_Set.
function Power_Set_Callback(hObject, eventdata, handles)


global Power
Power.Pset(str2double(handles.Power_ToSet.String));
pause(0.5);
Power_Str = ['Power Supply is Set to ',num2str(Power.Pread(),'%.2f'),'W'];
PrintInCommand(handles,Power_Str);



% hObject    handle to Power_Set (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)



function Power_ToSet_Callback(hObject, eventdata, handles)
% hObject    handle to Power_ToSet (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of Power_ToSet as text
%        str2double(get(hObject,'String')) returns contents of Power_ToSet as a double


% --- Executes during object creation, after setting all properties.
function Power_ToSet_CreateFcn(hObject, eventdata, handles)
% hObject    handle to Power_ToSet (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function Temperature_Period_Callback(hObject, eventdata, handles)
% hObject    handle to Temperature_Period (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of Temperature_Period as text
%        str2double(get(hObject,'String')) returns contents of Temperature_Period as a double


% --- Executes during object creation, after setting all properties.
function Temperature_Period_CreateFcn(hObject, eventdata, handles)
% hObject    handle to Temperature_Period (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes on button press in pushbutton7.
function pushbutton7_Callback(hObject, eventdata, handles)
% hObject    handle to pushbutton7 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
global Motor_Sample_x Motor_Sample_y fc Joy_Control_Sample Motor_Sample_Info Joy_Sample_Info;
global Motor_GLS_x Motor_GLS_y Motor_GLS_z Joy_Control_GLS Motor_GLS_Info Joy_GLS_Info;
global Temperature;
global FileRename;

date =clock();
formatOut1 = 'yyyy_mm_dd';formatOut2 = 'mm-dd-yy';
FileRename.Date = {};
FileRename.Date{1} = datestr(now,formatOut1);
FileRename.Date{2} = datestr(now,formatOut2);
FileRename.LoadPath = uigetdir(['C:\Users\admin\Desktop\Microscope_Images\',FileRename.Date{1}]);
PrintInCommand(handles,['LoadPath is set to',FileRename.LoadPath]);


% --- Executes on button press in pushbutton8.
function pushbutton8_Callback(hObject, eventdata, handles)
global Motor_Sample_x Motor_Sample_y fc Joy_Control_Sample Motor_Sample_Info Joy_Sample_Info;
global Motor_GLS_x Motor_GLS_y Motor_GLS_z Joy_Control_GLS Motor_GLS_Info Joy_GLS_Info;
global Temperature;
global FileRename;

FileRename.SavePath = uigetdir(['C:\Users\admin\Desktop\Yanyu Jia']);
PrintInCommand(handles, ['Save Path is Set to ', FileRename.SavePath]);

% hObject    handle to pushbutton8 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)



function FileRenema_SampleNum_Callback(hObject, eventdata, handles)
% hObject    handle to FileRenema_SampleNum (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of FileRenema_SampleNum as text
%        str2double(get(hObject,'String')) returns contents of FileRenema_SampleNum as a double


% --- Executes during object creation, after setting all properties.
function FileRenema_SampleNum_CreateFcn(hObject, eventdata, handles)
% hObject    handle to FileRenema_SampleNum (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function FileRename_FlakeNum_Callback(hObject, eventdata, handles)
% hObject    handle to FileRename_FlakeNum (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of FileRename_FlakeNum as text
%        str2double(get(hObject,'String')) returns contents of FileRename_FlakeNum as a double


% --- Executes during object creation, after setting all properties.
function FileRename_FlakeNum_CreateFcn(hObject, eventdata, handles)
% hObject    handle to FileRename_FlakeNum (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function FileRename_RelToRef_Callback(hObject, eventdata, handles)
% hObject    handle to FileRename_RelToRef (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of FileRename_RelToRef as text
%        str2double(get(hObject,'String')) returns contents of FileRename_RelToRef as a double


% --- Executes during object creation, after setting all properties.
function FileRename_RelToRef_CreateFcn(hObject, eventdata, handles)
% hObject    handle to FileRename_RelToRef (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function FileRename_Setup_Callback(hObject, eventdata, handles)
% hObject    handle to FileRename_Setup (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of FileRename_Setup as text
%        str2double(get(hObject,'String')) returns contents of FileRename_Setup as a double


% --- Executes during object creation, after setting all properties.
function FileRename_Setup_CreateFcn(hObject, eventdata, handles)
% hObject    handle to FileRename_Setup (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes on button press in pushbutton9.
function pushbutton9_Callback(hObject, eventdata, handles)
% hObject    handle to pushbutton9 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hint: get(hObject,'Value') returns toggle state of pushbutton9


% --- Executes on button press in pushbutton10.
function pushbutton10_Callback(hObject, eventdata, handles)
% hObject    handle to pushbutton10 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hint: get(hObject,'Value') returns toggle state of pushbutton10


% --- Executes on button press in pushbutton11.
function pushbutton11_Callback(hObject, eventdata, handles)

% hObject    handle to pushbutton11 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
global Motor_Sample_x Motor_Sample_y fc Joy_Control_Sample Motor_Sample_Info Joy_Sample_Info;
global Motor_GLS_x Motor_GLS_y Motor_GLS_z Joy_Control_GLS Motor_GLS_Info Joy_GLS_Info;
global Temperature;
global FileRename;
date =clock();
formatOut1 = 'mm_dd_yy';formatOut2 = 'yy-mm-dd';
FileRename.Date{1} = datestr(now,formatOut1);
FileRename.Date{2} = datestr(now,formatOut2);
FileRename.Type = handles.FileRename_Type.String{handles.FileRename_Type.Value};
FileRename.File = dir([FileRename.LoadPath,'/*',FileRename.Type]);

FileRename.SampleName = handles.FileRename_SampleName.String;
FileRename.SampleNum = handles.FileRenema_SampleNum.String;
FileRename.FlakeNum = ['Flake',handles.FileRename_FlakeNum.String];
FileRename.RelToRef = handles.FileRename_RelToRef.String;
FileRename.Setup = handles.FileRename_Setup.String;
FileRename.ReferenceCorner = handles.FileRename_ReferenceCorner.String{handles.FileRename_ReferenceCorner.Value};
FileRename.Magnification = {'M5','M20','M50','M100'};


%File Name of the Sample
FileRename.SampleFileName = [FileRename.Date{2},'_',FileRename.SampleName,FileRename.SampleNum,'_',FileRename.ReferenceCorner];


FileRename.MovePath = fullfile(FileRename.SavePath,FileRename.SampleName,FileRename.SampleFileName);

[status,msg] = mkdir(FileRename.MovePath);

if status == 0
    PrintInCommand(handles,['Error when create destination dir:',msg]);
else
    PrintInCommand(handles,'Destination Directory is created:');
    PrintInCommand(handles,FileRename.MovePath);
end


[status,msg] = mkdir(fullfile(FileRename.LoadPath,FileRename.SampleName));
if status == 0
    PrintInCommand(handles,['Error when create copy dir:',msg]);
else
    PrintInCommand(handles,'Copy Directory is created:');
    PrintInCommand(handles,fullfile(FileRename.LoadPath,FileRename.SampleName));
end




% Change Name of Image and move it to save dir and copy dir
for i = 1:1:4
    
    
    NewImageName = [FileRename.Date{2},'_',FileRename.SampleName,FileRename.SampleNum,'_',...
    FileRename.FlakeNum,'_',FileRename.Magnification{i} ,'_',FileRename.ReferenceCorner,'_',FileRename.RelToRef...
    ,'_',FileRename.Setup,FileRename.Type];
    
    
    NewImageDir = [FileRename.MovePath,'\',NewImageName];
    OldImageDir = fullfile(FileRename.File(end-i+1).folder,FileRename.File(end-i+1).name);
    CopyImageDir = fullfile(FileRename.File(end-i+1).folder,'\',FileRename.SampleName,'\',NewImageName);
    
    

    
    
    
    [status2,msg] = movefile(OldImageDir,NewImageDir);
    
    if status2 == 0
        PrintInCommand(handles,['Error when move file:',msg]);
    elseif status2 == 1
        p = [FileRename.File(i).name,'is moved successfully'];
        PrintInCommand(handles,p);
        pause(0.5);
    end
    
    
    
    [status,msg] = copyfile(NewImageDir,CopyImageDir);
    
    if status == 0
        PrintInCommand(handles,['Error when Copy file:',msg]);
    elseif status == 1
        p = [FileRename.File(i).name,'is copied successfully'];
        PrintInCommand(handles,p);
        pause(0.5);
    end
    
    
end
 handles.FileRename_FlakeNum.String = num2str(str2double(handles.FileRename_FlakeNum.String)+1);






function FileRename_ReferencePoint_Y_Callback(hObject, eventdata, handles)
% hObject    handle to FileRename_ReferencePoint_Y (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of FileRename_ReferencePoint_Y as text
%        str2double(get(hObject,'String')) returns contents of FileRename_ReferencePoint_Y as a double


% --- Executes during object creation, after setting all properties.
function FileRename_ReferencePoint_Y_CreateFcn(hObject, eventdata, handles)
% hObject    handle to FileRename_ReferencePoint_Y (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function FileRename_ReferencePoint_X_Callback(hObject, eventdata, handles)
% hObject    handle to FileRename_ReferencePoint_X (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of FileRename_ReferencePoint_X as text
%        str2double(get(hObject,'String')) returns contents of FileRename_ReferencePoint_X as a double


% --- Executes during object creation, after setting all properties.
function FileRename_ReferencePoint_X_CreateFcn(hObject, eventdata, handles)
% hObject    handle to FileRename_ReferencePoint_X (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes on selection change in FileRename_Type.
function FileRename_Type_Callback(hObject, eventdata, handles)
% hObject    handle to FileRename_Type (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: contents = cellstr(get(hObject,'String')) returns FileRename_Type contents as cell array
%        contents{get(hObject,'Value')} returns selected item from FileRename_Type


% --- Executes during object creation, after setting all properties.
function FileRename_Type_CreateFcn(hObject, eventdata, handles)
% hObject    handle to FileRename_Type (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: popupmenu controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes on selection change in FileRename_ReferenceCorner.
function FileRename_ReferenceCorner_Callback(hObject, eventdata, handles)
% hObject    handle to FileRename_ReferenceCorner (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: contents = cellstr(get(hObject,'String')) returns FileRename_ReferenceCorner contents as cell array
%        contents{get(hObject,'Value')} returns selected item from FileRename_ReferenceCorner


% --- Executes during object creation, after setting all properties.
function FileRename_ReferenceCorner_CreateFcn(hObject, eventdata, handles)
% hObject    handle to FileRename_ReferenceCorner (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: popupmenu controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes on button press in text33.
function text33_Callback(hObject, eventdata, handles)

global Motor_Sample_x Motor_Sample_y fc Joy_Control_Sample Motor_Sample_Info Joy_Sample_Info;
global Motor_GLS_x Motor_GLS_y Motor_GLS_z Joy_Control_GLS Motor_GLS_Info Joy_GLS_Info;
global Temperature;
global FileRename;

FileRename.ReferencePoint = {};
FileRename.ReferencePoint{1} = num2str(Motor_Sample_x.GetPosition_Position(0));
FileRename.ReferencePoint{2} = num2str(Motor_Sample_y.GetPosition_Position(0));
handles.FileRename_ReferencePoint_X.String = FileRename.ReferencePoint{1};
handles.FileRename_ReferencePoint_Y.String = FileRename.ReferencePoint{2};
Reference = ['Reference Position is Set to X = ',FileRename.ReferencePoint{1},',Y = ',FileRename.ReferencePoint{2}];
PrintInCommand(handles,Reference);
% hObject    handle to text33 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)


% --- Executes during object creation, after setting all properties.
function Temperature_Temperature_CreateFcn(hObject, eventdata, handles)
% hObject    handle to Temperature_Temperature (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called


% --- Executes during object creation, after setting all properties.
function edit40_CreateFcn(hObject, eventdata, handles)
% hObject    handle to edit40 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called



function GLS_JogStepSize_Medium_Callback(hObject, eventdata, handles)
% hObject    handle to GLS_JogStepSize_Medium (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of GLS_JogStepSize_Medium as text
%        str2double(get(hObject,'String')) returns contents of GLS_JogStepSize_Medium as a double


% --- Executes during object creation, after setting all properties.
function GLS_JogStepSize_Medium_CreateFcn(hObject, eventdata, handles)
% hObject    handle to GLS_JogStepSize_Medium (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes on selection change in Objective_Pop.
function Objective_Pop_Callback(hObject, eventdata, handles)
% hObject    handle to Objective_Pop (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: contents = cellstr(get(hObject,'String')) returns Objective_Pop contents as cell array
%        contents{get(hObject,'Value')} returns selected item from Objective_Pop


% --- Executes during object creation, after setting all properties.
function Objective_Pop_CreateFcn(hObject, eventdata, handles)
% hObject    handle to Objective_Pop (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: popupmenu controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end
