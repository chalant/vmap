def apply_filters(pipeline, image):
    im = image
    for filter_ in pipeline:
        im = filter_.apply(im)

    return im