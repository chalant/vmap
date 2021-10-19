from sqlalchemy import text

_DELETE_RECTANGLE_IMAGES = text(
    '''
    DELETE 
    FROM images
    WHERE rectangle_id=:rectangle_id
    '''
)

def delete_rectangle_images(connection, rectangle):
    connection.execute(
        _DELETE_RECTANGLE_IMAGES,
        rectangle_id=rectangle.id)