# Copyright 2024 The Rubic. All Rights Reserved.

"""Concrete implementation of the Rectangle model."""

from __future__ import annotations

from src.models.db import Rectangle, Vector2


class RectangleService:
    """Rectangle model."""

    @staticmethod
    def get_area(rectangle: Rectangle) -> float:
        """Returns the area of the rectangle."""
        return (rectangle.top_right.x - rectangle.bottom_left.x) * (
            rectangle.top_right.y - rectangle.bottom_left.y
        )

    @staticmethod
    def get_bottom_center_point(rectangle: Rectangle) -> Vector2:
        """Returns the bottom middle point of the rectangle."""
        x1, y1 = rectangle.bottom_left.x, rectangle.bottom_left.y
        x2, _ = rectangle.top_right.x, rectangle.top_right.y
        return Vector2(
            x=(x1 + x2) / 2,
            y=y1,
        )

    @staticmethod
    def get_center_point(rectangle: Rectangle) -> Vector2:
        """Returns the center point of the rectangle."""
        x1, y1 = rectangle.bottom_left.x, rectangle.bottom_left.y
        x2, y2 = rectangle.top_right.x, rectangle.top_right.y
        return Vector2(
            x=(x1 + x2) / 2,
            y=(y1 + y2) / 2,
        )

    @staticmethod
    def get_overlap_area(rectangle_1: Rectangle, rectangle_2: Rectangle) -> float:
        """Returns the area of overlap between two rectangles."""
        x_overlap = max(
            0,
            min(rectangle_1.top_right.x, rectangle_2.top_right.x)
            - max(rectangle_1.bottom_left.x, rectangle_2.bottom_left.x),
        )
        y_overlap = max(
            0,
            min(rectangle_1.top_right.y, rectangle_2.top_right.y)
            - max(rectangle_1.bottom_left.y, rectangle_2.bottom_left.y),
        )
        return x_overlap * y_overlap

    @staticmethod
    def contains_point(rectangle: Rectangle, x: float, y: float) -> bool:
        """Returns True if the point is inside the rectangle."""
        return (rectangle.bottom_left.x <= x <= rectangle.top_right.x) and (
            rectangle.bottom_left.y <= y <= rectangle.top_right.y
        )

    @staticmethod
    def is_stacked_on(
        top_rectangle: Rectangle,
        bottom_rectangle: Rectangle,
        vertical_margin: float = 0.055,
        horizontal_margin: float = 0.1,
    ) -> bool:
        """Returns True if the rectangle is stacked on top of the other rectangle."""
        is_horizontal_overlapping = (
            top_rectangle.top_right.x
            > bottom_rectangle.bottom_left.x + horizontal_margin
            and top_rectangle.bottom_left.x
            < bottom_rectangle.top_right.x - horizontal_margin
        )

        # vertically difference less than 1.5 centimeters
        is_vertical_near = (
            abs(top_rectangle.bottom_left.y - bottom_rectangle.top_right.y)
            < vertical_margin
        )

        return is_horizontal_overlapping and is_vertical_near

    @staticmethod
    def can_contain(rectangle_1: Rectangle, rectangle_2: Rectangle) -> bool:
        """Returns true of other_rect with threshold can fit in the self rectangle."""
        fits_width = rectangle_1.width > rectangle_2.width
        fits_height = rectangle_1.height > rectangle_2.height
        return fits_width and fits_height

    @classmethod
    def slice_rectangle(
        cls, rectangle_1: Rectangle, rectangle_2: Rectangle, min_dimension: float = 0.1
    ) -> list[Rectangle]:
        """Slice rectangle_1 with rectangle_2."""
        if cls.get_overlap_area(rectangle_1, rectangle_2) <= 0:
            raise ValueError("Rectangles do not overlap.")

        overlap_left = max(rectangle_1.bottom_left.x, rectangle_2.bottom_left.x)
        overlap_right = min(rectangle_1.top_right.x, rectangle_2.top_right.x)
        _overlap_bottom = max(rectangle_1.bottom_left.y, rectangle_2.bottom_left.y)
        overlap_top = min(rectangle_1.top_right.y, rectangle_2.top_right.y)

        rect_left = Rectangle(
            bottom_left=rectangle_1.bottom_left,
            top_right=Vector2(x=overlap_left, y=rectangle_1.top_right.y),
        )
        rect_middle = Rectangle(
            bottom_left=Vector2(x=overlap_left, y=overlap_top),
            top_right=Vector2(x=overlap_right, y=rectangle_1.top_right.y),
        )
        rect_right = Rectangle(
            bottom_left=Vector2(x=overlap_right, y=rectangle_1.bottom_left.y),
            top_right=rectangle_1.top_right,
        )

        return [
            rect
            for rect in (rect_left, rect_middle, rect_right)
            if rect.width > min_dimension and rect.height > min_dimension
        ]

    @classmethod
    def adjust_rectangle_contains_point(
        cls, rectangle: Rectangle, x: float, y: float
    ) -> Rectangle:
        """Adjusts the rectangle so that it does not contain the point."""
        if cls.contains_point(rectangle, x, y):
            # Find which side is closest to the point (left or right)
            left_distance = abs(rectangle.bottom_left.x - x)
            right_distance = abs(rectangle.top_right.x - x)
            if left_distance < right_distance:
                # Adjust the left side
                rectangle.bottom_left.x = x
            else:
                # Adjust the right side
                rectangle.top_right.x = x

            # Find which side is closest to the point (top or bottom)
            bottom_distance = abs(rectangle.bottom_left.y - y)
            top_distance = abs(rectangle.top_right.y - y)
            if bottom_distance < top_distance:
                # Adjust the bottom side
                rectangle.bottom_left.y = y
            else:
                # Adjust the top side
                rectangle.top_right.y = y
        return rectangle

    @classmethod
    def adjust_rectangle_vertical_split(
        cls, rect1: Rectangle, rect2: Rectangle, intersect_rect: Rectangle
    ) -> tuple[Rectangle, Rectangle]:
        """Adjusts the two rectangles so that they do not overlap vertically."""
        intersect_rect_center_y = cls.get_center_point(intersect_rect).y

        # Get the rectangle that is above the other
        if (
            rect1.top_right.y > rect2.top_right.y
            and rect1.bottom_left.y > rect2.bottom_left.y
        ):
            # rect 1 is top
            height_to_subtract = rect2.top_right.y - intersect_rect_center_y
            rect2.top_right.y -= height_to_subtract

            height_to_add = intersect_rect_center_y - rect1.bottom_left.y
            rect1.bottom_left.y += height_to_add

            return rect1, rect2

        # rect 2 is top
        height_to_subtract = rect1.top_right.y - intersect_rect_center_y
        rect1.top_right.y -= height_to_subtract

        height_to_add = intersect_rect_center_y - rect2.bottom_left.y
        rect2.bottom_left.y += height_to_add

        return rect1, rect2

    @classmethod
    def adjust_rectangle_horizontal_split(
        cls,
        rectangle_1: Rectangle,
        rectangle_2: Rectangle,
        intersect_rectangle: Rectangle,
    ) -> tuple[Rectangle, Rectangle]:
        """Adjusts the two rectangles so that they do not overlap horizontally."""
        intersect_rectangle_center_x = cls.get_center_point(intersect_rectangle).x

        # Get the rectangle that is to the right of the other
        if (
            rectangle_1.top_right.x > rectangle_2.top_right.x
            and rectangle_1.bottom_left.x > rectangle_2.bottom_left.x
        ):
            # rect 1 is to the right (move the right side more right)
            width_to_add = intersect_rectangle_center_x - rectangle_1.bottom_left.x
            rectangle_1.bottom_left.x += width_to_add

            # rect 2 is to the left (move the left side more left)
            width_to_subtract = rectangle_2.top_right.x - intersect_rectangle_center_x
            rectangle_2.top_right.x -= width_to_subtract

            return rectangle_1, rectangle_2

        # rect 1 is to the left (move the left side more left)
        width_to_subtract = rectangle_1.top_right.x - intersect_rectangle_center_x
        rectangle_1.top_right.x -= width_to_subtract

        # rect 2 is to the right (move the right side more right)
        width_to_add = intersect_rectangle_center_x - rectangle_2.bottom_left.x
        rectangle_2.bottom_left.x += width_to_add

        return rectangle_1, rectangle_2

    @staticmethod
    def get_intersecting_rect(
        rectangle_1: Rectangle, rectangle_2: Rectangle
    ) -> Rectangle:
        """Returns the intersecting rectangle between two rectangles."""
        x1 = max(rectangle_1.bottom_left.x, rectangle_2.bottom_left.x)
        y1 = max(rectangle_1.bottom_left.y, rectangle_2.bottom_left.y)
        x2 = min(rectangle_1.top_right.x, rectangle_2.top_right.x)
        y2 = min(rectangle_1.top_right.y, rectangle_2.top_right.y)

        # Check if there is a valid intersection (non-negative width and height)
        if x1 < x2 and y1 < y2:
            return Rectangle.model_validate(
                {"bottom_left": {"x": x1, "y": y1}, "top_right": {"x": x2, "y": y2}}
            )
        raise ValueError("Rectangles overlap is invalid")

    @classmethod
    def intersection_w_h_ratio(
        cls, rectangle_1: Rectangle, rectangle_2: Rectangle
    ) -> float:
        """Returns the ratio of width  height of the intersection of two rectangles."""
        intersect_rect = cls.get_intersecting_rect(rectangle_1, rectangle_2)
        width = intersect_rect.top_right.x - intersect_rect.bottom_left.x
        height = intersect_rect.top_right.y - intersect_rect.bottom_left.y
        return width / height

    @classmethod
    def merge(cls, rectangle_1: Rectangle, rectangle_2: Rectangle) -> Rectangle:
        """Returns the merged rectangle of two rectangles."""
        if cls.get_overlap_area(rectangle_1, rectangle_2) == 0:
            raise ValueError("Rectangles do not overlap")

        # find which rectangle has larger area
        max_top_right_x = max(rectangle_1.top_right.x, rectangle_2.top_right.x)
        max_top_right_y = max(rectangle_1.top_right.y, rectangle_2.top_right.y)

        min_bottom_left_x = min(rectangle_1.bottom_left.x, rectangle_2.bottom_left.x)
        min_bottom_left_y = min(rectangle_1.bottom_left.y, rectangle_2.bottom_left.y)

        return Rectangle.model_validate(
            {
                "bottom_left": {"x": min_bottom_left_x, "y": min_bottom_left_y},
                "top_right": {"x": max_top_right_x, "y": max_top_right_y},
            }
        )

    @classmethod
    def remove_overlap(
        cls, rectangle_1: Rectangle, rectangle_2: Rectangle
    ) -> tuple[Rectangle, Rectangle]:
        """Returns two rectangles that do not overlap."""
        overlap_area = cls.get_overlap_area(rectangle_1, rectangle_2)
        overlap_threshold = 0.95

        if cls.get_overlap_area(rectangle_1, rectangle_2) == 0:
            raise ValueError("Rectangles do not overlap")

        intersection_w_h_ratio = cls.intersection_w_h_ratio(rectangle_1, rectangle_2)
        intersect_rect = cls.get_intersecting_rect(rectangle_1, rectangle_2)

        w_h_ratio_threshold = 3

        if intersection_w_h_ratio >= w_h_ratio_threshold:
            # the intersect has a much higher width, we need to shift vertically
            rectangle_1, rectangle_2 = cls.adjust_rectangle_vertical_split(
                rectangle_1, rectangle_2, intersect_rect
            )

        elif intersection_w_h_ratio <= (1 / w_h_ratio_threshold):
            # the intersect has a muchhigher height, we need to shift horizontally
            rectangle_1, rectangle_2 = cls.adjust_rectangle_horizontal_split(
                rectangle_1, rectangle_2, intersect_rect
            )

        else:
            # check if overlap is greater than 95% of either rectangle
            # if True, then return both rectangles as is
            min_area = min(
                cls.get_overlap_area(rectangle_1, rectangle_1),
                cls.get_overlap_area(rectangle_2, rectangle_2),
            )
            percent_overlap = overlap_area / min_area
            if percent_overlap >= overlap_threshold:
                return rectangle_1, rectangle_2

            center_point = cls.get_center_point(intersect_rect)
            rectangle_1 = cls.adjust_rectangle_contains_point(
                rectangle_1, center_point.x, center_point.y
            )
            rectangle_2 = cls.adjust_rectangle_contains_point(
                rectangle_2, center_point.x, center_point.y
            )

        return rectangle_1, rectangle_2
