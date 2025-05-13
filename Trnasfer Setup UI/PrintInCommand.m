function  PrintInCommand(handles,str)
handles.Command_Window.String(end+1) = {str};
handles.Command_Window.Value = size(handles.Command_Window.String,1);
end

