function Turret = TurretControl()

baudate = 9600;
Comport = 'COM7';
Timeout = 3;
Terminator = 'CR';
Position = 1;

%initialize the serial port
Turret.SerialPort = serial(Comport,'BaudRate',baudate,'Terminator',Terminator,'Timeout',Timeout);
fopen(Turret.SerialPort);

Turret.RotateToPosition = @RotateToPosition;
Turret.Response = @Response;
Turret.getPos = @getPos;
Turret.Kill = @Kill;

    function Msg = RotateToPosition(Pos)
        
        Cmd = ['cRDC',num2str(Pos)];
        fprintf(Turret.SerialPort,Cmd);
        Msg = Turret.Response();
        pause(0.1);
        
    end


  function  Pos = getPos()
    
       fprintf(Turret.SerialPort,'rRAR');
       response = fscanf(Turret.SerialPort);
       Pos = str2double(response(end-1));

  end


    function Msg = Response()
        
        response = fscanf(Turret.SerialPort);
        if response(1) == 'o'
            Position = getPos();
            switch Position
                case 1
                     Msg = ['Objective is set to 5 Mag'];
                case 2
                     Msg = ['Objective is set to 20 Mag'];
                case 3
                    Msg = ['Objective is set to 50 Mag'];
                case 4
                    Msg = ['Objective is set to 100 Mag'];
            end
        else
            switch response(5)
                case 'a'
                    Msg = 'An unregistered command was received';
                case 'b'
                    Msg = 'Data was invalid';
                case 'd'
                    Msg = 'Timeout error occurred during control';
                case 'f'
                    Msg = 'Control Command is received whole control is forbidden ';
                case '4'
                    Msg = 'The received data exceeded the limit';
                case '5'
                    Msg = 'Hardware breakdown';
            end
            
        end
        
    end


    function Kill()
 
        fclose(Turret.SerialPort);
        delete(Turret.SerialPort);
        clear Turret.SerialPort;
    
    end
  

end