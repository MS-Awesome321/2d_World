function [j] = IsMoving(h)

Com = ones(1,50);
judge = [];
for i = 1:1:50
    judge(1,end+1) = h.GetPosition_Position(0); 
end
    
if norm(Com.*mean(judge) - judge) < 0.01
    j = 0;
else
    j =1;
end

end

