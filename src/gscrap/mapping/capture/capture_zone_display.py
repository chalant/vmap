from collections import defaultdict

from gscrap.data.rectangles import rectangle_labels as rl

from gscrap.mapping.tools import display

from gscrap.mapping.sampling import capture

class CaptureZoneDisplay(object):
    def __init__(self, canvas):
        self._capture_zones = {}

        self._display = display.RectangleDisplay(canvas)

        self._instances_by_rectangle_id = defaultdict(list)

    def draw(self, scene):
        capture_zones = self._capture_zones
        ins_by_rid = self._instances_by_rectangle_id
        dsp = self._display

        factory = capture.CaptureZoneFactory(scene, ins_by_rid)

        # load capture zones...
        with scene.connect() as connection:
            for rct in scene.get_rectangles(connection):
                cap_labels = [label for label in rl.get_rectangle_labels(connection, rct) if label.capture]

                # create capturable rectangles
                if cap_labels:
                    for instance in rct.get_instances(connection):
                        zone = dsp.draw(instance, factory)

                        capture_zones[zone.id] = zone

                        ins_by_rid[rct.id].append(zone)

        return capture_zones

    def clear(self):
        dsp = self._display

        self._instances_by_rectangle_id.clear()

        for cz in self._capture_zones.values():
            dsp.delete(cz)