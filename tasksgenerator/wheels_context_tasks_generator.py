"""
wheels_programs_tasks_generator.py | Author: Catherine Wong.
Defines TasksGenerators that produce gadget tasks with wheels on them.
Threads program string generating logic through the generation.
"""

import math, random, itertools, copy
from sqlite3 import connect
from primitives.gadgets_primitives import *
from dreamcoder_programs.grammar import Grammar
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
    name = "wheels_context_programs"

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
        synthetic_dict = copy.deepcopy(SYNTHETIC_DICT)

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
            base_synthetic_dict,
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
        # Add the base to the synthetic dict.
        for k in base_synthetic_dict:
            synthetic_dict[k] += base_synthetic_dict[k]

        if show_doors:
            window_synthetic_dict = copy.deepcopy(SYNTHETIC_DICT)
            window = T_string(r_string[0], r_string[1], s=str(MEDIUM))
            window_synthetic_dict[LOW_LEVEL] += ["window_rectangle"]
            window_synthetic_dict[LOW_LEVEL_PARTS] += [r_string[1]]

            window_synthetic_dict[MID_LEVEL] += ["window_rectangle"]
            window_synthetic_dict[MID_LEVEL_PARTS] += [window[1]]

            n_windows = 2 * body_repetitions
            (
                new_strokes,
                new_stroke_strings,
                new_synthetic_dict,
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
                object_synthetic_dict=window_synthetic_dict,
            )
            strokes = [strokes[0] + new_strokes[0]]
            stroke_strings = [stroke_strings, new_stroke_strings]
            # Add the base to the synthetic dict.
            for k in new_synthetic_dict:
                synthetic_dict[k] += new_synthetic_dict[k]

        if type(stroke_strings) == list:
            object_string = connect_strokes(stroke_strings)
        else:
            object_string = stroke_strings
        return strokes, object_string, synthetic_dict, min_x, max_x, min_y, max_y

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
        synthetic_dict = copy.deepcopy(SYNTHETIC_DICT)

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
            base_synthetic_dict,
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
        # Add the base to the synthetic dict.
        for k in base_synthetic_dict:
            synthetic_dict[k] += base_synthetic_dict[k]

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
                min_x, max_x = (
                    min(peval(min_x), peval(new_min_x)),
                    max(peval(new_max_x), peval(max_x)),
                )

                # Replace the high-level with the whole base.

                shape_abstraction = "base_shape"
                synthetic_dict[LOW_LEVEL].append(shape_abstraction)
                synthetic_dict[LOW_LEVEL_PARTS].append("r_s")
                synthetic_dict[LOW_LEVEL_PARAMS].append(str(tier_width))
                # Mid-level: just choose the outer one.

                outer_shape_abstraction = "base_dial_hand"
                synthetic_dict[MID_LEVEL].append(outer_shape_abstraction)
                synthetic_dict[MID_LEVEL_PARTS].append("r_s")
                synthetic_dict[MID_LEVEL_PARAMS].append(str(tier_width))

                synthetic_dict[HIGH_LEVEL_PARTS] = [stroke_strings]

        # Add optional windows.
        if n_windows > 0:
            window = T_string(r_string[0], r_string[1], s=str(MEDIUM))
            window_synthetic_dict = copy.deepcopy(SYNTHETIC_DICT)
            window = T_string(r_string[0], r_string[1], s=str(MEDIUM))
            window_synthetic_dict[LOW_LEVEL] += ["window_rectangle"]
            window_synthetic_dict[LOW_LEVEL_PARTS] += [r_string[1]]

            window_synthetic_dict[MID_LEVEL] += ["window_rectangle"]
            window_synthetic_dict[MID_LEVEL_PARTS] += [window[1]]
            (
                new_strokes,
                new_stroke_strings,
                new_synthetic_dict,
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
            for k in new_synthetic_dict:
                synthetic_dict[k] += new_synthetic_dict[k]

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
            min_x, max_x = (
                min(peval(min_x), peval(new_min_x)),
                max(peval(new_max_x), peval(max_x)),
            )
            antenna_synthetic_dict = copy.deepcopy(antenna[-1])
            for k in antenna_synthetic_dict:
                synthetic_dict[k] += antenna_synthetic_dict[k]
        return strokes, stroke_strings, synthetic_dict, min_x, max_x, min_y, max_y

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
            wheel_synthetic_dict,
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
            base_wheel, base_wheel_string = T_string(
                peval(base_wheel_string),
                base_wheel_string,
                x=f"(* -0.5 {wheel_height})",
            )
            wheel_synthetic_dict[LOW_LEVEL] = wheel_synthetic_dict[LOW_LEVEL] * 2
            wheel_synthetic_dict[LOW_LEVEL_PARTS] = (
                wheel_synthetic_dict[LOW_LEVEL_PARTS] * 2
            )
            wheel_synthetic_dict[MID_LEVEL] = ["repeat_x"] + wheel_synthetic_dict[
                MID_LEVEL
            ]
            wheel_synthetic_dict[MID_LEVEL_PARTS] = ["repeat_x"] + wheel_synthetic_dict[
                MID_LEVEL_PARTS
            ]
            wheel_synthetic_dict[MID_LEVEL_PARAMS] = ["2"] + wheel_synthetic_dict[
                MID_LEVEL_PARAMS
            ]
            wheel_synthetic_dict[HIGH_LEVEL] = ["double_wheel"]
            wheel_synthetic_dict[HIGH_LEVEL_PARTS] = [base_wheel_string]

            min_x = f"(+ {min_x} (* 1 {wheel_height}))"
            max_x = f"(- {max_x} (* 1 {wheel_height}))"
        else:
            min_x = f"(+ {min_x} (* 0.5 {wheel_height}))"
            max_x = f"(- {max_x} (* 0.5 {wheel_height}))"

        wheel_synthetic_dict = copy.deepcopy(wheel_synthetic_dict)
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
            n_columns=n_wheels if not paired_wheels else n_wheels / 2,
            float_location=float_location,
            object_synthetic_dict=wheel_synthetic_dict,
        )

    def _generate_wheels_strings_iterator(
        self,
        min_x,
        max_x,
        n_wheels,
        paired_wheels=False,
        float_location=FLOAT_BOTTOM,
        wheel_scale=1.0,
        context=CONTEXT_LARGE_ABSTRACTIONS,
        variance=True,
    ):
        if context == CONTEXT_LARGE_ABSTRACTIONS or not variance:
            possible_outer_shapes = [[c_string]]
            possible_n_decorators = [4]
        else:
            possible_outer_shapes = [[c_string], [c_string, c_string]]
            possible_n_decorators = [4, 6, 8]

        for outer_shapes in possible_outer_shapes:
            for outer_shapes_min_size in [MEDIUM * MEDIUM]:
                for inner_shapes in [[c_string]]:
                    for inner_shapes_max_size in [f"(* {SMALL} {SCALE_UNIT})"]:
                        for n_decorators in possible_n_decorators:
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
        strokes, stroke_strings, stroke_dicts = [], [], []
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
                wheels_stroke_dicts,
                wheels_min_x,
                wheels_max_x,
                wheels_min_y,
                wheels_max_y,
            ) in wheels_iterator:
                strokes += wheels_strokes
                stroke_strings.append(wheels_stroke_strings)
                stroke_dicts.append(wheels_stroke_dicts)
        for scale_wires in [True, False]:
            antenna_generator = DialProgramsTasksGenerator()
            n_wires = 3
            (
                antenna_object,
                antenna_string,
                antenna_dict,
            ) = antenna_generator._generate_stacked_antenna_strings(
                n_wires=n_wires, scale_wires=scale_wires, end_shape=None,
            )
            strokes += antenna_object
            stroke_strings.append(antenna_string)
            stroke_dicts.append(antenna_dict)

        return random_sample_ratio_ordered_array(
            strokes, train_ratio, strings_array=list(zip(stroke_strings, stroke_dicts))
        )

    def _generate_truck_stimuli_strings(
        self,
        train_ratio=1.0,
        context=CONTEXT_LARGE_ABSTRACTIONS,
        generation_probability=1.0,
    ):

        if context == CONTEXT_LARGE_ABSTRACTIONS:
            possible_body_sizes = [
                (LARGE * 8, LARGE * 4),
            ]
        else:
            possible_body_sizes = [
                (LARGE * 8, LARGE * 4),
                (LARGE * 10, LARGE * 3),
            ]

        big_width = f"(* {LARGE} 8)"
        strokes, stroke_strings, stroke_dicts = [], [], []
        for head_width in [LARGE]:
            for head_height in [LARGE * 2]:
                for body_width, body_height in possible_body_sizes:
                    reverse = False
                    nose_scale = THREE_QUARTER_SCALE

                    (
                        base_strokes,
                        base_stroke_strings,
                        base_synthetic_dict,
                        base_min_x,
                        base_max_x,
                        base_min_y,
                        base_max_y,
                    ) = self._generate_truck_bases_strings(
                        head_width=head_width,
                        head_height=body_height * THREE_QUARTER_SCALE,
                        body_width=body_width,
                        body_height=body_height,
                        nose_scale=nose_scale,
                        reverse=reverse,
                    )
                    n_wheels_types = [2, 4, 5, 6]
                    for n_wheels in n_wheels_types:
                        for paired_wheels in [True, False]:
                            if (n_wheels == 2 or n_wheels % 2 != 0) and paired_wheels:
                                continue
                            # paired_wheels = True if n_wheels > 2 else False
                            wheels_iterator = self._generate_wheels_strings_iterator(
                                base_min_x,
                                base_max_x,
                                n_wheels=n_wheels,
                                float_location=FLOAT_CENTER,
                                paired_wheels=paired_wheels,
                                context=context,
                            )
                            for (
                                wheels_strokes,
                                wheels_strokes_strings,
                                wheels_synthetic_dict,
                                wheels_min_x,
                                wheels_max_x,
                                wheels_min_y,
                                wheels_max_y,
                            ) in wheels_iterator:

                                synthetic_dict = copy.deepcopy(base_synthetic_dict)
                                truck_strokes = [base_strokes[0] + wheels_strokes[0]]
                                truck_stroke_strings = connect_strokes(
                                    [base_stroke_strings, wheels_strokes_strings]
                                )
                                for k in wheels_synthetic_dict:
                                    synthetic_dict[k] += wheels_synthetic_dict[k]
                                strokes += truck_strokes
                                stroke_strings.append(truck_stroke_strings)
                                stroke_dicts.append(synthetic_dict)

        return random_sample_ratio_ordered_array(
            strokes, train_ratio, strings_array=list(zip(stroke_strings, stroke_dicts))
        )

    def _generate_train_stimuli_strings(
        self,
        train_ratio=1.0,
        context=CONTEXT_LARGE_ABSTRACTIONS,
        generation_probability=1.0,
    ):
        strokes, stroke_strings, stroke_dicts = [], [], []

        body_height = SMALL * 5
        caboose_width = MEDIUM
        caboose_height = body_height * THREE_QUARTER_SCALE
        caboose_primitives, caboose_heights, caboose_widths, caboose_floats = (
            [RECTANGLE,],
            [caboose_height],
            [caboose_width],
            [FLOAT_TOP,],
        )
        small_width, large_width = SMALL * 7, SMALL * 9
        if context == CONTEXT_LARGE_ABSTRACTIONS:
            possible_body_widths = [small_width]
            possible_show_doors = [False]
        else:
            possible_body_widths = [small_width, large_width]
            possible_show_doors = [False]

        for body_heights in [body_height]:
            for body_widths in possible_body_widths:
                body_repetitions = [2] if body_widths > small_width else [2, 3]
                for body_repetitions in body_repetitions:
                    for car_margins in [QUARTER_SCALE]:
                        for show_doors in possible_show_doors:

                            (
                                base_strokes,
                                base_stroke_strings,
                                base_synthetic_dict,
                                base_min_x,
                                base_max_x,
                                base_min_y,
                                base_max_y,
                            ) = self._generate_train_bases_strings(
                                caboose_primitives=caboose_primitives,
                                caboose_heights=caboose_heights,
                                caboose_widths=caboose_widths,
                                caboose_floats=caboose_floats,
                                reflect_caboose_for_head=True,
                                body_primitives=[RECTANGLE],
                                body_heights=[body_heights],
                                body_widths=[body_widths],
                                body_floats=[FLOAT_TOP],
                                body_repetitions=body_repetitions,
                                car_margins=car_margins,
                                show_doors=show_doors,
                            )

                            n_wheels_types = [
                                body_repetitions * 2,
                                body_repetitions * 3,
                                body_repetitions * 4,
                            ]
                            for n_wheels in n_wheels_types:
                                wheels_iterator = self._generate_wheels_strings_iterator(
                                    base_min_x,
                                    base_max_x,
                                    n_wheels=n_wheels,
                                    float_location=FLOAT_CENTER,
                                    wheel_scale=THREE_QUARTER_SCALE,
                                    context=context,
                                    variance=False,
                                )
                                for (
                                    wheels_strokes,
                                    wheels_strokes_strings,
                                    wheels_synthetic_dict,
                                    wheels_min_x,
                                    wheels_max_x,
                                    wheels_min_y,
                                    wheels_max_y,
                                ) in wheels_iterator:
                                    synthetic_dict = copy.deepcopy(base_synthetic_dict)
                                    train_strokes = [
                                        base_strokes[0] + wheels_strokes[0]
                                    ]
                                    train_stroke_strings = connect_strokes(
                                        [base_stroke_strings, wheels_strokes_strings]
                                    )
                                    for k in wheels_synthetic_dict:
                                        synthetic_dict[k] += wheels_synthetic_dict[k]
                                    strokes += train_strokes
                                    stroke_strings.append(train_stroke_strings)
                                    stroke_dicts.append(synthetic_dict)
        return random_sample_ratio_ordered_array(
            strokes, train_ratio, strings_array=list(zip(stroke_strings, stroke_dicts))
        )

    def _generate_buggy_stimuli_strings(
        self,
        train_ratio=1.0,
        generation_probability=0.80,
        context=CONTEXT_LARGE_ABSTRACTIONS,
    ):
        if context == CONTEXT_LARGE_ABSTRACTIONS:

            possible_tier_widths = [LARGE * n for n in [8]]

        else:

            possible_tier_widths = [LARGE * n for n in [5, 8]]

        strokes, stroke_strings, stroke_dicts = [], [], []
        for scale_wires in [False]:
            antenna_generator = DialProgramsTasksGenerator()
            n_wires = 3
            (
                antenna_object,
                antenna_string,
                antenna_dict,
            ) = antenna_generator._generate_stacked_antenna_strings(
                n_wires=n_wires, scale_wires=scale_wires, end_shape=None,
            )
            antenna_object = antenna_object[0]

            antenna_base_height = 3
            antenna_height = antenna_base_height + (SMALL * (n_wires - 1))

            for first_tier_height, second_tier_height in [
                (MEDIUM * 3, SMALL),
            ]:
                small_width = LARGE * 7
                for first_tier_width in possible_tier_widths:
                    for (nose_tail_heights, nose_tail_widths,) in [
                        (0, 0),
                        (first_tier_height * THREE_QUARTER_SCALE, LARGE,),
                    ]:
                        if context == CONTEXT_LARGE_ABSTRACTIONS:
                            possible_antenna = [None]
                        else:
                            possible_antenna = [
                                None,
                            ]
                        for antenna in possible_antenna:
                            n_wheel_sets = (
                                [2, 4, 6] if first_tier_width <= small_width else [2, 6]
                            )
                            for n_wheels in n_wheel_sets:
                                (
                                    base_strokes,
                                    base_stroke_strings,
                                    base_synthetic_dict,
                                    base_min_x,
                                    base_max_x,
                                    base_min_y,
                                    base_max_y,
                                ) = self._generate_buggy_bases_strings(
                                    tier_heights=[
                                        first_tier_height,
                                        second_tier_height,
                                    ],
                                    tier_widths=[
                                        first_tier_width,
                                        first_tier_width * THREE_QUARTER_SCALE,
                                    ],
                                    nose_tail_heights=[nose_tail_heights],
                                    nose_tail_widths=[nose_tail_widths],
                                    antenna=antenna,
                                    antenna_height=antenna_height,
                                    n_windows=0,
                                )

                                wheels_iterator = self._generate_wheels_strings_iterator(
                                    base_min_x + nose_tail_widths,
                                    base_max_x - nose_tail_widths,
                                    n_wheels=n_wheels,
                                    float_location=FLOAT_CENTER,
                                    context=context,
                                )
                                for (
                                    wheels_strokes,
                                    wheels_strokes_strings,
                                    wheels_synthetic_dict,
                                    wheels_min_x,
                                    wheels_max_x,
                                    wheels_min_y,
                                    wheels_max_y,
                                ) in wheels_iterator:
                                    buggy_strokes = [
                                        base_strokes[0] + wheels_strokes[0]
                                    ]
                                    buggy_stroke_strings = connect_strokes(
                                        [base_stroke_strings, wheels_strokes_strings]
                                    )
                                    synthetic_dict = copy.deepcopy(SYNTHETIC_DICT)

                                    # Add the base.
                                    for k in base_synthetic_dict:
                                        synthetic_dict[k] += base_synthetic_dict[k]

                                    # Add the wheels.
                                    for k in wheels_synthetic_dict:
                                        synthetic_dict[k] += wheels_synthetic_dict[k]
                                    if random.uniform(0, 1) > generation_probability:
                                        continue
                                    strokes += buggy_strokes
                                    stroke_strings.append(buggy_stroke_strings)
                                    stroke_dicts.append(synthetic_dict)
        return random_sample_ratio_ordered_array(
            strokes, train_ratio, strings_array=list(zip(stroke_strings, stroke_dicts))
        )

    def _generate_strokes_strings_for_stimuli(
        self,
        train_ratio=0.8,
        generation_probability=1.0,  # Probabilistically generate from space
        context=None,
    ):
        """Main generator function. Returns a list of all stimuli from this generative model as sets of strokes."""
        train, test = [], []
        train_strings, test_strings = [], []
        for generator_fn in [
            self._generate_truck_stimuli_strings,
            self._generate_train_stimuli_strings,
            self._generate_buggy_stimuli_strings,
        ]:
            (
                generator_train,
                generator_test,
                generator_train_strings,
                generator_test_strings,
            ) = generator_fn(train_ratio, generation_probability=1.0, context=context)
            train += generator_train
            test += generator_test
            train_strings += generator_train_strings
            test_strings += generator_test_strings

        return train, test, train_strings, test_strings

    def _generate_train_test_tasks(
        self,
        num_tasks_to_generate_per_condition=AbstractTasksGenerator.GENERATE_ALL,
        train_ratio=0.8,
        max_train=200,
        max_test=50,
        context=None,
    ):
        # Currently generates all tasks as single entities. Does not generate a curriculum.
        train_tasks, test_tasks = self._generate_drawing_tasks_from_strokes(
            num_tasks_to_generate_per_condition,
            request_type=object_primitives.tstroke,
            render_parsed_program_fn=object_primitives.render_parsed_program,
            task_generator_name=self.name,
            train_ratio=train_ratio,
            context=context,
        )
        max_train = len(train_tasks) if max_train == None else max_train
        max_test = len(test_tasks) if max_test == None else max_test
        return train_tasks[:max_train], test_tasks[:max_test]

    def generate_tasks_curriculum(
        self, num_tasks_to_generate_per_condition, train_ratio=0.8
    ):
        """:ret: a curriculum that randomly samples among the train ratio for the simple and complex stimuli."""
        task_curriculum = TaskCurriculum(
            curriculum_id=num_tasks_to_generate_per_condition,
            task_generator_name=self.name,
            grammar=self.grammar,
        )

        for context in [CONTEXT_LARGE_ABSTRACTIONS, CONTEXT_SMALL_ABSTRACTIONS]:
            train_tasks, test_tasks = self._generate_train_test_tasks(
                num_tasks_to_generate_per_condition, train_ratio=0.8, context=context,
            )
            # Rename all of the tasks.
            tasks = train_tasks + test_tasks
            for idx, task in enumerate(tasks):
                padded_index = str.zfill(str(idx), 3)

                task.name = f"{self.name}_{context}_{padded_index}"

            # Add the train tasks.
            task_curriculum.add_tasks(
                split=context, condition=self.name, curriculum_block=0, tasks=tasks,
            )
        return task_curriculum
