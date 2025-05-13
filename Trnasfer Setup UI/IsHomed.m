function [j] = IsHomed(h,x)
judge = [];
     com = ones(1,50).* x;
     for i = 1:1:50
        judge(1,end+1) = h.GetPosition_Position(0); 
     end
     if norm(com-judge) < 0.001
        j = 1;  
     else 
        j = 0;
     end
end

