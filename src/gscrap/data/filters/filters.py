import abc

import tkinter as tk

from sqlalchemy import text
import cv2
from PIL import Image

_GET_FILTER_GROUP = text(
    '''
    SELECT * 
    FROM filter_groups
    INNER JOIN labels_filters 
        ON labels_filters.filter_group = filter_groups.group_id
    WHERE labels_filters.label_type =:label_type 
        AND labels_filters.label_name =:label_name
        AND labels_filters.scene_name =:scene_name
    ''')

_REMOVE_LABEL_FROM_GROUP = text(
    '''
    DELETE FROM labels_filters
    WHERE labels_filters.label_type =:label_type 
        AND labels_filters.label_name =:label_name 
        AND labels_filters.scene_name =:scene_name
    ''')

_STORE_FILTER_GROUP = text(
    '''
    INSERT OR IGNORE 
    INTO filter_groups(group_id)
    VALUES (:group_id)
    ''')

# _ADD_FILTER_GROUP = text(
#     '''
#     INSERT OR IGNORE
#     INTO filter_groups(group_id)
#     VALUES (:group_id)
#     '''
# )

_GET_GROUP_ID = text(
    '''
    SELECT * FROM filter_groups
    WHERE group_id=:group_id
    '''
)

_UPDATE_LABEL_FILTERS_GROUP = text(
    '''
    UPDATE labels_filters
    SET filter_group=:group_id
    WHERE labels_filters.label_name=:label_name
        AND labels_filters.label_type=:label_type
        AND labels_filters.scene_name=:scene_name
    ''')

_GET_GROUPS = text(
    """
    SELECT * FROM filter_groups
    """)

_GET_FILTERS = text(
    """
    SELECT * FROM filters
    WHERE group_name=:group_id AND parameter_id=:parameter_id
    ORDER BY position ASC
    """)

_STORE_FILTER = text(
    '''
    INSERT OR REPLACE INTO filters(group_name, type, name, position, parameter_id)
    VALUES (:group_name, :type, :name, :position, :parameter_id)
    '''
)

_DELETE_FILTER = text(
    '''
    DELETE FROM filters
    WHERE group_name=:group_name 
        AND type=:type 
        AND name=:name 
        AND position=:position
        AND parameter_id=:parameter_id
    ''')

_STORE_FILTER_LABEL = text(
    '''
    INSERT OR IGNORE
    INTO labels_filters(filter_group, label_type, label_name, parameter_id, scene_name)
    VALUES (:filter_group, :label_type, :label_name, :parameter_id, :scene_name)
    ''')

_ADD_PARAMETER_ID = text(
    '''
    INSERT OR IGNORE INTO parameters(parameter_id)
    VALUES (:parameter_id)
    ''')

_GET_PARAMETER_ID = text(
    '''
    SELECT * FROM parameters
    WHERE parameter_id=:parameter_id
    ''')

_UPDATE_LABEL_FILTERS_PARAM_ID = text(
    '''
    UPDATE labels_filters
    SET parameter_id=:parameter_id
    WHERE labels_filters.label_name=:label_name
        AND labels_filters.label_type=:label_type
        AND labels_filters.scene_name=:scene_name
    ''')

_PARAMETER_QUERY = """
    SELECT * 
    FROM {} 
    WHERE group_name=:group_name 
        AND position=:position
        AND parameter_id=:parameter_id
    """

_DELETE_STRING = """
    DELETE 
    FROM {} 
    WHERE group_name=:group_name 
        AND position=:position"""

FILTER_TYPES = ("Color", "Resize", "Threshold", "Blur")

_THRESHOLD_TYPES = {
    "Binary":cv2.THRESH_BINARY,
    "Inverse Binary":cv2.THRESH_BINARY_INV,
    "Trunc":cv2.THRESH_TRUNC,
    "To Zero":cv2.THRESH_TOZERO,
    "To Zero Inverse":cv2.THRESH_TOZERO_INV
}

