"""
dial_programs_tasks_generator.py | Author: Catherine Wong.
Defines TasksGenerators that produce gadgets tasks with dials on them.

Threads program string generating logic through the generation.
"""
import math, random, itertools, copy
from primitives.gadgets_primitives import *
from dreamcoder.grammar import Grammar
from primitives.object_primitives import rectangle
from tasksgenerator.dial_tasks_generator import (
    ANTENNA_DIAL_SCALE_DOWN,
    DIAL_SCALE_UNIT,
    MAX_ANTENNA_WIRES,
)
from tasksgenerator.tasks_generator import (
    AbstractTasksGenerator,
    ManualCurriculumTasksGenerator,
    TasksGeneratorRegistry,
    TaskCurriculum,
    DrawingTask,
    random_sample_ratio_ordered_array,
)
from tasksgenerator.bases_parts_tasks_generator import *

from tasksgenerator.s12_s13_tasks_generator import RANDOM_SEED


@TasksGeneratorRegistry.register
class DialProgramsTasksGenerator(AbstractTasksGenerator):
    name = "dial_programs"

    def __init__(self):
        super().__init__(grammar=constants + some_none + objects + transformations)

    def _generate_base_with_dials(
        self,
        n_dials,
        n_circles,
        circle_size,
        dial_size,
        dial_angle,
        n_dial_rows=1,
        spacing=f"(+ {LARGE} {SCALE_UNIT})",
        base_width=LARGE,
        base_height=LARGE,
        base_columns=None,
        n_base_tiers=1,
        centered=False,
        max_dials=3,
        base_end_filials=False,
        shape_specification=None,
        no_base=False,
    ):
        strokes, stroke_strings = [], []
        if not no_base:
            base, base_string, base_width, base_height = self._generate_bases_string(
                base_width=base_width,
                base_height=base_height,
                base_columns=base_columns,
                max_rows=n_dial_rows,
                n_tiers=str(n_base_tiers),
                base_end_filials=base_end_filials,
            )
            strokes += base
            stroke_strings.append(base_string)

        if n_dials > 0:
            # Generate the base dial.
            base_dial, base_dial_string = self._generate_nested_circle_dials_string(
                n_circles=str(n_circles),
                circle_size=circle_size,
                dial_size=dial_size,
                dial_angle=dial_angle,
                shape_specification=shape_specification,
            )
            # Generate the row of dials.
            row_of_dials, row_of_dials_string = self._generate_rows_of_dials(
                n_dial_rows=str(n_dial_rows),
                n_dials=str(n_dials),
                x_spacing=spacing,
                dial_shape=base_dial,
                dial_shape_string=base_dial_string,
                centered=centered,
            )

            # Offset them with respect to the base.
            y_offset = f"(- 0 (* 0.5 (* (- {n_dial_rows} 1) {spacing})))"

            if centered:
                x_offset = f"(- 0 (* 0.5 (* (- {max_dials} 1) {spacing})))"
            else:
                x_offset = f"(+ 0 (* 0.5 (* {max_dials} {spacing})))"
            row_of_dials, row_of_dials_string = T_string(
                row_of_dials, row_of_dials_string, x=x_offset, y=y_offset
            )

            strokes += row_of_dials
            stroke_strings.append(row_of_dials_string)

        return strokes, connect_strokes(stroke_strings), base_width, base_height

    def _generate_rows_of_dials(
        self,
        n_dial_rows=str(1),
        n_dials=str(1),
        x_spacing=f"(+ {LARGE} {SCALE_UNIT})",
        dial_shape=None,
        dial_shape_string=None,
        centered=False,
    ):
        # Generate a row of dials.
        if centered:
            _, x_shift = M_string(x=x_spacing)
        else:
            _, x_shift = M_string(x=f"(- 0 {x_spacing})")

        _, y_shift = M_string(y=f"{x_spacing}")
        row_of_dials_string = f"(repeat {dial_shape_string} {n_dials} {x_shift})"
        row_of_rows_string = f"(repeat {row_of_dials_string} {n_dial_rows} {y_shift})"
        return peval(row_of_rows_string), row_of_rows_string

    def _generate_nested_circle_dials_string(
        self,
        n_circles=str(1),
        circle_size=str(SMALL),
        dial_size=str(SMALL),
        dial_angle=STR_VERTICAL,
        shape_specification=None,
    ):
        """
        Generates primitive parts for circular dials: parameterized by
        number of dials to draw left to right, n-nested circles, radius of inner-most circle,
        length of the dial hand (or NONE), and angle of the dial hand.
        Shape specification: array of shapes to draw the dial from.

        :ret: dial_strokes, dial_strokes_string
        """
        strokes, stroke_strings = [], []
        if circle_size != STR_ZERO and not shape_specification:
            # Draw nested circles.
            scale_factor = f"(+ {circle_size} {SCALE_UNIT})"
            circle_strokes, circle_strings = nested_scaling_string(
                c_string[-1], n_circles, scale_factor
            )
            strokes += circle_strokes
            stroke_strings.append(circle_strings)
        # Shape specification - we don't really do this one correctly.
        if shape_specification:
            for shape_idx, (shape, shape_string) in enumerate(shape_specification):
                scale_factor = f"(+ {circle_size} (* {shape_idx} {SCALE_UNIT}))"
                object_stroke, object_string = T_string(
                    shape, shape_string, s=scale_factor
                )
                strokes += object_stroke
                stroke_strings.append(object_string)

        # Dials.
        if dial_size != STR_ZERO:
            dial_hand, dial_hand_string = T_string(
                short_l_string[0], short_l_string[-1], theta=dial_angle, s=dial_size
            )
            dial_x = f"(* {dial_size} (* {SCALE_UNIT} (cos {dial_angle})))"
            dial_y = f"(* {dial_size} (* {SCALE_UNIT} (sin {dial_angle})))"
            dial_hand, dial_hand_string = T_string(
                dial_hand, dial_hand_string, x=dial_x, y=dial_y
            )
            strokes += dial_hand
            stroke_strings.append(dial_hand_string)

        return [strokes], connect_strokes(stroke_strings)

    def _generate_bases_string(
        self,
        base_columns=str(3),
        max_rows=str(1),
        base_width=str(LARGE),
        base_height=str(LARGE),
        n_tiers=str(1),
        base_center=str(BASE_CENTER),
        tier_scaling=str(SCALE_UNIT),
        base_end_filials=False,
    ):
        """
        Generates bases and a string program that can be evaluated to generate the resulting base.
        See dial_tasks_generator.generate_bases for the original implementation.

        :ret: base, base_string, base_width, base_width_string, base_height, base_height_string.
        """
        strokes, stroke_strings = [], []
        margins = f"(* 4 {tier_scaling})"
        total_base_height = "0"
        total_base_width = "0"
        tier_offset = "0"

        # Place tiers. Note that we don't currently express the looped computation in a loop.
        first_tier_width, first_tier_height = None, None
        for tier_idx in range(peval(n_tiers)):
            tier_width = (
                f"(+ (* {base_columns} (+ {base_width} {SCALE_UNIT})) {margins})"
            )
            tier_width = f"(- {tier_width} (* {tier_idx} {margins}))"

            tier_height = f"(+ (* {max_rows} (+ {base_height} {SCALE_UNIT})) {margins})"
            tier_height = f"(* {tier_height} (^ {tier_scaling} {tier_idx}))"

            # Hacky: only allows two tiers
            if tier_idx > 0:
                tier_offset = f"(* {SCALE_UNIT} (+ {tier_height} {first_tier_height}))"

            tier_y = f"(+ (* 0.5 {base_center}) {tier_offset})"
            tier_rect, tier_rect_string = scaled_rectangle_string(
                tier_width, tier_height
            )
            tier_rect, tier_rect_string = T_string(
                tier_rect, tier_rect_string, y=tier_y
            )
            strokes += tier_rect
            stroke_strings.append(tier_rect_string)

            total_base_width = f"(max {total_base_width} {tier_width})"

            if tier_idx == 0:
                first_tier_width, first_tier_height = tier_width, tier_height
                total_base_height = f"(+ (* 0.5 {tier_height}) {total_base_height})"
            else:
                total_base_height = f"(+ {tier_height} {total_base_height})"

        # Add decorative finials.
        if base_end_filials:
            filial_width = f"(* 2 {SCALE_UNIT})"
            filial_height = f"(* {first_tier_height} {SCALE_UNIT})"
            filial_rect, filial_rect_string = scaled_rectangle_string(
                w=filial_width, h=filial_height
            )
            x_shift = f"(* 0.5 (+ {first_tier_width} {filial_width}))"
            first_filial, first_filial_string = T_string(
                filial_rect, filial_rect_string, x=x_shift
            )

            strokes += first_filial
            stroke_strings.append(first_filial_string)

            x_shift = f"(- 0 {x_shift})"
            scd_filial, scd_filial_string = T_string(
                filial_rect, filial_rect_string, x=x_shift
            )
            strokes += scd_filial
            stroke_strings.append(scd_filial_string)

            total_base_width = f"(+ {total_base_width} (* 2 {filial_width}))"

        return (
            strokes,
            connect_strokes(stroke_strings),
            total_base_width,
            total_base_height,
        )

    def _generate_stacked_antenna_strings(
        self, n_wires=str(3), antenna_size=str(SMALL), scale_wires=True, end_shape=None
    ):
        """
        Generates stacked antenna. See SimpleAntennaTasksGenerator for original implementation.
        """
        strokes, stroke_strings = [], []

        antenna_base_height = "3"
        long_vl_string = T_string(
            l_string[0],
            l_string[-1],
            theta=STR_VERTICAL,
            s=antenna_base_height,
            y="(- 0 2)",
        )

        if antenna_size != STR_ZERO:
            base_line, base_line_string = T_string(
                long_vl_string[0], long_vl_string[-1], s=antenna_size, x=STR_ZERO
            )
            base_line, base_line_string = T_string(
                base_line, base_line_string, x=STR_ZERO
            )

            strokes += base_line
            stroke_strings.append(base_line_string)

            for a_idx in range(peval(n_wires)):
                antenna_length = antenna_size
                antenna_height = f"(* 0.5 {antenna_size})"
                if scale_wires:
                    s = f"(- (* {antenna_length} 2) {a_idx})"
                else:
                    s = f"(* {antenna_length} 2)"
                antenna_wire, antenna_wire_string = T_string(
                    short_l_string[0], short_l_string[-1], s=s
                )
                antenna_wire, antenna_wire_string = T_string(
                    antenna_wire,
                    antenna_wire_string,
                    y=f"(- (* {antenna_height} 2) {a_idx})",
                )
                strokes += antenna_wire
                stroke_strings.append(antenna_wire_string)

        if end_shape:
            # Add end finials
            x_shift = f"(+ {SCALE_UNIT} {antenna_length})"
            finial, finial_string = T_string(
                end_shape[0], end_shape[1], x=f"(- 0 {x_shift})", y=antenna_height
            )
            finial, finial_string = T_string(finial, finial_string, y=antenna_height)
            strokes += finial
            stroke_strings.append(finial_string)

            finial, finial_string = T_string(
                end_shape[0], end_shape[1], x=x_shift, y=antenna_height
            )
            finial, finial_string = T_string(finial, finial_string, y=antenna_height)
            strokes += finial
            stroke_strings.append(finial_string)
        return [strokes], connect_strokes(stroke_strings)

    def _add_antenna_to_stimuli(
        self,
        stimuli,
        stimuli_string,
        base_width,
        base_height,
        antenna_end_shapes=[None, c_string, r_string],
        add_double_antenna=False,
        add_side_antenna=False,
        generation_probability=1.0,
        antenna_generation_probability=0.25,
    ):
        if random.uniform(0, 1) > generation_probability:
            return None
        generation_probability *= antenna_generation_probability

        strokes, stroke_strings = [], []
        antenna_strokes, antenna_strings = [], []
        for n_wires in ["1", "2", "3"]:
            for scale_wires in [True, False]:
                for end_shape in antenna_end_shapes:
                    stroke, stroke_string = self._generate_stacked_antenna_strings(
                        n_wires=n_wires, scale_wires=scale_wires, end_shape=end_shape
                    )
                    antenna_strokes += stroke
                    antenna_strings.append(stroke_string)

        sideways_antenna_strokes, sideways_antenna_strings = [], []
        for n_wires in ["2", "3"]:
            stroke, stroke_string = self._generate_stacked_antenna_strings(
                n_wires=n_wires, scale_wires=False, end_shape=None
            )
            sideways_antenna_strokes += stroke
            sideways_antenna_strings.append(stroke_string)

        for base_antenna_primitive, base_antenna_string in zip(
            antenna_strokes, antenna_strings
        ):
            y_shift = f"(+ {LARGE} {base_height})"
            antenna_primitive, antenna_primitive_string = T_string(
                base_antenna_primitive, base_antenna_string, y=y_shift
            )
            if random.uniform(0, 1) < generation_probability:
                strokes.append(stimuli + antenna_primitive)
                stroke_strings.append(
                    connect_strokes([stimuli_string, antenna_primitive_string])
                )

            if random.uniform(0, 1) < generation_probability:
                if peval(base_width) > peval(base_height) and add_double_antenna:
                    x_shift = f"(* {base_width} 0.25)"
                    finial_right = T_string(
                        base_antenna_primitive,
                        base_antenna_string,
                        y=y_shift,
                        x=x_shift,
                    )
                    finial_left = T_string(
                        base_antenna_primitive,
                        base_antenna_string,
                        y=y_shift,
                        x=f"(- 0 {x_shift})",
                    )
                    strokes.append(stimuli + finial_right[0] + finial_left[0])
                    stroke_strings.append(
                        connect_strokes(
                            [stimuli_string, finial_right[-1], finial_left[-1]]
                        )
                    )
            if random.uniform(0, 1) < generation_probability:
                if add_side_antenna:
                    for (base_sideways, base_sideways_string) in zip(
                        sideways_antenna_strokes, sideways_antenna_strings
                    ):
                        sideways_antenna = T_string(
                            base_sideways,
                            base_sideways_string,
                            theta=f"(- 0 {STR_VERTICAL})",
                        )
                        sideways_antenna = T_string(
                            sideways_antenna[0],
                            sideways_antenna[-1],
                            x=f"(+ {LARGE} (* 0.5 {base_width}))",
                        )
                        strokes.append(
                            stimuli + antenna_primitive + sideways_antenna[0]
                        )
                        stroke_strings.append(
                            connect_strokes(
                                [
                                    stimuli_string,
                                    antenna_primitive_string,
                                    sideways_antenna[-1],
                                ]
                            )
                        )

        if len(strokes) < 1:
            return None
        return strokes, stroke_strings

    def _generate_parts_strings_for_stimuli(
        self,
        max_dials=5,
        train_ratio=1.0,
        spacing=f"(+ {LARGE} {SCALE_UNIT})",
        generation_probability=0.2,
    ):
        """
        Generator function for drawing the individual parts in the domain.
        See dials_task_generator.generate_parts_stimuli for original implementation.
        """
        strokes, stroke_strings = [], []

        # Generate antenna.
        antenna_end_shapes = [None, c_string, r_string]
        for n_wires in ["1", "2", "3"]:
            for scale_wires in [True, False]:
                for end_shape in antenna_end_shapes:
                    (
                        antenna_stimuli,
                        antenna_string,
                    ) = self._generate_stacked_antenna_strings(
                        n_wires=n_wires, scale_wires=scale_wires, end_shape=end_shape
                    )
                    strokes += antenna_stimuli
                    stroke_strings.append(antenna_string)

        # Generate dials.
        for total_dials in [1, max_dials + 1]:
            # Varying bases for the single small dials.
            for base_columns in [1, max_dials + 1]:
                for base_heights in [1, max_dials]:
                    for rows in [1, 2]:
                        if base_heights < rows:
                            continue
                        base_height = base_heights * LARGE
                        if rows > 1:  # We already take care of sizing the rows.
                            base_height = LARGE
                        if base_columns < total_dials:
                            continue

                        centered = total_dials % 2 != 0

                        # Small and large dials with the lever sticking out
                        for dial_size in [SMALL, LARGE]:
                            for dial_angle in [STR_VERTICAL, STR_RIGHT]:
                                for shape_specification in [
                                    None,
                                    [c_string, r_string],
                                    [c_string, c_string],
                                ]:
                                    if (
                                        dial_size == LARGE
                                        and dial_angle == STR_VERTICAL
                                    ):
                                        continue

                                    (
                                        stimuli,
                                        stimuli_string,
                                        total_base_width,
                                        total_base_height,
                                    ) = self._generate_base_with_dials(
                                        max_dials=total_dials,
                                        n_dials=total_dials,
                                        n_circles=1,
                                        dial_size=str(dial_size),
                                        circle_size=str(dial_size),
                                        dial_angle=dial_angle,
                                        base_columns=str(base_columns),
                                        base_height=str(base_height),
                                        centered=centered,
                                        n_dial_rows=rows,
                                        n_base_tiers=STR_ZERO,
                                        spacing=spacing,
                                        base_end_filials=False,
                                        shape_specification=shape_specification,
                                        no_base=True,
                                    )
                                    if total_dials > 1 or rows > 1:
                                        if (
                                            random.uniform(0, 1)
                                            > generation_probability
                                        ):
                                            continue

                                    strokes.append(stimuli)
                                    stroke_strings.append(stimuli_string)

        # Randomly sample them.
        return random_sample_ratio_ordered_array(strokes, train_ratio, stroke_strings)

    def _generate_strokes_strings_for_stimuli(
        self,
        train_ratio=1.0,
        max_dials=5,
        spacing=f"(+ {LARGE} {SCALE_UNIT})",
        generation_probability=0.14,  # Probabilistically generate from space
    ):
        """
        Main generator function. Returns strokes and strings for stimuli.

        See dials_task_generator.generate_strokes_for_stimuli for original implementation.
        """
        strokes, stroke_strings = [], []

        MAX_BASE_COLUMNS_FOR_ANTENNA = 3

        # Loop over the full cross product of dials / antenna / stimuli / tiers
        total_dials_range = list(range(1, max_dials + 1))
        random.shuffle(total_dials_range)
        for total_dials in total_dials_range:
            total_columns_range = list(range(1, max_dials + 1, 2))
            random.shuffle(total_columns_range)

            # Varying bases for the single small dials.
            for base_columns in total_columns_range:
                for base_heights in [1, max_dials]:
                    for rows in [1, 2]:
                        for tiers in [1, 2]:
                            for base_end_filials in [True, False]:
                                can_add_tiers = rows <= 1 and base_heights <= 1
                                if tiers > 1 and not can_add_tiers:
                                    continue

                                if base_heights < rows:
                                    continue
                                base_height = base_heights * LARGE
                                if rows > 1:  # We already take care of sizing the rows.
                                    base_height = LARGE
                                if base_columns < total_dials:
                                    continue

                                centered = total_dials % 2 != 0

                                add_side_antenna = (
                                    base_columns < MAX_BASE_COLUMNS_FOR_ANTENNA
                                )
                                add_double_antenna = (
                                    base_columns > MAX_BASE_COLUMNS_FOR_ANTENNA
                                )

                                # Blank bases with antenna.
                                if (
                                    can_add_tiers
                                    and rows == 1
                                    and tiers == 1
                                    and total_dials == 1
                                ):
                                    (
                                        stimuli,
                                        stimuli_string,
                                        total_base_width,
                                        total_base_height,
                                    ) = self._generate_base_with_dials(
                                        n_dials=0,
                                        n_circles=1,
                                        dial_size=STR_ZERO,
                                        circle_size=STR_ZERO,
                                        dial_angle=STR_ZERO,
                                        base_columns=base_columns,
                                        base_height=base_height,
                                        centered=centered,
                                        n_dial_rows=rows,
                                    )
                                    antenna_stimuli = self._add_antenna_to_stimuli(
                                        stimuli,
                                        stimuli_string,
                                        base_width=total_base_width,
                                        base_height=total_base_height,
                                        generation_probability=1.0,
                                        antenna_generation_probability=0.5,
                                    )
                                    if antenna_stimuli is not None:
                                        stim_strokes, stim_strings = antenna_stimuli

                                        strokes += stim_strokes
                                        stroke_strings += stim_strings

                                # Small and large dials with the lever sticking out.
                                for dial_size in [SMALL, LARGE]:
                                    for dial_angle in [STR_VERTICAL, STR_RIGHT]:
                                        for shape_specification in [
                                            None,
                                            [c_string, r_string],
                                            [c_string, c_string],
                                        ]:
                                            if (
                                                dial_size == LARGE
                                                and dial_angle == STR_VERTICAL
                                            ):
                                                continue

                                            (
                                                stimuli,
                                                stimuli_string,
                                                total_base_width,
                                                total_base_height,
                                            ) = self._generate_base_with_dials(
                                                max_dials=total_dials,
                                                n_dials=total_dials,
                                                n_circles=1,
                                                dial_size=str(dial_size),
                                                circle_size=str(dial_size),
                                                dial_angle=dial_angle,
                                                base_columns=str(base_columns),
                                                base_height=str(base_height),
                                                centered=centered,
                                                n_dial_rows=rows,
                                                n_base_tiers=tiers,
                                                spacing=spacing,
                                                base_end_filials=base_end_filials,
                                                shape_specification=shape_specification,
                                            )
                                            if (
                                                random.uniform(0, 1)
                                                < generation_probability
                                            ):
                                                strokes.append(stimuli)
                                                stroke_strings.append(stimuli_string)

                                            add_side_antenna = (
                                                base_columns
                                                < MAX_BASE_COLUMNS_FOR_ANTENNA
                                            )
                                            add_double_antenna = (
                                                base_columns
                                                > MAX_BASE_COLUMNS_FOR_ANTENNA
                                            )

                                            antenna_stimuli = self._add_antenna_to_stimuli(
                                                stimuli,
                                                stimuli_string,
                                                base_width=total_base_width,
                                                base_height=total_base_height,
                                                add_double_antenna=add_double_antenna,
                                                add_side_antenna=add_side_antenna,
                                                generation_probability=generation_probability,
                                            )
                                            if antenna_stimuli is not None:
                                                (
                                                    stim_strokes,
                                                    stim_strings,
                                                ) = antenna_stimuli

                                                strokes += stim_strokes
                                                stroke_strings += stim_strings

        (
            train_parts,
            test_parts,
            train_parts_strings,
            test_parts_strings,
        ) = self._generate_parts_strings_for_stimuli(train_ratio=0.95)

        (
            train_main,
            test_main,
            train_main_strings,
            test_main_strings,
        ) = random_sample_ratio_ordered_array(
            strokes, train_ratio, strings_array=stroke_strings
        )

        return (
            train_parts + train_main,
            test_parts + test_main,
            train_parts_strings + train_main_strings,
            test_parts_strings + test_main_strings,
        )
