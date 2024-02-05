from game.UPDATED_GEOMETRY import Point, Line, Circle, StraightAngle, Rectangle


def test_one_two():
    # Point ============================================================================================================
    p1 = Point(0, 0)
    p2 = Point(3, 4)

    assert p1 != p2
    assert p1.distance(p2) == 5

    p2 = Point(0, 0)

    assert p1 == p2
    # ==================================================================================================================

    # Line =============================================================================================================
    l1 = Line(Point(-10, 0), Point(10, 0))
    l2 = Line(Point(0, 5), Point(10, 5))

    assert l1.distance(l2) == 5
    assert l1.distance(p1) == 0
    assert l1.parallel(l2)

    l3 = Line(Point(-10, -10), Point(10, 10))
    assert l1.intersection(l3) == Point(0, 0)
    # ==================================================================================================================

    # Circle ===========================================================================================================
    c1 = Circle(Point(0, 0), 2)
    c2 = Circle(Point(10, 10), 1)
    c3 = Circle(Point(3, 0), 2)

    assert not c1.intersection(c2)
    assert c1.intersection(c3)
    assert Point(0, 0) in c1
    assert Point(9, 3) not in c1
    assert c1.intersection(l1)
    assert not c1.intersection(l2)
    # ==================================================================================================================

    # Angle ============================================================================================================

    # ==================================================================================================================

    # Rectangle ========================================================================================================
    r1 = Rectangle([
        Point(0, 0),
        Point(5, 0),
        Point(5, 10),
        Point(0, 10)
    ])

    r2 = Rectangle([
        Point(3, 3),
        Point(7, 3),
        Point(7, 15),
        Point(3, 15)
    ])

    assert r1.intersection(c1)
    assert r1.intersection(l3)
    assert r1.intersection(r2)
    assert Point(2, 2) in r1
    assert Point(100, 100) not in r1
    assert Point(-100, 100) not in r1
    assert Point(-100, -100) not in r1
    assert Point(100, -100) not in r1
    # ==================================================================================================================