FILTERS_BY_TYPE = {
    "Color":("Grey",),
    "Blur": ("Gaussian" ,"Average", "Median"),
    "Threshold":tuple(_THRESHOLD_TYPES.keys()),
    "Resize":("Trim",)
}

_FILTERS_IDS = {
    "Binary": 10,
    "Inverse Binary": 11,
    "Trunc": 12,
    "To Zero": 13,
    "To Zero Inverse": 14,
    "Gaussian": 20,
    "Average": 21,
    "Median": 22,
    "Grey":30,
    "Trim":40
}

def add_parameter_id(connection, parameter_id):
    connection.execute(
        _ADD_PARAMETER_ID,
        parameter_id=parameter_id
    )

def parameters_exists(connection, parameter_id):
    if connection.execute(
        _GET_PARAMETER_ID,
        parameter_id=parameter_id).first():
        return True
    return False

def filter_group_exists(connection, group_id):
    if connection.execute(
        _GET_GROUP_ID,
        group_id=group_id
    ).first():
        return True
    return False

def update_filter_labels_parameter_id(
        connection,
        label_name,
        label_type,
        scene_name,
        parameter_id):

    connection.execute(
        _UPDATE_LABEL_FILTERS_PARAM_ID,
        label_name=label_name,
        label_type=label_type,
        scene_name=scene_name,
        parameter_id=parameter_id
    )

def update_filter_labels_group(
        connection,
        label_name,
        label_type,
        scene_name,
        group_id):

    connection.execute(
        _UPDATE_LABEL_FILTERS_GROUP,
        label_name=label_name,
        label_type=label_type,
        scene_name=scene_name,
        group_id=group_id)

def remove_label_from_group(connection, label_name, label_type, scene_name):
    return connection.execute(
        _REMOVE_LABEL_FROM_GROUP,
        label_type=label_type,
        label_name=label_name,
        scene_name=scene_name
    )

def get_filter_group(connection, label_name, label_type, scene_name):
    return connection.execute(
        _GET_FILTER_GROUP,
        label_type=label_type,
        label_name=label_name,
        scene_name=scene_name
    ).first()

def store_filter_group(connection, group_id):
    connection.execute(
        _STORE_FILTER_GROUP,
        group_id=group_id)

def store_filter_labels(
        connection,
        filter_group,
        label_type,
        label_name,
        parameter_id,
        scene_name):

    connection.execute(
        _STORE_FILTER_LABEL,
        filter_group=filter_group,
        label_type=label_type,
        label_name=label_name,
        parameter_id=parameter_id,
        scene_name=scene_name
    )

def get_filter_parameters(connection, filter_, group, parameter_id):
    if filter_.type == "Blur":
        if filter_.name == "Gaussian":
            query = text(_PARAMETER_QUERY.format("gaussian_blur"))
        elif filter_.name == "Average":
            query = text(_PARAMETER_QUERY.format("average_blur"))
        elif filter_.name == "Median":
            query = text(_PARAMETER_QUERY.format("median_blur"))
        else:
            raise ValueError("No filter of class {}".format(filter_.name))

    elif filter_.type == "Threshold":
        query = text(_PARAMETER_QUERY.format("threshold"))
    else:
        raise ValueError("No filter of type {}".format(filter_.type))

    return connection.execute(
        query,
        group_name=group,
        position=filter_.position,
        parameter_id=parameter_id
    ).fetchone()

def load_filters(connection, group_id, parameter_id):
    return connection.execute(
        _GET_FILTERS,
        group_id=group_id,
        parameter_id=parameter_id)

def get_filter_groups(connection):
    return connection.execute(_GET_GROUPS)

def get_filter_types():
    return FILTER_TYPES

def get_filter_classes(filter_type):
    return FILTERS_BY_TYPE[filter_type]

def create_parameter_id(filter_pipeline):
    sequence = ''

    for filter_ in filter_pipeline:
        sequence += filter_.get_parameters_sequence()

    if not sequence and len(filter_pipeline) > 0:
        return '-1'
    return sequence

def create_group_id(filter_pipeline):
    sequence = ''

    for filter_ in filter_pipeline:
        sequence += str(filter_.filter_id)

    return sequence

