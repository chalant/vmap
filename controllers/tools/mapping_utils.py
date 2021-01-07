class RectangleWrapper(object):
    def __init__(self, rectangle, rid, instance, container=None):
        self._components = []
        self._container = container
        self._rectangle = rectangle

        self._cursor = -1
        self._rid = rid
        self._top_left = instance.top_left
        self._instance = instance

    @property
    def rid(self):
        return self._rid

    @rid.setter
    def rid(self, value):
        self._rid = value

    @property
    def bbox(self):
        return self._instance.bbox

    @bbox.setter
    def bbox(self, value):
        self._instance.bbox = value

    @property
    def top_left(self):
        return self._top_left

    @top_left.setter
    def top_left(self, value):
        self._top_left = value

    @property
    def bottom_right(self):
        return self._rectangle.bottom_right

    @property
    def center(self):
        return self._rectangle.center

    @property
    def rectangle(self):
        return self._rectangle

    @property
    def height(self):
        return self._rectangle.height

    @property
    def width(self):
        return self._rectangle.width

    @property
    def container(self):
        return self._container

    @container.setter
    def container(self, value):
        self._container = value

    @property
    def components(self):
        return self._components

    def add_component(self, rid):
        self._components.append(rid)

    def submit(self, connection):
        self._instance.submit(connection)

    def delete(self, connection):
        self._instance.delete(connection)

    def __iter__(self):
        return self

    def __next__(self):
        self._cursor += 1
        c = self._cursor
        comps = self._components
        if c < len(comps):
            return comps[c]
        else:
            self._cursor = -1
            raise StopIteration

class TreeIterator(object):
    def __init__(self, mapper, start):
        '''

        Parameters
        ----------
        mapper: controllers.tools.mapping.MappingTool
        '''
        self._stack = [start]
        self._mapper = mapper

        self._ls = len(self._stack)

    def __iter__(self):
        return self

    def __next__(self):
        stack = self._stack

        if self._ls == 0:
            raise StopIteration
        else:
            rct = self._mapper.get_rectangle(stack[-1])
            try:
                stack.append(next(rct))
                self._ls += 1
            except StopIteration:
                stack.pop()
                self._ls -= 1
                return rct

def tree_iterator(mapper, start):
    '''

    Parameters
    ----------
    mapper: controllers.tools.mapping.MappingTool
    start: int

    Yields
    ------
    RectangleWrapper

    '''
    stack = [start]
    ls = len(stack)

    while ls != 0:
        rct = mapper.get_rectangle(stack[-1])
        try:
            stack.append(next(rct))
            ls += 1
        except StopIteration:
            stack.pop()
            ls -= 1
            yield rct

def copy(mapper, start, dx, dy):
    '''

    Parameters
    ----------
    mapper: controllers.tools.mapping.MappingTool
    start

    Yields
    ------
    RectangleWrapper
    '''

    stack = [start]

    ls = len(stack)

    instances = []

    while ls != 0:
        rct = mapper.get_rectangle(stack[-1])
        try:
            stack.append(next(rct))
            ls += 1
        except StopIteration:
            a, b = rct.top_left

            rid = mapper.add_instance(rct.rid, a + dx, b + dy)

            stack.pop()

            for _ in range(len(rct.components)):
                mapper.add_component(rid, instances.pop())

            instances.append(rid)
            ls -= 1

            yield rid
