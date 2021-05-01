#a logger has an image capture loop and writes a list of detected events into a file

class Logger(object):
    def __init__(self):
        self._capture_zones = []

    def start(self):
        #todo: capture zones must be sorted by "position" (increasing)
        #todo: each captured event should be appended to a queue.
        #todo: each time we call capture/detect, each capture zone detects the
        # captured element and appends it to a queue.
        #todo: we must sort capture zones by increasing "position".

        #we have an infinit loop that runs by frame rate and captures images
        #we call "capture" on each capture zone,
        #we push the detected event (which is an event) to a list (queue)

        # 1) capture images (by iterating through capture zones)
        # 2) for each entity call "log" which should return a "flatened" message
        #    ex: {
        #           entity: opponent,
        #           index: 0
        #           event: {
        #               id: player_id
        #               action: bet,
        #               dealer: 0,
        #               amount: 10,
        #               cards: [Null, Null]
        #             }
        #       }
        pass