def create_filter(filter_type, filter_name, position):
    """

    Parameters
    ----------
    filter_type
    filter_name
    position

    Returns
    -------
    Filter
    """

    if filter_type == "Blur":
        if filter_name == "Gaussian":
            return GaussianBlur(position)
        elif filter_name == "Average":
            return AverageBlur(position)
        elif filter_name == "Median":
            return MedianBlur(position)
        else:
            raise ValueError("Unknown filter: {} {}".format(filter_name, filter_type))

    elif filter_type == "Threshold":
        if filter_name not in _THRESHOLD_TYPES:
            raise ValueError("Unknown filter: {} {}".format(filter_name, filter_type))
        return Threshold(position, filter_name)

    elif filter_type == "Color":
        if filter_name == "Grey":
            return Grey(position)
        else:
            raise ValueError("Unknown filter: {} {}".format(filter_name, filter_type))

    elif filter_type == "Resize":
        if filter_name == "Trim":
            return Trim(position)
    else:
        raise  ValueError("Unknown filter type: {}")

class Filter(abc.ABC):
    def __init__(self, position):
        self.position = position
        self._changed = False

        self._callbacks = []

    def on_data_update(self, callback):
        self._callbacks.append(callback)

    def clear_callbacks(self):
        self._callbacks.clear()

    @property
    def filter_id(self):
        return _FILTERS_IDS[self.name]

    @property
    @abc.abstractmethod
    def type(self):
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def name(self):
        raise NotImplementedError

    def apply(self, img):
        return self._apply(img)

    @abc.abstractmethod
    def _apply(self, img):
        raise NotImplementedError

    def render(self, container):
        self._flag = False
        frame = self._render(container)
        self._flag = True
        return frame

    @abc.abstractmethod
    def _render(self, container):
        raise NotImplementedError

    def load_parameters(self, connection, group, parameter_id):
        self._load_parameters(connection, group, parameter_id)

    @abc.abstractmethod
    def _load_parameters(self, connection, group, parameter_id):
        raise NotImplementedError

    def store(self, connection, group, parameter_id):
        connection.execute(
            _STORE_FILTER,
            group_name=group,
            parameter_id=parameter_id,
            type=self.type,
            name=self.name,
            position=self.position)

        self._store_parameters(connection, group, parameter_id)

    def delete(self, connection, group, parameter_id):
        pos = self.position

        connection.execute(
            _DELETE_FILTER,
            group_name=group,
            parameter_id=parameter_id,
            type=self.type,
            name=self.name,
            position=pos
        )

        self._delete_parameters(connection, group, pos, parameter_id)

    @abc.abstractmethod
    def _store_parameters(self, connection, group, parameter_id):
        raise NotImplementedError

    @abc.abstractmethod
    def _delete_parameters(self, connection, group, position, parameter_id):
        raise NotImplementedError

    def __lt__(self, other):
        return other.position < self.position

    def __le__(self, other):
        return other.position <= self.position

    def __eq__(self, other):
        return other.position == self.position

    def __setattr__(self, key, value):
        d = self.__dict__
        if key not in d:
            self.__dict__[key] = value

            # if '_callbacks' in d:
            #     for fn in self._callbacks:
            #         fn(self)
        else:
            pv = d[key]
            if pv != value:
                d[key] = value
                # if '_callbacks' in key:
                #     for fn in self._callbacks:
                #         fn(self)

    def __str__(self):
        return "Filter<{} {}>".format(self.type, self.name)

    def get_parameters_sequence(self):
        return ''

class Trim(Filter):
    #removes any "non interesting" information
    def __init__(self, position):
        super(Trim, self).__init__(position)

    @property
    def name(self):
        return "Trim"

    @property
    def type(self):
        return "Resize"

    def _apply(self, img):
        pil = Image.fromarray(img)
        wd, ht = pil.width, pil.height

        cnts, hier = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        cnts = sorted(cnts, key=cv2.contourArea, reverse=True)

        if len(cnts) != 0:
            x, y, w, h = cv2.boundingRect(cnts[0])
            roi = img[y:y+h, x:x+w]
            return cv2.resize(roi, (wd, ht), 0, 0)

        return img

    def _render(self, container):
        pass

    def _delete_parameters(self, connection, group, position, parameter_id):
        pass

    def _load_parameters(self, connection, group, parameter_id):
        pass

    def _store_parameters(self, connection, group, parameter_id):
        pass


