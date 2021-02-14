import math

import typing

from controllers.rectangles import utils

def tree_iterator(instances, start):
    '''

    Parameters
    ----------
    start: int

    Yields
    ------
    RectangleWrapper

    '''
    stack = [start]
    ls = len(stack)

    while ls != 0:
        rct = get_rectangle(instances, stack[-1])
        try:
            stack.append(next(rct))
            ls += 1
        except StopIteration:
            stack.pop()
            ls -= 1
            yield rct

def get_root_container(instances, rid):
    r = get_rectangle(instances, rid)
    if r:
        container = r.container

        while container is not None:
            r = get_rectangle(instances, container)
            container = r.container

        if r:
            return r.rid
        return
    return

def get_rectangles(instances, container=None):
    """

    Parameters
    ----------
    instances: typing.Dict[int, controllers.rectangles.utils.RectangleWrapper]
    container: controllers.rectangles.utils.RectangleWrapper

    Returns
    -------
    typing.Generator[int]

    """
    if container:
        for c in container.components:
            yield instances[c]
    else:
        for r in instances.values():
            if not r.container:
                yield r

def get_rectangle(instances, rid):
    """

    Parameters
    ----------
    instances: typing.Dict[int, controllers.rectangles.utils.RectangleWrapper]
    rid: int

    Returns
    -------
    controllers.rectangles.utils.RectangleWrapper
    """

    if rid in instances:
        return instances[rid]
    return

def add_component(instances, rid, comp_rid):
    """

    Parameters
    ----------
    instances: typing.Dict[int, controllers.rectangles.utils.RectangleWrapper]
    rid: int

    Returns
    -------
    None

    """
    comp = instances[comp_rid]
    comp.container = rid
    cont = instances[rid]
    cont.add_component(comp_rid)
    comp.instance.container_id = cont.instance.id

def copy(instances, rectangle, dx, dy, factory, container_id=None):
    '''

    Parameters
    ----------
    instances: typing.Dict[int, controllers.rectangles.utils.RectangleWrapper]
    rectangle: controllers.rectangles.utils.RectangleWrapper
    dx: float
    dy: float
    factory: controllers.rectangles.utils.RectangleFactory
    container_id: int

    Returns
    ------
    typing.Generator[controllers.rectangles.utils.RectangleWrapper]
    '''

    rct = rectangle

    stack = [rct.rid]

    ls = len(stack)

    copies = []
    last = None

    while ls != 0:
        rct = get_rectangle(instances, stack[-1])

        try:
            stack.append(next(rct))
            ls += 1
        except StopIteration:
            x0, y0, x1, y1 = rct.bbox

            x = x0 + dx
            y = y0 + dy

            # we create a new instance of the cz.
            rectangle = factory.create_rectangle(rct.instance.create_instance(x, y), x, y)
            nid = rectangle.rid

            instances[nid] = rectangle

            stack.pop()

            for _ in range(len(rct.components)):
                add_component(instances, nid, copies.pop())

            copies.append(nid)
            ls -= 1
            last = nid

            yield rectangle

    if container_id:
        add_component(instances, container_id, last)

def find_closest(instances, x, y):
    m_dist = None
    p = (x, y)

    results = []

    for r in instances.values():
        if m_dist is None:
            m_dist = min((math.dist(p, r.top_left), math.dist(p, r.bottom_right)))
            continue

        dst = min((math.dist(p, r.top_left), math.dist(p, r.bottom_right)))

        if dst < m_dist:
            m_dist = dst

    for rid, r in instances.items():
        if m_dist == min((math.dist(p, r.top_left), math.dist(p, r.bottom_right))):
            results.append(rid)

    return results

def get_components(instances, rct):
    if isinstance(rct, utils.RectangleWrapper):
        return rct.components
    return instances[rct].components

def load_rectangles(connection, project):
    for rct in project.get_rectangles(connection):
        yield rct

def load_rectangle_instances(connection, rectangles, factory):
    """

    Parameters
    ----------
    connection
    rectangles: typing.Iterable[models.rectangles.Rectangle]
    factory: controllers.rectangles.utils.RectangleFactory

    Returns
    -------
    typing.Generator[controllers.rectangles.utils.RectangleWrapper]
    """

    cmp_to_rid = {}
    instances = {}

    for rct in rectangles:
        for instance in rct.get_instances(connection):
            wrapper = factory.create_rectangle(instance, *instance.top_left)

            rid = wrapper.rid

            instances[rid] = wrapper
            cmp_to_rid[instance.id] = rid

    # build relations
    for k, w in instances.items():
        wrapper = instances[k]
        for cmp in wrapper.instance.get_components():
            rid = cmp_to_rid[cmp]
            component = instances[rid]
            component.container = k
            w.add_component(rid)
        yield w

def remove_rectangle(instances, rid):
    """

    Parameters
    ----------
    instances: Dict
    rid: Int

    Yields
    ------
    controllers.rectangles.utils.RectangleWrapper
    """
    container = get_rectangle(instances, rid).container

    if container:
        ct = get_rectangle(instances, container)
        ct.components.remove(rid)

    for rct in tree_iterator(instances, rid):
        yield rct

def _smallest(per, p):
    return per <= p

def _biggest(per, p):
    return per >= p


def find_closest_enclosing(instances, x, y):
    m_dist = None
    p = (x, y)

    results = []

    #find smallest distance

    for r in instances.values():
        x0, y0, x1, y1 = r.bbox

        if m_dist is None:
            if x0 < x and y0 < y and x1 > x and y1 > y:
                m_dist = math.dist(p, r.top_left)
            continue

        dst = math.dist(p, r.top_left)

        if dst < m_dist and x0 < x and y0 < y and x1 > x and y1 > y:
            m_dist = dst

    for rid, r in instances.items():
        if m_dist == math.dist(p, r.top_left):
            results.append(rid)

    return results