ID = 2; 
Joy_Control_GLS = vrjoystick(ID);

while true
    
    for i = 1:1:12
     if button(Joy_Control_GLS,i) == 1
         disp(num2str(i));
        break;

     end
    end
end