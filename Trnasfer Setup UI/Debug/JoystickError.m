    try
    Joy_Sample_x = axis(Joy_Control_Sample,1);
    Joy_Sample_y = axis(Joy_Control_Sample,2);
    Joy_Sample_focus = axis(Joy_Control_Sample,3);
        
    catch
    warning('Joystick Disconencted');
    pause(1)
    Joy_Sample_x = axis(Joy_Control_Sample,1);
    Joy_Sample_y = axis(Joy_Control_Sample,2);
    Joy_Sample_focus = axis(Joy_Control_Sample,3);
    end