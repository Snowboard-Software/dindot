"""Transform font anchors with an affine matrix or an optical point mapper."""

def move_anchor(anchor, matrix):
    if anchor is None:
        return
    if callable(matrix):
        anchor.XCoordinate, anchor.YCoordinate = map(round, matrix((anchor.XCoordinate, anchor.YCoordinate)))
        return
    sx, sy, dx, dy = matrix
    anchor.XCoordinate = round(anchor.XCoordinate * sx + dx)
    anchor.YCoordinate = round(anchor.YCoordinate * sy + dy)
