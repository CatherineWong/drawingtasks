"""
furniture_context_tasks_generator.py | Author: Catherine Wong.

Generates programs at varying contexts.

Avoids randomizing choices.
"""
import copy
import itertools
import math
import random

from dreamcoder_programs.grammar import Grammar
from primitives.gadgets_primitives import *

from tasksgenerator.bases_parts_tasks_generator import *
from tasksgenerator.s12_s13_tasks_generator import RANDOM_SEED
from tasksgenerator.tasks_generator import (
    AbstractTasksGenerator,
    DrawingTask,
    ManualCurriculumTasksGenerator,
    TaskCurriculum,
    TasksGeneratorRegistry,
    random_sample_ratio_ordered_array,
)
from tasksgenerator.wheels_programs_tasks_generator import *
from tasksgenerator.furniture_tasks_generator import FurnitureTasksGenerator

octagon_string = T_string(octagon_string[0], octagon_string[1], s=THREE_QUARTER_SCALE)


@TasksGeneratorRegistry.register
class FurnitureContextTasksGenerator(AbstractBasesAndPartsProgramsTasksGenerator):
    name = "furniture_context_programs"

    def _generate_drawer_pulls_strings_iterator(
        self,
        min_x,
        max_x,
        n_drawer_pulls,
        float_location=FLOAT_CENTER,
        drawer_pull_scale=str(SCALE_UNIT),
        context=CONTEXT_LARGE_ABSTRACTIONS,
    ):
        wheels_generator = WheelsProgramsTasksGenerator()

        if context == CONTEXT_LARGE_ABSTRACTIONS:
            possible_outer_shapes = [[]]
            possible_inner_shapes = [[r_string]]
        else:
            # Arbitrary context.
            possible_outer_shapes = [
                [],
            ]
            possible_inner_shapes = [[cc_string], [r_string]]

        # Always have the base ones.
        base_min_size = MEDIUM * MEDIUM
        for outer_shapes in possible_outer_shapes:
            for outer_shapes_min_size in [base_min_size]:
                for inner_shapes in possible_inner_shapes:
                    for inner_shapes_max_size in [base_min_size * THREE_QUARTER_SCALE]:
                        for n_decorators in [0]:
                            # Row of wheels is very similar to a set of drawer pulls.
                            yield wheels_generator._generate_row_of_wheels_strings(
                                outer_shapes=outer_shapes,
                                outer_shapes_min_size=outer_shapes_min_size,
                                inner_shapes=inner_shapes,
                                inner_shapes_max_size=inner_shapes_max_size,
                                n_decorators=n_decorators,
                                n_spokes=0,
                                min_x=min_x,
                                max_x=max_x,
                                paired_wheels=False,
                                n_wheels=n_drawer_pulls,
                                float_location=float_location,
                                wheel_scale=drawer_pull_scale,
                            )

    def _generate_drawers_strings_iterator(
        self,
        n_drawers=1,
        base_heights_and_widths=[
            (SMALL * 3, MEDIUM * 9),
            (SMALL * 4, SMALL * 9),
            (SMALL * 5, SMALL * 12),
        ],
        stack_float_locations=FLOAT_CENTER,
        generation_probability=1.0,
        context=CONTEXT_LARGE_ABSTRACTIONS,
    ):

        if context == CONTEXT_LARGE_ABSTRACTIONS:
            base_heights_and_widths = [
                # (SMALL * 3, MEDIUM * 9),
                (SMALL * 5, SMALL * 12),
            ]
            possible_drawer_pulls = [2]
        else:
            base_heights_and_widths = [
                (SMALL * 3, SMALL * 15),
                (SMALL * 5, SMALL * 12),
            ]
            # Arbitrary context.
            possible_drawer_pulls = [0, 2]

        original_generator = generator = TasksGeneratorRegistry[
            FurnitureTasksGenerator.name
        ]
        # Generates strokes for drawers with and without drawer pulls. Returns strokes at the center.
        for (base_height, base_width) in base_heights_and_widths:
            if base_height > SMALL * 4 and n_drawers > 3:
                continue
            (
                base_strokes,
                base_stroke_strings,
                base_synthetic_dict,
                base_min_x,
                base_max_x,
                base_min_y,
                base_max_y,
            ) = self._generate_basic_n_segment_bases_string(
                primitives=[RECTANGLE],
                heights=[base_height],
                widths=[base_width],
                float_locations=[FLOAT_CENTER],
            )
            drawn_blank = False

            for n_drawer_pulls in possible_drawer_pulls:
                for (
                    drawer_pull_idx,
                    (
                        drawer_pull_strokes,
                        drawer_pull_strings,
                        drawer_pull_synthetic_dict,
                        drawer_pull_strokes_min_x,
                        drawer_pull_strokes_max_x,
                        drawer_pull_strokes_min_y,
                        drawer_pull_strokes_max_y,
                    ),
                ) in enumerate(
                    self._generate_drawer_pulls_strings_iterator(
                        min_x=base_min_x + (base_width * QUARTER_SCALE),
                        max_x=base_max_x - (base_width * QUARTER_SCALE),
                        n_drawer_pulls=n_drawer_pulls,
                        float_location=FLOAT_CENTER,
                        drawer_pull_scale=SCALE_UNIT,
                        context=context,
                    )
                ):
                    drawer_spacing = base_height * QUARTER_SCALE

                    original_drawer_pulls = list(
                        original_generator._generate_drawer_pulls_iterator(
                            min_x=base_min_x + (base_width * QUARTER_SCALE),
                            max_x=base_max_x - (base_width * QUARTER_SCALE),
                            n_drawer_pulls=n_drawer_pulls,
                            float_location=FLOAT_CENTER,
                            drawer_pull_scale=SCALE_UNIT,
                        )
                    )

                    (
                        _,
                        original_drawer_pull_strokes_min_x,
                        original_drawer_pull_strokes_max_x,
                        original_drawer_pull_strokes_min_y,
                        original_drawer_pull_strokes_max_y,
                    ) = original_drawer_pulls[drawer_pull_idx]

                    if original_drawer_pull_strokes_max_y >= (
                        base_max_y - (drawer_spacing)
                    ) or original_drawer_pull_strokes_max_x >= (
                        base_max_x - (drawer_spacing)
                    ):

                        continue
                    # if peval(drawer_pull_strokes_max_y) >= (
                    #     base_max_y - (drawer_spacing)
                    # ) or peval(drawer_pull_strokes_max_x) >= (
                    #     base_max_x - (drawer_spacing)
                    # ):
                    #     print(
                    #         peval(drawer_pull_strokes_max_y),
                    #         peval(drawer_pull_strokes_max_x),
                    #     )
                    #     continue

                    # Insanely, let's copy the logic.

                    if n_drawer_pulls < 1 and drawn_blank:
                        continue

                    drawer_strokes = [base_strokes[0] + drawer_pull_strokes[0]]
                    drawer_stroke_string = connect_strokes(
                        [base_stroke_strings, drawer_pull_strings]
                    )

                    if n_drawer_pulls < 1:
                        drawn_blank = True

                    # Draw the grid of drawers.
                    total_height = (n_drawers - 1) * (base_height + drawer_spacing)
                    min_y, max_y = (
                        -total_height * 0.5,
                        total_height * 0.5,
                    )

                    drawer_synthetic_dict = copy.deepcopy(SYNTHETIC_DICT)
                    # Add the drawer pulls.
                    for k in drawer_pull_synthetic_dict:
                        drawer_synthetic_dict[k] += drawer_pull_synthetic_dict[k]
                    # Add the base.
                    for k in base_synthetic_dict:
                        drawer_synthetic_dict[k] += base_synthetic_dict[k]

                    (
                        drawer_stack_strokes,
                        drawer_stack_stroke_strings,
                        drawer_stack_synthetic_dict,
                        drawer_stack_strokes_min_x,
                        drawer_stack_strokes_max_x,
                        drawer_stack_strokes_min_y,
                        drawer_stack_strokes_max_y,
                    ) = self._generate_n_objects_on_grid_x_y_limits_string(
                        object=drawer_strokes[0],
                        object_string=drawer_stroke_string,
                        object_center=(0, 0),
                        object_height=base_height,
                        object_width=base_width,
                        min_x=0,
                        max_x=0,
                        min_y=min_y,
                        max_y=max_y,
                        n_rows=n_drawers,
                        n_columns=1,
                        float_location=stack_float_locations,
                        grid_indices=range(n_drawers * n_drawers),
                        object_synthetic_dict=drawer_synthetic_dict,
                    )
                    if stack_float_locations in [FLOAT_TOP, FLOAT_BOTTOM]:

                        (drawer_stack_strokes, drawer_stack_stroke_strings,) = T_string(
                            drawer_stack_strokes[0],
                            drawer_stack_stroke_strings,
                            y=drawer_spacing,
                        )
                        drawer_stack_strokes = [drawer_stack_strokes]

                    # Draw the enclosing around them.
                    total_height = (n_drawers * base_height) + (
                        (n_drawers + 1) * drawer_spacing
                    )
                    enclosure_width = base_width + (2 * drawer_spacing)
                    (
                        enclosure_strokes,
                        enclosure_stroke_string,
                        enclosure_synthetic_dict,
                        enclosure_min_x,
                        enclosure_max_x,
                        enclosure_min_y,
                        enclosure_max_y,
                    ) = self._generate_basic_n_segment_bases_string(
                        primitives=[RECTANGLE],
                        heights=[total_height],
                        widths=[enclosure_width],
                        float_locations=[stack_float_locations],
                    )
                    drawer_strokes = [drawer_stack_strokes[0] + enclosure_strokes[0]]
                    drawer_stroke_string = connect_strokes(
                        [drawer_stack_stroke_strings, enclosure_stroke_string]
                    )
                    drawer_synthetic_dict = drawer_stack_synthetic_dict
                    for k in enclosure_synthetic_dict:
                        drawer_stack_synthetic_dict[k] += enclosure_synthetic_dict[k]

                    if random.uniform(0, 1) > generation_probability:
                        continue

                    yield (
                        drawer_strokes,
                        drawer_stroke_string,
                        drawer_synthetic_dict,
                        enclosure_min_x,
                        enclosure_max_x,
                        enclosure_min_y,
                        enclosure_max_y,
                    )

    def _generate_feet_strings_iterator(
        self,
        n_feet,
        min_x,
        max_x,
        min_y,
        max_y,
        feet_heights=[SMALL, MEDIUM * 2, MEDIUM * 4],
        generation_probability=1.0,
        context=CONTEXT_LARGE_ABSTRACTIONS,
    ):
        short_v_line = T_string(
            short_l_string[0], short_l_string[1], theta=STR_VERTICAL
        )

        if context == CONTEXT_LARGE_ABSTRACTIONS:
            possible_feet_heights = [MEDIUM * 4]
            possible_foot_primitives = [LINE]
        else:
            # Arbitrary context.
            possible_feet_heights = feet_heights
            possible_foot_primitives = [RECTANGLE, LINE]

        # Adds a row of feet to the object. These can be short or tall.
        for foot_primitive in possible_foot_primitives:
            for foot_height in possible_feet_heights:
                foot_synthetic_dict = copy.deepcopy(SYNTHETIC_DICT)
                if foot_primitive == RECTANGLE:
                    foot_width = SMALL

                    foot = scaled_rectangle_string(w=foot_width, h=foot_height)

                    if n_feet > 2:
                        continue

                    shape_abstraction = "foot"
                    foot_synthetic_dict[LOW_LEVEL] = [shape_abstraction]
                    foot_synthetic_dict[LOW_LEVEL_PARTS] = ["r_s"]
                    foot_synthetic_dict[LOW_LEVEL_PARAMS] = [foot_width, foot_height]

                    foot_synthetic_dict[MID_LEVEL] = [shape_abstraction]
                    foot_synthetic_dict[MID_LEVEL_PARTS] = ["r_s"]
                    foot_synthetic_dict[MID_LEVEL_PARAMS] = [foot_width, foot_height]
                else:
                    foot_width = 0
                    foot = T_string(short_v_line[0], short_v_line[1], s=foot_height)
                    shape_abstraction = "foot"
                    foot_synthetic_dict[LOW_LEVEL] = [shape_abstraction]
                    foot_synthetic_dict[LOW_LEVEL_PARTS] = [short_v_line[-1]]
                    foot_synthetic_dict[LOW_LEVEL_PARAMS] = [foot_height]

                    foot_synthetic_dict[MID_LEVEL] = [shape_abstraction]
                    foot_synthetic_dict[MID_LEVEL_PARTS] = [short_v_line[-1]]
                    foot_synthetic_dict[MID_LEVEL_PARAMS] = [foot_height]

                (
                    feet_strokes,
                    feet_strokes_string,
                    feet_strokes_synthetic_dict,
                    feet_strokes_min_x,
                    feet_strokes_max_x,
                    feet_strokes_min_y,
                    feet_strokes_max_y,
                ) = self._generate_n_objects_on_grid_x_y_limits_string(
                    object=foot[0],
                    object_string=foot[1],
                    object_center=(0, 0),
                    object_height=foot_height
                    * 0.5,  # TODO: figure out what's going on.
                    object_width=foot_width if foot_width > 0 else 1,
                    min_x=peval(min_x) + foot_width * 0.5,
                    max_x=peval(max_x) - foot_width * 0.5,
                    min_y=min_y,
                    max_y=max_y,
                    n_rows=1,
                    n_columns=n_feet,
                    float_location=FLOAT_BOTTOM,
                    grid_indices=range(n_feet),
                    object_synthetic_dict=foot_synthetic_dict,
                )
                if random.uniform(0, 1) > generation_probability:
                    continue
                yield feet_strokes, feet_strokes_string, feet_strokes_synthetic_dict

    def _generate_parts_stimuli_strings(self, train_ratio=1.0):
        strokes, stroke_strings, stroke_dicts = [], [], []
        # Generate wheels.
        n_drawer_pulls = [1, 2]
        for n_pulls in n_drawer_pulls:
            for (
                drawer_pull_strokes,
                drawer_pull_stroke_strings,
                drawer_pull_stroke_dicts,
                drawer_pull_strokes_min_x,
                drawer_pull_strokes_max_x,
                drawer_pull_strokes_min_y,
                drawer_pull_strokes_max_y,
            ) in self._generate_drawer_pulls_strings_iterator(
                min_x=-LARGE * 4,
                max_x=LARGE * 4,
                n_drawer_pulls=n_pulls,
                float_location=FLOAT_CENTER,
                drawer_pull_scale=SCALE_UNIT,
            ):
                strokes += drawer_pull_strokes
                stroke_strings.append(drawer_pull_stroke_strings)
                stroke_dicts.append(drawer_pull_stroke_dicts)
        return random_sample_ratio_ordered_array(
            strokes, train_ratio, strings_array=list(zip(stroke_strings, stroke_dicts))
        )

    def _generate_stacked_drawers_stimuli_strings(
        self,
        total_drawers=4,
        train_ratio=1.0,
        generation_probability=1.0,
        context=CONTEXT_LARGE_ABSTRACTIONS,
    ):
        if context == CONTEXT_LARGE_ABSTRACTIONS:
            generation_probability = 1.0
            possible_n_feet = [2, 3, 4]
            possible_feet_heights = [MEDIUM * 4]

        else:
            possible_n_feet = [2, 3, 4]
            possible_feet_heights = [SMALL, MEDIUM * 2, MEDIUM * 4]

        stimuli_strokes, stimuli_strings, stroke_dicts = [], [], []
        # Draw stacked bookshelves with no legs.
        for n_drawers in range(2, int(total_drawers) + 1):
            for (
                drawer_strokes,
                drawer_strings,
                drawer_synthetic_dict,
                enclosure_min_x,
                enclosure_max_x,
                enclosure_min_y,
                enclosure_max_y,
            ) in self._generate_drawers_strings_iterator(
                n_drawers=n_drawers,
                generation_probability=generation_probability,
                context=context,
            ):
                if drawer_strokes:
                    stimuli_strokes += drawer_strokes
                    stimuli_strings.append(drawer_strings)
                    stroke_dicts.append(drawer_synthetic_dict)
        # Draw short drawers with long legs.
        max_short_drawers = 2
        for n_drawers in range(1, max_short_drawers + 1):
            base_heights_and_widths = [
                (SMALL * 3, MEDIUM * 9),
            ]
            for (
                enclosure_strokes,
                enclosure_stroke_strings,
                enclosure_synthetic_dict,
                enclosure_min_x,
                enclosure_max_x,
                enclosure_min_y,
                enclosure_max_y,
            ) in self._generate_drawers_strings_iterator(
                n_drawers=n_drawers,
                base_heights_and_widths=base_heights_and_widths,
                stack_float_locations=FLOAT_TOP,
                generation_probability=generation_probability,
                context=context,
            ):
                if enclosure_strokes:
                    for n_feet in possible_n_feet:
                        for (
                            feet_strokes,
                            feet_string,
                            feet_synthetic_dict,
                        ) in self._generate_feet_strings_iterator(
                            n_feet=n_feet,
                            min_x=enclosure_min_x,
                            max_x=enclosure_max_x,
                            min_y=enclosure_min_y,
                            max_y=enclosure_max_y,
                            feet_heights=possible_feet_heights,
                            generation_probability=generation_probability,
                            context=context,
                        ):
                            drawer_strokes = [enclosure_strokes[0] + feet_strokes[0]]
                            stimuli_strokes += drawer_strokes
                            drawer_string = connect_strokes(
                                [enclosure_stroke_strings, feet_string]
                            )
                            stimuli_strings.append(drawer_string)

                            synthetic_dict = copy.deepcopy(SYNTHETIC_DICT)
                            for k in enclosure_synthetic_dict:
                                synthetic_dict[k] += enclosure_synthetic_dict[k]
                            for k in feet_synthetic_dict:
                                synthetic_dict[k] += enclosure_synthetic_dict[k]
                            stroke_dicts.append(synthetic_dict)

        # Shuffle before returning.
        stimuli_data = list(zip(stimuli_strokes, stimuli_strings, stroke_dicts))
        random.shuffle(stimuli_data)
        stimuli_strokes, stimuli_strings, stroke_dicts = zip(*stimuli_data)

        return random_sample_ratio_ordered_array(
            stimuli_strokes,
            train_ratio,
            strings_array=list(zip(stimuli_strings, stroke_dicts)),
        )

    def _generate_lounges_stimuli_strings(
        self,
        train_ratio=1.0,
        generation_probability=1.0,
        context=CONTEXT_LARGE_ABSTRACTIONS,
    ):
        if context == CONTEXT_LARGE_ABSTRACTIONS:
            generation_probability = 1.0
            possible_base_heights_and_widths = [
                (SMALL * 3, MEDIUM * 9),
            ]
            all_seat_back_primitives = [
                [CIRCLE, CIRCLE, ([], "empt")],
            ]
            possible_n_feet = [2, 4]
            possible_feet_heights = [SMALL, MEDIUM * 2]

        else:
            generation_probability = 1.0
            possible_base_heights_and_widths = [
                (SMALL * 3, MEDIUM * 9),
            ]
            all_seat_back_primitives = [
                [CIRCLE, CIRCLE, ([], "empt")],
                [RECTANGLE, CIRCLE, ([], "empt"),],
            ]
            possible_n_feet = [2, 4]
            possible_feet_heights = [SMALL, MEDIUM * 2]

        # Generates lounges containing a large base and one or more rectangular pillows on top. Lounges may or may not have an inset drawer.
        # Grab the drawer stack enclosure and add pillows, etc.
        stimuli_strokes, stimuli_strings, stroke_dicts = [], [], []
        # Draw short drawers with long legs.
        for (
            enclosure_strokes,
            enclosure_stroke_strings,
            enclosure_synthetic_dict,
            enclosure_min_x,
            enclosure_max_x,
            enclosure_min_y,
            enclosure_max_y,
        ) in self._generate_drawers_strings_iterator(
            n_drawers=1,
            base_heights_and_widths=possible_base_heights_and_widths,
            stack_float_locations=FLOAT_BOTTOM,
            generation_probability=1.0,
            context=context,
        ):
            enclosure_width = enclosure_max_x - enclosure_min_x
            if enclosure_strokes:
                # Now add pillows.

                for seat_back_primitives in all_seat_back_primitives:
                    for base_height in [MEDIUM * 2]:
                        n_segments = len(seat_back_primitives)
                        shape_heights = [base_height] * n_segments

                        def get_width(shape, base_height):
                            if type(shape) == tuple:
                                return 0
                            elif shape == RECTANGLE:
                                return base_height * 0.5
                            else:
                                return base_height

                        shape_widths = [
                            get_width(shape, base_height)
                            for shape in seat_back_primitives
                        ]

                        seat_spacer_width = enclosure_width - np.sum(shape_widths)

                        shape_widths = [
                            w if w > 0 else seat_spacer_width for w in shape_widths
                        ]

                        (
                            seat_back_strokes,
                            seat_back_strokes_string,
                            seat_back_synthetic_dict,
                            _,
                            _,
                            _,
                            _,
                        ) = self._generate_basic_n_segment_bases_string(
                            primitives=seat_back_primitives,
                            heights=shape_heights,
                            widths=shape_widths,
                            float_locations=[FLOAT_TOP for x in range(n_segments)],
                            right_margins=[0 for x in range(n_segments)],
                        )

                        for n_feet in possible_n_feet:
                            for (
                                feet_strokes,
                                feet_string,
                                feet_synthetic_dict,
                            ) in self._generate_feet_strings_iterator(
                                n_feet=n_feet,
                                min_x=enclosure_min_x,
                                max_x=enclosure_max_x,
                                min_y=enclosure_min_y,
                                max_y=enclosure_max_y,
                                feet_heights=possible_feet_heights,
                                generation_probability=1.0,
                            ):
                                feet_strokes, feet_string = T_string(
                                    feet_strokes, feet_string, y=float(enclosure_min_y)
                                )
                                drawer_strokes = [
                                    seat_back_strokes[0]
                                    + enclosure_strokes[0]
                                    + feet_strokes[0]
                                ]
                                drawer_string = connect_strokes(
                                    [
                                        seat_back_strokes_string,
                                        enclosure_stroke_strings,
                                        feet_string,
                                    ]
                                )
                                drawer_synthetic_dict = copy.deepcopy(SYNTHETIC_DICT)
                                for k in seat_back_synthetic_dict:
                                    drawer_synthetic_dict[
                                        k
                                    ] += seat_back_synthetic_dict[k]
                                for k in enclosure_synthetic_dict:
                                    drawer_synthetic_dict[
                                        k
                                    ] += enclosure_synthetic_dict[k]
                                for k in feet_synthetic_dict:
                                    drawer_synthetic_dict[k] += feet_synthetic_dict[k]
                                if random.uniform(0, 1) > generation_probability:
                                    continue

                                stimuli_strokes += drawer_strokes
                                stimuli_strings.append(drawer_string)
                                stroke_dicts.append(drawer_synthetic_dict)

        # Shuffle before returning.
        stimuli_data = list(zip(stimuli_strokes, stimuli_strings, stroke_dicts))

        random.shuffle(stimuli_data)
        stimuli_strokes, stimuli_strings, stroke_dicts = zip(*stimuli_data)

        return random_sample_ratio_ordered_array(
            stimuli_strokes,
            train_ratio,
            strings_array=list(zip(stimuli_strings, stroke_dicts)),
        )

    def _generate_seat_drawers_stimuli_strings(
        self,
        train_ratio=1.0,
        generation_probability=1.0,
        context=CONTEXT_LARGE_ABSTRACTIONS,
    ):

        if context == CONTEXT_LARGE_ABSTRACTIONS:
            generation_probability = 1.0
            possible_base_heights_and_widths = [
                (SMALL * 3, MEDIUM * 9),
            ]
            possible_feet_heights = [SMALL, MEDIUM * 2]

        else:
            possible_base_heights_and_widths = [
                (SMALL * 2, SMALL * 5),
                (SMALL * 4, SMALL * 8),
            ]
            possible_feet_heights = [SMALL, MEDIUM * 2]
        # Generates lounges containing a large base and one or more rectangular pillows on top. Lounges may or may not have an inset drawer.
        # Grab the drawer stack enclosure and add pillows, etc.
        stimuli_strokes, stimuli_strings, stroke_dicts = [], [], []
        # Draw short drawers with long legs.

        for (
            enclosure_strokes,
            enclosure_strokes_strings,
            enclosure_synthetic_dict,
            enclosure_min_x,
            enclosure_max_x,
            enclosure_min_y,
            enclosure_max_y,
        ) in self._generate_drawers_strings_iterator(
            n_drawers=1,
            base_heights_and_widths=possible_base_heights_and_widths,
            stack_float_locations=FLOAT_TOP,
            generation_probability=1.0,
            context=context,
        ):
            enclosure_width = enclosure_max_x - enclosure_min_x
            # Shift it to one side.
            for shifted_location in [enclosure_width * 0.5, -enclosure_width * 0.5]:
                shifted_enclosure_strokes, shifted_enclosure_string = T_string(
                    enclosure_strokes, enclosure_strokes_strings, x=shifted_location
                )

                # Generate a seat base.
                seat_base_height = SMALL
                (
                    seat_strokes,
                    seat_strokes_string,
                    seat_strokes_dict,
                    seat_min_x,
                    seat_max_x,
                    seat_min_y,
                    seat_max_y,
                ) = self._generate_basic_n_segment_bases_string(
                    primitives=[RECTANGLE],
                    heights=[seat_base_height],
                    widths=[2 * enclosure_width],
                    float_locations=[FLOAT_BOTTOM],
                    right_margins=[0],
                )

                # Add feet.
                for n_feet in [2, 3, 4]:
                    for (
                        feet_strokes,
                        feet_string,
                        feet_synthetic_dict,
                    ) in self._generate_feet_strings_iterator(
                        n_feet=n_feet,
                        min_x=seat_min_x,
                        max_x=seat_max_x,
                        min_y=seat_min_y,
                        max_y=seat_max_y,
                        feet_heights=possible_feet_heights,
                        generation_probability=1.0,
                        context=context,
                    ):
                        feet_strokes, feet_string = T_string(
                            feet_strokes, feet_string, y=float(seat_min_y)
                        )
                        drawer_strokes = [
                            seat_strokes[0]
                            + shifted_enclosure_strokes[0]
                            + feet_strokes[0]
                        ]
                        drawer_string = connect_strokes(
                            [
                                seat_strokes_string,
                                shifted_enclosure_string,
                                feet_string,
                            ]
                        )
                        drawer_synthetic_dict = copy.deepcopy(SYNTHETIC_DICT)
                        for k in seat_strokes_dict:
                            drawer_synthetic_dict[k] += seat_strokes_dict[k]
                        for k in enclosure_synthetic_dict:
                            drawer_synthetic_dict[k] += enclosure_synthetic_dict[k]
                        for k in feet_synthetic_dict:
                            drawer_synthetic_dict[k] += feet_synthetic_dict[k]
                        if random.uniform(0, 1) > generation_probability:
                            continue

                        stimuli_strokes += drawer_strokes
                        stimuli_strings.append(drawer_string)
                        stroke_dicts.append(drawer_synthetic_dict)

        # Shuffle before returning.
        stimuli_data = list(zip(stimuli_strokes, stimuli_strings, stroke_dicts))
        random.shuffle(stimuli_data)
        stimuli_strokes, stimuli_strings, stroke_dicts = zip(*stimuli_data)

        return random_sample_ratio_ordered_array(
            stimuli_strokes,
            train_ratio,
            strings_array=list(zip(stimuli_strings, stroke_dicts)),
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
            self._generate_stacked_drawers_stimuli_strings,
            self._generate_lounges_stimuli_strings,
            self._generate_seat_drawers_stimuli_strings,
        ]:
            (
                generator_train,
                generator_test,
                generator_train_strings,
                generator_test_strings,
            ) = generator_fn(train_ratio=train_ratio, context=context)
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
