function Power = PowerControl()

Baudrate = 9600;
Comport = 'COM6';
Timeout = 3;
Terminator = 'LF';
Resistance = 11.3;

%initialize the serial port
Power.SerialPort = serial(Comport,'Baudrate',Baudrate,'Terminator',Terminator,'Timeout', Timeout);
fopen(Power.SerialPort);


Power.Iset = @Iset;
Power.Vset = @Vset;
Power.Pset = @Pset;
Power.Iread = @Iread;
Power.Vread = @Vread;
Power.Pread = @Pread;
Power.OutputOn = @OutputOn;
Power.OutputOff = @OutputOff;
Power.Kill = @Kill;

pause(0.5);
Power.Iset(4);
pause(0.5);
Power.Vset(0);
pause(0.5);
Power.OutputOff();
pause(0.5)


    function Iset(I)
        
        Cmd = ['ISET1:',num2str(I,'%5.3f'),'\n'];
        fwrite(Power.SerialPort,Cmd);
        
    end

    function Vset(V)
       
        Cmd = ['VSET1:',num2str(V,'%05.2f'),'\n'];
        fwrite(Power.SerialPort,Cmd);
        
    end

    function Pset(P)
        
       V = sqrt(P*Resistance); 
       Vset(V);
        
    end

    function I = Iread()
       
        fwrite(Power.SerialPort,'IOUT1?\n'); 
        I = str2double(fscanf(Power.SerialPort));
        
    end

    function V = Vread()
        
        fwrite(Power.SerialPort,'VOUT1?\n');
        V = str2double(fscanf(Power.SerialPort));
    
    end

    function P = Pread()
    
        P = Iread()*Vread();
        
    end

    function OutputOn()
        
       fwrite(Power.SerialPort,'OUTPUT1\n'); 
        
    end

    function OutputOff()
        
       fwrite(Power.SerialPort,'OUTPUT0\n'); 
        
    end



    function Kill()
       
        fclose(Power.SerialPort);
        delete(Power.SerialPort);
        clear Power.SerialPort;
        
    end


end