class Threshold(Filter):
    def __init__(self, position, thresh_type, thresh_value=127, max_value=255):
        super(Threshold, self).__init__(position)

        self.thresh_type = thresh_type
        self.thresh_value = thresh_value
        self.max_value = max_value

    @property
    def type(self):
        return "Threshold"

    @property
    def name(self):
        return self.thresh_type

    def _apply(self, img):
        return cv2.threshold(
            img,
            self.thresh_value,
            self.max_value,
            _THRESHOLD_TYPES[self.thresh_type])[1]

    def _render(self, container):
        self._frame = frame = tk.Frame(container)
        thresh_label = tk.Label(frame, text="Value")

        self._thresh = thresh = tk.IntVar(frame, self.thresh_value)

        # notify
        def update(a, b, c):
            self.thresh_value = int(thresh.get())

            if self._flag:
                for fn in self._callbacks:
                    fn(self)

        thresh.trace_add("write", update)

        thresh = tk.Spinbox(frame, from_=0, to=255, width=5, textvariable=thresh, state='readonly')

        thresh_label.grid(column=0, row=0)
        thresh.grid(column=1, row=0)

        return frame

    def get_parameters_sequence(self):
        return '{}'.format(self.thresh_value)

    def _load_parameters(self, connection, group, parameter_id):
        data = get_filter_parameters(connection, self, group, parameter_id)

        self.thresh_type = data["type"]
        self.max_value = data["max_value"]
        self.thresh_value  = data["thresh_value"]

    def _store_parameters(self, connection, group, parameter_id):
        connection.execute(
            text(
                """
                INSERT OR REPLACE INTO threshold (group_name, parameter_id, position, thresh_value, max_value, type)
                VALUES (:group_name, :parameter_id, :position, :thresh_value, :max_value, :type)
                """),

            group_name=group,
            parameter_id=parameter_id,
            position=self.position,
            thresh_value=self.thresh_value,
            max_value=self.max_value,
            type=self.thresh_type
        )

    def _delete_parameters(self, connection, group, position, parameter_id):
        connection.execute(
            text(_DELETE_STRING.format('threshold')),
            group_name=group,
            position=position
        )

