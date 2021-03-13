from xdo import Xdo, XdoException

xdo = Xdo()
try:
    win_id = xdo.select_window_with_click()
except XdoException:
    print("Aborted!")
    raise
# print(xdo.get_window_location(win_id), xdo.get_window_size(win_id))
xdo.enable_feature()

