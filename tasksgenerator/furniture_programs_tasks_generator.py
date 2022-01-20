"""
furniture_programs_tasks_generator.py | Author: Catherine Wong.

Defines TaskGenerators that produce tasks for furniture drawings.

Threads program string generating logic through the generation.
"""
from inspect import stack
import math, random, itertools, copy
from primitives.gadgets_primitives import *
from dreamcoder.grammar import Grammar

from tasksgenerator.tasks_generator import (
    AbstractTasksGenerator,
    ManualCurriculumTasksGenerator,
    TasksGeneratorRegistry,
    TaskCurriculum,
    DrawingTask,
    random_sample_ratio_ordered_array,
)
from tasksgenerator.bases_parts_tasks_generator import *
from tasksgenerator.wheels_programs_tasks_generator import *

from tasksgenerator.s12_s13_tasks_generator import RANDOM_SEED


@TasksGeneratorRegistry.register
class FurnitureProgramsTasksGenerator(AbstractBasesAndPartsProgramsTasksGenerator):
    name = "furniture_programs"

    def _generate_drawer_pulls_strings_iterator(
        self,
        min_x,
        max_x,
        n_drawer_pulls,
        float_location=FLOAT_CENTER,
        drawer_pull_scale=str(SCALE_UNIT),
    ):
        wheels_generator = WheelsProgramsTasksGenerator()

        base_min_size = MEDIUM * MEDIUM
        for outer_shapes in [
            [cc_string],
            [cc_string, cc_string],
            [r_string],
            [octagon_string],
            [],
        ]:
            for outer_shapes_min_size in [base_min_size]:
                for inner_shapes in [[c_string], [r_string]]:
                    for inner_shapes_max_size in [base_min_size * THREE_QUARTER_SCALE]:
                        for n_decorators in [0]:
                            if outer_shapes + inner_shapes == [r_string, r_string]:
                                continue
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
    ):
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
            for n_drawer_pulls in [0, 2]:
                for (
                    drawer_pull_strokes,
                    drawer_pull_strings,
                    drawer_pull_synthetic_dict,
                    drawer_pull_strokes_min_x,
                    drawer_pull_strokes_max_x,
                    drawer_pull_strokes_min_y,
                    drawer_pull_strokes_max_y,
                ) in self._generate_drawer_pulls_strings_iterator(
                    min_x=base_min_x + (base_width * QUARTER_SCALE),
                    max_x=base_max_x - (base_width * QUARTER_SCALE),
                    n_drawer_pulls=n_drawer_pulls,
                    float_location=FLOAT_CENTER,
                    drawer_pull_scale=SCALE_UNIT,
                ):
                    drawer_spacing = base_height * QUARTER_SCALE
                    if peval(drawer_pull_strokes_max_y) >= (
                        base_max_y - (drawer_spacing)
                    ) or peval(drawer_pull_strokes_max_x) >= (
                        base_max_x - (drawer_spacing)
                    ):

                        continue

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

                    # TODO: Make the drawer synthetic dic.
                    drawer_synthetic_dict = base_synthetic_dict

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

                    if random.uniform(0, 1) > generation_probability:
                        continue

                    yield (
                        drawer_strokes,
                        drawer_stroke_string,
                        enclosure_min_x,
                        enclosure_max_x,
                        enclosure_min_y,
                        enclosure_max_y,
                    )

    def _generate_feet_iterator(
        self,
        n_feet,
        min_x,
        max_x,
        min_y,
        max_y,
        feet_heights=[SMALL, MEDIUM * 2, MEDIUM * 4],
        generation_probability=1.0,
    ):
        short_v_line = T_string(
            short_l_string[0], short_l_string[1], theta=STR_VERTICAL
        )
        # Adds a row of feet to the object. These can be short or tall.
        for foot_primitive in [RECTANGLE, LINE]:
            for foot_height in feet_heights:
                if foot_primitive == RECTANGLE:
                    foot_width = SMALL

                    foot = scaled_rectangle_string(w=foot_width, h=foot_height)

                    if n_feet > 2:
                        continue
                else:
                    foot_width = 0
                    foot = T_string(short_v_line[0], short_v_line[1], s=foot_height)

                    foot_synthetic_dict = copy.deepcopy(SYNTHETIC_DICT)
                (
                    feet_strokes,
                    feet_strokes_string,
                    feet_strokes_synthetic_dict,
                    feet_strokes_min_x,
                    feet_strokes_max_x,
                    feet_strokes_min_y,
                    feet_strokes_max_y,
                ) = self._generate_n_objects_on_grid_x_y_limits(
                    object=foot[0],
                    object_string=foot[1],
                    object_center=(0, 0),
                    object_height=foot_height,
                    object_width=foot_width if foot_width > 0 else 1,
                    min_x=min_x + (foot_width * 0.5),
                    max_x=max_x - (foot_width * 0.5),
                    min_y=min_y,
                    max_y=min_y,
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

    def _generate_stacked_drawers_strings_stimuli(
        self, total_drawers=4, train_ratio=1.0, generation_probability=0.45
    ):
        stimuli_strokes, stimuli_strings = [], []
        # Draw stacked bookshelves with no legs.
        for n_drawers in range(2, total_drawers + 1):
            for (
                drawer_strokes,
                drawer_strings,
                drawer_synthetic_dict,
                enclosure_min_x,
                enclosure_max_x,
                enclosure_min_y,
                enclosure_max_y,
            ) in self._generate_drawers_iterator(
                n_drawers=n_drawers,
                generation_probability=generation_probability,
            ):
                if drawer_strokes:
                    stimuli_strokes += drawer_strokes
                    stimuli_strings.append(drawer_strings)

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
            ) in self._generate_drawers_iterator(
                n_drawers=n_drawers,
                base_heights_and_widths=base_heights_and_widths,
                stack_float_locations=FLOAT_TOP,
                generation_probability=generation_probability,
            ):
                if drawer_strokes:
                    for n_feet in [2, 3, 4]:
                        for (
                            feet_strokes,
                            feet_string,
                            feet_synthetic_dict,
                        ) in self._generate_feet_iterator(
                            n_feet=n_feet,
                            min_x=enclosure_min_x,
                            max_x=enclosure_max_x,
                            min_y=enclosure_min_y,
                            max_y=enclosure_max_y,
                            feet_heights=[SMALL, MEDIUM * 2, MEDIUM * 4],
                            generation_probability=generation_probability,
                        ):
                            drawer_strokes = [enclosure_strokes[0] + feet_strokes[0]]
                            stimuli_strokes += drawer_strokes
                            drawer_string = connect_strokes(
                                [enclosure_stroke_strings, feet_string]
                            )
                            stimuli_strings.append(drawer_strings)

        # Shuffle before returning.
        stimuli_data = zip(stimuli_strokes, stimuli_strings)
        random.shuffle(stimuli_data)
        stimuli_strokes, stimuli_strings = zip(*stimuli_data)
        return random_sample_ratio_ordered_array(
            stimuli_strokes, train_ratio, strings_array=stimuli_strings
        )