class GaussianBlur(Filter):
    def __init__(self, position, ksizeX=5, ksizeY=5, sigmaX=0, sigmaY=0):
        super(GaussianBlur, self).__init__(position)

        self.ksizeX = ksizeX
        self.ksizeY = ksizeY
        self.sigmaX = sigmaX
        self.sigmaY = sigmaY

    @property
    def type(self):
        return "Blur"

    @property
    def name(self):
        return "Gaussian"

    def _apply(self, img):
        try:
            return cv2.GaussianBlur(
                img,
                (self.ksizeX, self.ksizeY),
                self.sigmaX,
                sigmaY=self.sigmaY)

        except Exception:
            return img

    def get_parameters_sequence(self):
        return '{}{}{}{}'.format(self.ksizeX, self.ksizeY, self.sigmaX, self.sigmaY)

    def _render(self, container):
        self._frame = frame = tk.Frame(container)
        ksize_label = tk.Label(frame, text="ksize")

        self._ksizeX = kx = tk.IntVar(frame, self.ksizeX)
        self._ksizeY = ky = tk.IntVar(frame, self.ksizeY)

        self._sigmaX = sx = tk.IntVar(frame, self.sigmaX)
        self._sigmaY = sy = tk.IntVar(frame, self.sigmaY)

        #notify
        def update(a, b, c):
            self.ksizeX = int(kx.get())
            self.ksizeY = int(ky.get())

            self.sigmaX = int(sx.get())
            self.sigmaY = int(sy.get())

            if self._flag:
                for fn in self._callbacks:
                    fn(self)

        kx.trace_add("write", update)
        ky.trace_add("write", update)

        sx.trace_add("write", update)
        sy.trace_add("write", update)

        ksizex = tk.Spinbox(frame, from_=0, to=10, width=5, textvariable=kx, state='readonly')
        ksizey = tk.Spinbox(frame, from_=0, to=10, width=5, textvariable=ky, state='readonly')

        sigma_label = tk.Label(frame, text="sigma")

        sigmaX = tk.Spinbox(frame, from_=0, to=10, width=5, textvariable=sx, state='readonly')
        sigmaY = tk.Spinbox(frame, from_=0, to=10, width=5, textvariable=sy, state='readonly')

        ksize_label.grid(column=0, row=0)
        ksizex.grid(column=1, row=0)
        ksizey.grid(column=2, row=0)

        sigma_label.grid(column=0, row=1)
        sigmaX.grid(column=1, row=1)
        sigmaY.grid(column=2, row=1)

        #avoid calling updating on render

        return frame

    def close(self):
        #update values
        if self._frame:
            self.ksizeX = self._ksizeX.get()
            self.ksizeY = self._ksizeY.get()

            self.sigmaX = self._sigmaX.get()
            self.sigmaY = self._sigmaY.get()


            self._frame.destroy()

    def _load_parameters(self, connection, group, parameter_id):
        data = get_filter_parameters(connection, self, group, parameter_id)

        self.ksizeX = data["ksizeX"]
        self.ksizeY = data["ksizeY"]
        self.sigmaX = data["sigmaX"]
        self.sigmaY = data["sigmaY"]

    def _store_parameters(self, connection, group, parameter_id):
        connection.execute(
            text(
                """
                INSERT OR REPLACE INTO gaussian_blur (group_name, parameter_id, position, ksizeX, ksizeY, sigmaX, sigmaY) 
                VALUES (:group_name, :position, :ksizeX, :ksizeY, :sigmaX, :sigmaY, :parameter_id) 
                """),
            group_name=group,
            parameter_id=parameter_id,
            position=self.position,
            ksizeX=self.ksizeX,
            ksizeY=self.ksizeY,
            sigmaX=self.sigmaX,
            sigmaY=self.sigmaY
        )

    def _delete_parameters(self, connection, group, position, parameter_id):
        connection.execute(
            text(_DELETE_STRING.format('gaussian_blur')),
            group_name=group,
            position=position
        )

class AverageBlur(Filter):
    def __init__(self, position, ksizeX=5, ksizeY=5):
        super(AverageBlur, self).__init__(position)
        self.ksizeX = ksizeX
        self.ksizeY = ksizeY

    @property
    def type(self):
        return "Blur"

    @property
    def name(self):
        return "Average"

    def _apply(self, img):
        return cv2.blur(img, (self.ksizeX, self.ksizeY))

    def render(self, container):
        pass

    def get_parameters_sequence(self):
        return '{}{}'.format(self.ksizeX, self.ksizeY)

class MedianBlur(Filter):
    def __init__(self, position, ksize=5):
        super(MedianBlur, self).__init__(position)
        self.ksize = ksize

    @property
    def type(self):
        return "Blur"

    @property
    def name(self):
        return "Gaussian"

    @property
    def ksize(self):
        return self._kx

    @ksize.setter
    def ksize(self, value):
        self._kx = value

    def _apply(self, img):
        return cv2.medianBlur(img, self.ksize)

    def render(self, container):
        pass

    def get_parameters_sequence(self):
        return '{}'.format(self.ksize)

class Grey(Filter):
    def __init__(self, position):
        super(Grey, self).__init__(position)

    @property
    def type(self):
        return "Color"

    @property
    def name(self):
        return "Grey"

    def _apply(self, img):
        return cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    def _render(self, container):
        pass

    def _load_parameters(self, connection, group, parameter_id):
        pass

    def _store_parameters(self, connection, group, parameter_id):
        pass

    def _delete_parameters(self, connection, group, position, parameter_id):
        pass