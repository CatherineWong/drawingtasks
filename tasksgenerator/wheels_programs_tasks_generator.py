"""
wheels_programs_tasks_generator.py | Author: Catherine Wong.
Defines TasksGenerators that produce gadget tasks with wheels on them.
Threads program string generating logic through the generation.
"""

import math, random, itertools, copy
from sqlite3 import connect
from primitives.gadgets_primitives import *
from dreamcoder.grammar import Grammar
from tasksgenerator.dial_programs_task_generator import DialProgramsTasksGenerator

from tasksgenerator.tasks_generator import (
    AbstractTasksGenerator,
    ManualCurriculumTasksGenerator,
    TasksGeneratorRegistry,
    TaskCurriculum,
    DrawingTask,
    random_sample_ratio_ordered_array,
)
from tasksgenerator.bases_parts_tasks_generator import *
from tasksgenerator.abstract_bases_parts_programs_tasks_generator import *

from tasksgenerator.s12_s13_tasks_generator import RANDOM_SEED
from tasksgenerator.nuts_bolts_programs_tasks_generator import *


@TasksGeneratorRegistry.register
class WheelsProgramsTasksGenerator(AbstractBasesAndPartsProgramsTasksGenerator):
    name = "wheels_programs"

    def _generate_truck_bases_strings(
        self,
        head_width,
        head_height,
        body_width,
        body_height,
        nose_scale=str(0.5),
        reverse=False,
    ):
        """Generates 'trucks' comprised of a head (with a 'nose') and a body. Trucks can face left or right."""

        n_segments = 3

        heights = [body_height, head_height, f"(* {head_height} {nose_scale})"]
        widths = [body_width, head_width, f"(* {head_width} {nose_scale})"]

        if reverse:
            heights.reverse()
            widths.reverse()

        return self._generate_basic_n_segment_bases_string(
            primitives=[RECTANGLE] * n_segments,
            heights=heights,
            widths=widths,
            float_locations=[FLOAT_TOP] * n_segments,
            right_margins=[STR_ZERO] * n_segments,
        )

    def _generate_train_bases_strings(
        self,
        caboose_primitives,
        caboose_heights,
        caboose_widths,
        caboose_floats,
        reflect_caboose_for_head,
        body_primitives,
        body_heights,
        body_widths,
        body_floats,
        body_repetitions,
        car_margins,
        show_doors=False,
    ):
        """Generates 'trains' comprised of a caboose at each end and one or more repeated body segments.
        reflect_caboose_for_head: we reverse the order of the head.
        car_margins: scalar value for spacing.
        """
        head_primitives, head_heights, head_widths, head_floats = (
            copy.deepcopy(caboose_primitives),
            copy.deepcopy(caboose_heights),
            copy.deepcopy(caboose_widths),
            copy.deepcopy(caboose_floats),
        )
        if reflect_caboose_for_head:
            head_primitives.reverse()
            head_heights.reverse()
            head_widths.reverse()
            head_floats.reverse()

        n_segments = 2 * len(caboose_primitives) + body_repetitions * len(
            body_primitives
        )

        # Again, we keep the majority of these calculations out of the DreamCoder for now.
        # Tricky: we only want spacing between the cars, not between the segments of the body.
        caboose_margin = [0] * (len(caboose_primitives) - 1) + [car_margins]
        body_margin = ([0] * (len(body_primitives) - 1)) + [
            car_margins
        ] * body_repetitions
        head_margin = [0] * len(caboose_primitives)

        (
            strokes,
            stroke_strings,
            min_x,
            max_x,
            min_y,
            max_y,
        ) = self._generate_basic_n_segment_bases_string(
            primitives=caboose_primitives
            + body_primitives * body_repetitions
            + head_primitives,
            heights=caboose_heights + body_heights * body_repetitions + head_heights,
            widths=caboose_widths + body_widths * body_repetitions + head_widths,
            float_locations=caboose_floats
            + body_floats * body_repetitions
            + head_floats,
            right_margins=caboose_margin + body_margin + head_margin,
        )

        if show_doors:
            window = T_string(r_string[0], r_string[1], s=str(MEDIUM))
            n_windows = 2 * body_repetitions
            (
                new_strokes,
                new_stroke_strings,
                _,
                _,
                _,
                _,
            ) = self._generate_n_objects_on_grid_x_y_limits_string(
                object=window[0],
                object_string=window[-1],
                object_center=(0, 0),
                object_height=1,
                object_width=1,
                min_x=-body_widths[0] * body_repetitions * 0.5 + MEDIUM,
                max_x=body_widths[0] * body_repetitions * 0.5 - MEDIUM,
                min_y=body_heights[0] * 0.5,
                max_y=body_heights[0] * 0.5,
                n_rows=1,
                n_columns=n_windows,
                float_location=FLOAT_CENTER,
                grid_indices=range(n_windows),
            )
            strokes = [strokes[0] + new_strokes[0]]
            stroke_strings = [stroke_strings, new_stroke_strings]

        if type(stroke_strings) == list:
            object_string = connect_strokes(stroke_strings)
        else:
            object_string = stroke_strings
        return strokes, object_string, min_x, max_x, min_y, max_y

    def _generate_buggy_bases_strings(
        self,
        tier_heights,
        tier_widths,
        nose_tail_heights=[STR_ZERO],
        nose_tail_widths=[STR_ZERO],
        antenna=None,
        antenna_height=None,
        n_windows=0,
    ):
        """Generates 'buggies' consisting of one or more tiers of cars and an optional antenna and windows."""
        nose_tail_primitives = [RECTANGLE]
        if nose_tail_heights[0] == STR_ZERO:
            nose_tail_primitives, nose_tail_heights, nose_tail_widths = [], [], []
        # First tier is a base.
        base_primitives = nose_tail_primitives + [RECTANGLE] + nose_tail_primitives
        base_heights = nose_tail_heights + [tier_heights[0]] + nose_tail_heights
        base_widths = nose_tail_widths + [tier_widths[0]] + nose_tail_widths
        base_float_locations = [FLOAT_TOP] * len(base_primitives)
        base_right_margins = [0] * len(base_primitives)
        (
            strokes,
            stroke_strings,
            min_x,
            max_x,
            min_y,
            max_y,
        ) = self._generate_basic_n_segment_bases_string(
            primitives=base_primitives,
            heights=base_heights,
            widths=base_widths,
            float_locations=base_float_locations,
            right_margins=base_right_margins,
        )
        # Add additional tiers.
        if len(tier_heights) > 1:
            for tier_height, tier_width in zip(tier_heights[1:], tier_widths[1:]):
                tier_rect = scaled_rectangle_string(w=tier_width, h=tier_height)
                (
                    new_strokes,
                    new_stroke_strings,
                    new_min_x,
                    new_max_x,
                    new_min_y,
                    new_max_y,
                ) = self._generate_object_on_location_string(
                    object=tier_rect[0],
                    object_string=tier_rect[1],
                    object_center=(0, 0),
                    object_height=tier_height,
                    object_width=tier_width,
                    location=(0, max_y),
                    float_location=FLOAT_TOP,
                    x_margin=0,
                    y_margin=0,
                )
                max_y += peval(tier_height)
                strokes = [strokes[0] + new_strokes[0]]
                stroke_strings = connect_strokes([stroke_strings, new_stroke_strings])
                min_x, max_x = min(peval(min_x), peval(new_min_x)), max(
                    peval(new_max_x), peval(max_x)
                )
        # Add optional windows.
        if n_windows > 0:
            window = T_string(r_string[0], r_string[1], s=str(MEDIUM))
            (
                new_strokes,
                new_stroke_strings,
                _,
                _,
                _,
                _,
            ) = self._generate_n_objects_on_grid_x_y_limits_string(
                object=window[0],
                object_string=window[1],
                object_center=(0, 0),
                object_height=1,
                object_width=1,
                min_x=-tier_widths[0] * 0.5 * THREE_QUARTER_SCALE,
                max_x=tier_widths[0] * 0.5 * THREE_QUARTER_SCALE,
                min_y=tier_heights[0] * 0.5,
                max_y=tier_heights[0] * 0.5,
                n_rows=1,
                n_columns=n_windows,
                float_location=FLOAT_CENTER,
                grid_indices=range(n_windows),
            )
            strokes = [strokes[0] + new_strokes[0]]
            stroke_strings = connect_strokes([stroke_strings, new_stroke_strings])

        # Add optional antenna.
        if antenna is not None:
            (
                new_strokes,
                new_stroke_strings,
                new_min_x,
                new_max_x,
                new_min_y,
                new_max_y,
            ) = self._generate_object_on_location_string(
                object=antenna[0],
                object_string=antenna[1],
                object_center=(0, 0),
                object_height=antenna_height,
                object_width=1,
                location=(0, max_y),
                float_location=FLOAT_TOP,
                x_margin=0,
                y_margin=0,
            )
            max_y += antenna_height
            strokes = [strokes[0] + new_strokes[0]]
            stroke_strings = connect_strokes([stroke_strings, new_stroke_strings])
            min_x, max_x = min(peval(min_x), peval(new_min_x)), max(
                peval(new_max_x), peval(max_x)
            )

        return strokes, stroke_strings, min_x, max_x, min_y, max_y

    def _generate_row_of_wheels_strings(
        self,
        outer_shapes,
        outer_shapes_min_size,
        inner_shapes,
        inner_shapes_max_size,
        n_decorators,
        n_spokes,
        min_x,
        max_x,
        paired_wheels,
        n_wheels,
        wheel_scale=1.0,
        float_location=FLOAT_BOTTOM,
    ):
        nuts_bolts_generator = NutsBoltsProgramsTasksGenerator()
        (
            base_wheel,
            base_wheel_string,
            synthetic_dict,
            wheel_height,
            wheel_height_string,
        ) = nuts_bolts_generator._generate_perforated_shapes_string(
            outer_shapes=outer_shapes,
            outer_shapes_min_size=f"(* {outer_shapes_min_size} {wheel_scale})",
            inner_shapes=inner_shapes,
            inner_shapes_max_size=f"(* {inner_shapes_max_size} {wheel_scale})",
            nesting_scale_unit=str(SCALE_UNIT),
            decorator_shape=c_string,
            n_decorators=str(n_decorators),
            n_spokes=n_spokes,  # This is never used.
            spoke_angle=np.pi,  # This is never used.
            spoke_length=outer_shapes_min_size
            * 0.5
            * wheel_scale,  # This is never used.
        )

        if paired_wheels:
            # Double the wheel.
            _, x_shift = M_string(x=wheel_height_string)
            base_wheel_string = f"(repeat {base_wheel_string} 2 {x_shift})"
            base_wheel = peval(base_wheel_string)

        # TODO: implement paired wheels.
        min_x = f"(+ {min_x} (* 0.5 {wheel_height}))"
        max_x = f"(- {max_x} (* 0.5 {wheel_height}))"
        return self._generate_n_objects_on_grid_x_y_limits_string(
            object=base_wheel[0],
            object_string=base_wheel_string,
            object_center=(STR_ZERO, STR_ZERO),
            object_height=wheel_height,
            object_width=wheel_height,
            min_x=min_x,
            max_x=max_x,
            min_y=STR_ZERO,
            max_y=STR_ZERO,
            n_rows=1,
            n_columns=n_wheels,
            float_location=float_location,
        )

    def _generate_wheels_strings_iterator(
        self,
        min_x,
        max_x,
        n_wheels,
        paired_wheels=False,
        float_location=FLOAT_BOTTOM,
        wheel_scale=1.0,
    ):
        for outer_shapes in [[c_string], [c_string, c_string]]:
            for outer_shapes_min_size in [MEDIUM * MEDIUM]:
                for inner_shapes in [[c_string], [r_string]]:
                    for inner_shapes_max_size in [f"(* {SMALL} {SCALE_UNIT})"]:
                        for n_decorators in [4, 8]:
                            yield self._generate_row_of_wheels_strings(
                                outer_shapes=outer_shapes,
                                outer_shapes_min_size=outer_shapes_min_size,
                                inner_shapes=inner_shapes,
                                inner_shapes_max_size=inner_shapes_max_size,
                                n_decorators=n_decorators,
                                n_spokes=0,
                                min_x=min_x,
                                max_x=max_x,
                                paired_wheels=paired_wheels,
                                n_wheels=n_wheels,
                                float_location=float_location,
                                wheel_scale=wheel_scale,
                            )

    def _generate_parts_stimuli_strings(self, train_ratio=1.0):
        strokes, stroke_strings = [], []
        # Generate wheels.
        n_wheels_types = [1, 4]
        for n_wheels in n_wheels_types:
            wheels_iterator = self._generate_wheels_strings_iterator(
                f"(* {LARGE} -4)",
                f"(* {LARGE} 4)",
                n_wheels=n_wheels,
                float_location=FLOAT_CENTER,
                paired_wheels=False,
            )
            for (
                wheels_strokes,
                wheels_stroke_strings,
                wheels_min_x,
                wheels_max_x,
                wheels_min_y,
                wheels_max_y,
            ) in wheels_iterator:
                strokes += wheels_strokes
                stroke_strings.append(wheels_stroke_strings)
        for scale_wires in [True, False]:
            antenna_generator = DialProgramsTasksGenerator()
            n_wires = 3
            (
                antenna_object,
                antenna_string,
                antenna_dict,
            ) = antenna_generator._generate_stacked_antenna_strings(
                n_wires=n_wires,
                scale_wires=scale_wires,
                end_shape=None,
            )
            strokes += antenna_object
            stroke_strings.append(antenna_string)

        return random_sample_ratio_ordered_array(
            strokes, train_ratio, strings_array=stroke_strings
        )
