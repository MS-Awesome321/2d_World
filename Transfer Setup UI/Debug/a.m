ID = 2; 
Joy_Control_GLS = vrjoystick(ID);

while true
    
    for i = 1:1:16
     if button(Joy_Control_GLS,i) == 1
        break;

     end

    end
    display(['Button', num2str(i)])
%     
%     Joy_GLS_x = axis(Joy_Control_GLS, 1);
%     Joy_GLS_y = axis(Joy_Control_GLS,2);
%     Joy_GLS_z = axis(Joy_Control_GLS,3);
% 
%     display(['Z Axis', num2str(Joy_GLS_z)]);
    
    
    
    
    
end