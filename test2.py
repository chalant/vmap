import Xlib
import Xlib.display
import select

def handle_event(event):
    print(event)

def main():
    display = Xlib.display.Display(':0')
    root = display.screen().root
    root.change_attributes(event_mask=
        Xlib.X.ButtonPressMask | Xlib.X.ButtonReleaseMask)

    while 1:
        # Wait for display to send something, or a timeout of one second
        readable, w, e = select.select([display], [], [], 1)

        # if no files are ready to be read, it's an timeout
        if not readable:
            print('Got no events')
            break

        # if display is readable, handle as many events as have been recieved
        elif display in readable:
            i = display.pending_events()
            while i > 0:
                event = display.next_event()
                handle_event(event)
                i = i - 1

if __name__ == "__main__":
    main()