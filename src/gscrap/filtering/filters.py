from gscrap.data.filters import filters

def apply_filters(pipeline, image):
    im = image
    for filter_ in pipeline:
        im = filter_.apply(im)

    return im


def load_filters(connection, group_id, parameter_id):
    for res in filters.load_filters(connection, group_id, parameter_id):
        type_ = res["type"]
        name = res["name"]
        position = res["position"]

        filter_ = filters.create_filter(type_, name, position)
        filter_.load_parameters(connection, group_id, parameter_id)

        yield filter_