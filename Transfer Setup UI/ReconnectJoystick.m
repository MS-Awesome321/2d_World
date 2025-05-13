function [Connected] = ReconnectJoystick(Joy_Control_Sample,count)

global Motor_Sample_x Motor_Sample_y fc Joy_Control_Sample Motor_Sample_Info Joy_Sample_Info;
global Motor_GLS_x Motor_GLS_y Motor_GLS_z Joy_Control_GLS Motor_GLS_Info Joy_GLS_Info;
global Temperature;
global FileRename;
global Power
global Turret
global Joy_Sample_x Joy_Sample_y Joy_Sample_focus Joy_Control_Sample

 try
    ID = 2; 
    Joy_Control_Sample = vrjoystick(ID);
    % Threshhold for joystick control being registered 
    Joy_Sample_Info.thd_dcouple_Sample = 0.5;
    Joy_Sample_Info.thd_move_Sample = 0.1;
    Joy_Sample_x = axis(Joy_Control_Sample,1);
    Joy_Sample_y = axis(Joy_Control_Sample,2);
%     Joy_Sample_focus = axis(Joy_Control_Sample,3);
    Connected = 1;
    
    
 catch
    
    warning('Joy Stick Reconnecting......');
    count = count + 1;
    pause(1)
    ReconnectJoystick(Joy_Control_Sample,count);
    if count > 60
        return; 
    end
end

