from gscrap.data.filters import filters

class FilterPipelines(object):
    def __init__(self):
        self._filter_pipelines = {}

    def get_filter_pipeline(self, connection, label, scene):
        filter_pipelines = self._filter_pipelines

        filter_group = filters.get_filter_group(
            connection,
            label.label_name,
            label.label_type,
            scene.name)

        group_id = filter_group['group_id'] + filter_group['parameter_id']

        if group_id not in filter_pipelines:
            # this will be displayed on the filters canvas.
            filter_pipeline = list(self._load_filters(
                connection,
                filter_group['group_id'],
                filter_group['parameter_id']
            ))
        else:
            filter_pipeline = filter_pipelines[group_id]

        return filter_pipeline

    def _load_filters(self, connection, group_id, parameter_id):
        for res in filters.load_filters(connection, group_id, parameter_id):
            type_ = res["type"]
            name = res["name"]
            position = res["position"]

            filter_ = filters.create_filter(type_, name, position)
            filter_.load_parameters(connection, group_id, parameter_id)

            yield filter_