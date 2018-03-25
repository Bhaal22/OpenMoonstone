from collections import UserList
from enum import Enum

from attr import attrs, attrib
import pygame

from input import InputSystem


x_distances = (
    (25, 3, 23, 4),
    (0, 0, 0, 0),
    (25, 3, 23, 4),
)
y_distances = (
    (2, 9, 2, 9),
    (0, 0, 0, 0),
    (8, 2, 9, 2),
)
BOUNDARY = pygame.Rect(10, 30, 320 - 10, 155 - 30)


class Direction(Enum):
    LEFT = -1
    RIGHT = 1


@attrs(slots=True)
class Movement:
    input = attrib(type=InputSystem)
    position = attrib(
        type=pygame.Rect,
        converter=lambda p: pygame.Rect(p[0], p[1], 0, 0),
    )
    frame_num = attrib(type=int, default=0)
    direction = attrib(type=Direction, default=Direction.RIGHT)

    next_position = attrib(
        type=pygame.Rect,
        default=lambda: pygame.Rect(0, 0, 0, 0),
    )
    next_frame = attrib(type=int, default=0)
    move_frame = attrib(type=int, default=0)

    attack_frame = attrib(type=int, default=None)
    attack_anim_length = attrib(type=int, default=None)


class MovementSystem(UserList):
    def update(self):
        for mover in self.data:
            if mover.attack_frame is not None:
                mover.attack_frame += 1
                if mover.attack_frame < mover.attack_anim_length:
                    continue
                else:
                    mover.attack_frame = None
                    mover.attack_anim_length = None

            if mover.input.fire:
                mover.attack_frame = 0
                continue

            new_position, frame = MovementSystem.next_position(mover)
            direction = mover.input.direction
            if direction.x:
                mover.direction = Direction(mover.input.direction.x)

            x, y, new_position = MovementSystem.clamp_to_boundary(
                mover.position, direction, new_position)
            direction.x = x
            direction.y = y

            frame = frame * ((direction.x | direction.y) & 1)
            mover.next_frame = frame
            mover.next_position = new_position

    @staticmethod
    def next_position(mover):
        new_position = pygame.Rect(mover.position)

        direction = mover.input.direction

        is_moving = (direction.x | direction.y) & 1
        move_frame = ((mover.frame_num + 1) % 4) * is_moving

        x_delta = x_distances[direction.x + 1][move_frame] * direction.x
        new_position.x = mover.position.x + x_delta

        y_delta = y_distances[direction.y + 1][move_frame] * direction.y
        new_position.y = mover.position.y + y_delta
        return new_position, move_frame

    @staticmethod
    def clamp_to_boundary(position, direction, new_position):
        x = direction.x
        y = direction.y

        clamped = new_position.clamp(BOUNDARY)
        if clamped.x != new_position.x:
            new_position.x = position.x
            x = 0
        if clamped.y != new_position.y:
            new_position.y = position.y
            y = 0
        return x, y, new_position


movement_system = MovementSystem()