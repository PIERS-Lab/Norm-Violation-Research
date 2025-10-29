import anki_vector
import anki_vector.events
# This class allows an easy way to extract pose data of objects that Vector has observed
class vectorObjectWatcher:
    def __init__ (self, robot, event):
        self.obj = None
        robot.events.subscribe(self.handle_event, anki_vector.events.Events.object_appeared)
    
    def handle_event(self, robot, even_type, event):
        self.obj = event.obj
        