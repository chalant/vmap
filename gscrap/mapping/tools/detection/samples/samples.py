class Sample(object):
    def __init__(self, rid, iid, cz, bbox, image_metadata, image, photo_image):
        """

        Parameters
        ----------
        rid: int
        iid: int
        cz: CaptureZone
        bbox: tuple
        image_metadata: models.images.ImageMetadata
        """

        self.rid = rid
        self._cz = cz
        self.bbox = bbox
        self.iid = iid
        self._meta = image_metadata
        self.image = image
        self.photo_image = photo_image

        self._changed = False

    @property
    def width(self):
        return self._meta.width

    @property
    def height(self):
        return self._meta.height

    @property
    def position(self):
        return self._meta.position

    @position.setter
    def position(self, value):
        meta = self._meta
        if meta.position != value:
            self._changed = True
            meta.position = value

    @property
    def top_left(self):
        bbox = self.bbox
        return bbox[0], bbox[1]

    @property
    def center(self):
        x0, y0, x1, y1 = self.bbox
        return (x0 + x1)/2, (y0 + y1)/2

    @property
    def label_type(self):
        return self._cz._label_type

    @property
    def label_name(self):
        return self._cz.label_name

    @property
    def label(self):
        return self._meta.label["instance_name"]

    def submit(self, connection):
        if self._changed:
            self._meta._submit(connection)

    def delete(self, connection):
        self._meta.delete_image(connection)

    def get_image(self):
        return self.image

class SamplesModel(object):
    def __init__(self):
        self._capture_zone = None
        self._sample_observers = []
        self._cz_obs = []

        self.position = 0

    def add_sample(self, image, label):
        cz = self._capture_zone

        position = self.position
        position += 1

        if cz:
            meta = cz.add_sample(image, label)
            for obs in self._sample_observers:
                obs.add_image(image, meta)

        self.position = position

    def get_samples(self, connection):
        position = 0

        for im in self._capture_zone.get_samples(connection):
            position += 1
            yield im

        self.position = position

    def add_sample_observer(self, observer):
        self._sample_observers.append(observer)

    def add_capture_zone_observer(self, observer):
        self._cz_obs.append(observer)


class SamplesController(object):
    def __init__(self, model):
        """

        Parameters
        ----------
        model: tools.detection.samples.SamplesModel
        """
        self._model = model

        self._view = SamplesView(self, model)

        self.samples = None

    def view(self):
        return self._view

    # def capture_zone_update(self, connection, capture_zone):
    #     view = self._view
    #     if not capture_zone.classifiable:
    #         view.deactivate() #deactive sampling
    #     else:
    #         view.activate()
    #         view.capture_zone_update(connection, capture_zone)

    def samples_update(self, samples):
        sp = self.samples

        if sp:
            sp.clear_image_observers()

        self.samples = samples

        view = self._view

        samples.add_image_observer(view)

        view.samples_update(samples)

    def set_capture_zone(self, capture_zone):
        pass

    def set_video_metadata(self, video_metadata):
        pass

    def filters_update(self, filters):
        """

        Parameters
        ----------
        filters: tools.detection.filtering.filtering.FilteringModel

        Returns
        -------

        """

        view = self._view

        if filters.filters_enabled:
            view.enable_filters(filters)
        else:
            view.disable_filters(filters)

    def add_images_observer(self, observer):
        self._view.add_image_observer(observer)