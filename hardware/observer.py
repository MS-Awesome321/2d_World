from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from livesegment import LiveSegment
import time
import os
from utils import focus_disk
import numpy as np

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
    grow = 2
    rad = int(430*grow)
    f1 = focus_disk(np.zeros((755 * grow, 1350 * grow)), rad, invert=True)
    f2 = focus_disk(np.zeros((755 * grow, 1350 * grow)), rad - 10, invert=True)
    if mag == 10:
        photo_dir = 'C:/Users/admin/Desktop/2d_World/hardware/photo_dir'
        result_dir = 'C:/Users/admin/Desktop/2d_World/hardware/results'
        event_handler = NewFileHandler()
        event_handler.set_run_method(LiveSegment(photo_dir, result_dir, 10, focus_disks=[(f1, rad), (f2, rad-10)], grow=grow))
    elif mag == 100:
        photo_dir = 'C:/Users/admin/Desktop/2d_World/hardware/photo_dir/m_100'
        result_dir = 'C:/Users/admin/Desktop/2d_World/hardware/results/m_100'
        event_handler = NewFileHandler()
        event_handler.set_run_method(LiveSegment(photo_dir, result_dir, 100, focus_disks=[(f1, rad), (f2, rad-10)], grow=grow))
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