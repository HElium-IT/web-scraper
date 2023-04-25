import logging

ObjectInfoLogger = logging.getLogger("ObjectInfoLogger")
ObjectInfoLogger.setLevel(logging.INFO)


def print_object_infos(object):
    ObjectInfoLogger.info(f"Object type: {type(object)}")
    ObjectInfoLogger.info(f"Object dir: {dir(object)}")
    ObjectInfoLogger.info(f"Object dict: {object.__dict__}")
    ObjectInfoLogger.info(f"Object repr: {repr(object)}")
    ObjectInfoLogger.info(f"Object str: {str(object)}")
