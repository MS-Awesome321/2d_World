function  focuscontrol = FocusControl()

baudrate                = 115200    ;
comport                 = 'COM5'    ;
mm_to_steps             = 32000*5   ; %%% microsteps and gear reduction
um_to_steps             = 32*5; 

FULL_STEPS_PER_ROTATION = 200       ;		%%factor applied before sending to serial
Z_STEPS_PER_MM_MIN		= 1         ;
Z_STEPS_PER_MM_MAX		= 1000000   ;
Z_STEPS_PER_MM_DEFAULT	= 32000     ;
Z_VELOCITY_MIN          = 8         ;
Z_VELOCITY_MAX          = 2047      ;
Z_VELOCITY_DEFAULT		= 256       ;

position                = 0         ; %%% saved position that will persist



focuscontrol.serialPort = InitializeFC(comport, baudrate);
%onCleanup(@() KillFC(focuscontrol.serialPort)); % Close the com port if an error occours

focuscontrol.rotateRelative = @rotateRelative;
focuscontrol.getPos = @getPos;
focuscontrol.setZero = @setZero;
focuscontrol.emergencystop = @emergencystop;
focuscontrol.getcoord = @getcoord;
focuscontrol.KillFC = @KillFC;
%%% Command Reference Section 
% commands are 8 bytes long: 
% command = [byte0 byte1 byte2 byte3 byte4 byte5 byte6 byte7 byte8];
% the meaning of each byte is below
% byte0 = 1; % address #, doesn't change
% byte1 = ?; % will change, describes type of action
%      Byte1 = 0;  // no sense
%      Byte1 = 1;  // rotate right
%      Byte1 = 2;  // rotate left
%      Byte1 = 3;  // stop
%      Byte1 = 4;  // move
%      Byte1 = 5;  // set axis parameter
%      Byte1 = 6;  // get axis parameter
%      Byte1 = 7;  // set stored axis parameter
%      Byte1 = 136; // get firmware version
% byte2 = 1; % 1 indicates relative motion, 0 is absolute motion
% byte3 = 0; % "motor index", always 0
% byte4 = 3; % bytes 4-7 are value of the command
% byte5 = 0;
% byte6 = 0;
% byte7 = 0;
% byte8 = 0; % checksum, calculated at the end
%%%


function fc = InitializeFC(comport, baudrate)
     fc = serial(comport);
     fc.Baudrate=baudrate;
     fc.StopBits=1;
     fc.Terminator='';
     fc.Parity='none';
     fc.FlowControl='none';
     fc.Timeout = 4;
     fopen(fc);
end

function KillFC(fc)
    fclose(fc);
    delete(fc);
    clear fc;
end


function checksum = CalculateChecksum(cmd)
    checksum = sum(cmd); %%% checksum is just sum of the command bytes
end

function cmd = StartCommand(cmdByte,stop)
    if stop == 1
        startcmd = [ 1 3 1 0]; 
    else
        startcmd = [ 1 4 1 0]; 
    end
   cmd = [startcmd cmdByte];
   % address, "move to", relative motion, motor index
end

function response = SendCommand(cmd)
    fwrite(focuscontrol.serialPort,char(cmd),'uint8');
    answer = fread(focuscontrol.serialPort, 9, 'uint8');
    errorcode = answer(3); 
    response = errorcode;

    if errorcode == 1
        response = 'Checksum incorrect';
    elseif errorcode == 2
        response = 'Invalid Command';
    elseif errorcode == 3
        response = 'Wrong Type';
    elseif errorcode == 4
        response = 'Invalid Value';
    elseif errorcode == 5 
        response = 'Configuration EEPROM locked';
    elseif errorcode == 6
        response = 'Command not avaialble';
    end
end

function value = um2byte(dist)
        microsteps = abs(dist)*um_to_steps;
        if dist == 0 
            dir = 1;
        else
            dir = (sign(dist)+1)/2; %%% convert +/-1 to 1 and 0
        end
        
        value = 0; %%% in case something goes wrong
        
        if abs(dist) > 2000 %% don't allow movement if it is > 2 mm
            value = 0;
        else
            if dir == 1
                value = dec2bin(microsteps,32);
            elseif dir == 0
                value = dec2bin((2^32-1) - microsteps,32);
                value = dec2bin(bin2dec(value)+1,32);
                value = value(end-31:end);
            else 
                value = 0;
            end
        end
end

function p = rotateRelative(dist)
        %%% distance must be in millimeters, convert to bytes
        value = um2byte(dist);
                
        %%% separate binary string into four separate bytes
        cmd   = [bin2dec(value(1:8)) bin2dec(value(9:16)) bin2dec(value(17:24)) bin2dec(value(25:32))]; 

        %%% add the beginning of the command and the checksum
        cmd = StartCommand(cmd,0);
        
        checksum = dec2bin(CalculateChecksum(cmd),8);
        checksum = bin2dec(checksum(end-7:end));
        cmd = [cmd checksum];
        
        response = SendCommand(cmd);
        
        position = position - dist;
        p = position;
end

function p = getPos()
    p = position;
end

function p = setZero()
    position = 0;
    p = position;
end

function emergencystop()
        value = um2byte(0); %%% value of zeros for the command
                
        %%% separate binary string into four separate bytes
        cmd   = [bin2dec(value(1:8)) bin2dec(value(9:16)) bin2dec(value(17:24)) bin2dec(value(25:32))]; 

        %%% add the beginning of the command and the checksum
        cmd = StartCommand(cmd,1);
        
        checksum = dec2bin(CalculateChecksum(cmd),8);
        checksum = bin2dec(checksum(end-7:end));
        cmd = [cmd checksum];
        
        response = SendCommand(cmd);
end


end

