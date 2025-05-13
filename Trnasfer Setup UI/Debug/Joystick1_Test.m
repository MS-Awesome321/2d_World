ID = 2; 
Joy_Control_GLS = vrjoystick(ID);

while true
    
    for i = 1:1:3
     if abs(axis(Joy_Control_GLS,i)) > 0.99
         disp(num2str(i));
        break;

     end
    end
end