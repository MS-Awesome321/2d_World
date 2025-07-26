from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from livesegment import LiveSegment
import time
import os

class NewFileHandler(FileSystemEventHandler):
    def _placeholder(fname):
        print(f"New file detected: {fname}")

    def set_run_method(self, method=_placeholder):
        self.method = method

    def on_created(self, event):
        if event.is_directory:
            return
        filename = os.path.basename(event.src_path)
        time.sleep(0.1)
        self.method(filename)

if __name__ == "__main__":
    import sys 

    mag = int(sys.argv[1])
    if mag == 10:
        photo_dir = 'C:/Users/admin/Desktop/2d_World/hardware/photo_dir'
        result_dir = 'C:/Users/admin/Desktop/2d_World/hardware/results'
        event_handler = NewFileHandler()
        event_handler.set_run_method(LiveSegment(photo_dir, result_dir, 10))
    elif mag == 100:
        photo_dir = 'C:/Users/admin/Desktop/2d_World/hardware/photo_dir/m_100'
        result_dir = 'C:/Users/admin/Desktop/2d_World/hardware/results/m_100'
        event_handler = NewFileHandler()
        event_handler.set_run_method(LiveSegment(photo_dir, result_dir, 100))
    else:
        raise ValueError('Invalid Magnification Given.')


    observer = Observer()
    observer.schedule(event_handler, path=photo_dir, recursive=False)
    observer.start()
    print(f"Watching {photo_dir} for new files...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()