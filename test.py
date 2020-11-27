import select

from Xlib.display import Display
from Xlib import X
from Xlib.ext.xtest import fake_input
from Xlib.ext import record
from Xlib.protocol import rq
from Xlib.display import request


display = Display(':0')
def handle_event(event):
    data = event.data
    while len(data):
        event, data = rq.EventField(None).parse_binary_value(data, display.display, None, None)
        if event.type == X.ButtonPress:
            print("Pressed!")
            raise KeyboardInterrupt

ctx = display.record_create_context(
            0,
            [record.AllClients],
            [{
                    'core_requests': (0, 0),
                    'core_replies': (0, 0),
                    'ext_requests': (0, 0, 0, 0),
                    'ext_replies': (0, 0, 0, 0),
                    'delivered_events': (0, 0),
                    'device_events': (X.ButtonPressMask, X.ButtonReleaseMask),
                    'errors': (0, 0),
                    'client_started': False,
                    'client_died': False,
            }]
 )

try:
    display.screen().root.grab_pointer(True, X.ButtonPressMask | X.ButtonReleaseMask , X.GrabModeAsync, X.GrabModeAsync, 0, 0, X.CurrentTime)
    display.record_enable_context(ctx, handle_event)
    display.record_free_context(ctx)
except KeyboardInterrupt:
    display.record_disable_context(ctx)
    display.ungrab_pointer(X.CurrentTime)
    # display.screen().root.ungrab_button(0, [0])
    display.flush()
    exit()

# try:
#     while 1:
#         # Wait for display to send something, or a timeout of one second
#         readable, w, e = select.select([display], [], [], 1)
#
#         # if no files are ready to be read, it's an timeout
#         if not readable:
#             print('Got no events')
#             break
#
#         # if display is readable, handle as many events as have been recieved
#         elif display in readable:
#             i = display.pending_events()
#             while i > 0:
#                 event = display.next_event()
#                 handle_event(event)
#                 i = i - 1
# except KeyboardInterrupt:
#     display.record_disable_context(ctx)
#     display.ungrab_pointer(X.CurrentTime)
#     display.flush()