"""
dial_programs_tasks_generator.py | Author: Catherine Wong.
Defines TasksGenerators that produce gadgets tasks with dials on them.

Threads program string generating logic through the generation.
"""
import math, random, itertools, copy
from primitives.gadgets_primitives import *
from dreamcoder_programs.grammar import Grammar
from primitives.object_primitives import rectangle
from tasksgenerator.dial_tasks_generator import (
    ANTENNA_DIAL_SCALE_DOWN,
    DIAL_SCALE_UNIT,
    MAX_ANTENNA_WIRES,
)
from tasksgenerator.tasks_generator import *
from tasksgenerator.bases_parts_tasks_generator import *

from tasksgenerator.s12_s13_tasks_generator import RANDOM_SEED


@TasksGeneratorRegistry.register
class DialProgramsTasksGenerator(AbstractTasksGenerator):
    name = "dials_programs"

    def __init__(self):
        super().__init__(
            grammar=constants + math_operations + objects + transformations
        )

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
        synthetic_dict = copy.deepcopy(SYNTHETIC_DICT)
        if not no_base:
            (
                base,
                base_string,
                base_width,
                base_height,
                base_synthetic_dict,
            ) = self._generate_bases_string(
                base_width=base_width,
                base_height=base_height,
                base_columns=base_columns,
                max_rows=n_dial_rows,
                n_tiers=str(n_base_tiers),
                base_end_filials=base_end_filials,
            )
            strokes += base
            stroke_strings.append(base_string)

            # Add the base to the synthetic dict.
            for k in base_synthetic_dict:
                synthetic_dict[k] += base_synthetic_dict[k]

        if n_dials > 0:
            # Generate the base dial.
            (
                base_dial,
                base_dial_string,
                base_dial_dict,
            ) = self._generate_nested_circle_dials_string(
                n_circles=str(n_circles),
                circle_size=circle_size,
                dial_size=dial_size,
                dial_angle=dial_angle,
                shape_specification=shape_specification,
            )
            # Generate the row of dials.
            (
                row_of_dials,
                row_of_dials_string,
                row_dials_dict,
            ) = self._generate_rows_of_dials(
                n_dial_rows=str(n_dial_rows),
                n_dials=str(n_dials),
                x_spacing=spacing,
                dial_shape=base_dial,
                dial_shape_string=base_dial_string,
                centered=centered,
                dial_synthetic_dict=base_dial_dict,
            )

            # Add the row of dials to the synthetic dict
            for k in row_dials_dict:
                synthetic_dict[k] += row_dials_dict[k]

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

        return (
            strokes,
            connect_strokes(stroke_strings),
            base_width,
            base_height,
            synthetic_dict,
        )

    def _generate_rows_of_dials(
        self,
        n_dial_rows=str(1),
        n_dials=str(1),
        x_spacing=f"(+ {LARGE} {SCALE_UNIT})",
        dial_shape=None,
        dial_shape_string=None,
        dial_synthetic_dict=None,
        centered=False,
    ):

        if centered:
            _, x_shift = M_string(x=x_spacing)
        else:
            _, x_shift = M_string(x=f"(- 0 {x_spacing})")

        _, y_shift = M_string(y=f"{x_spacing}")
        row_of_dials_string = f"(repeat {dial_shape_string} {n_dials} {x_shift})"
        row_of_rows_string = f"(repeat {row_of_dials_string} {n_dial_rows} {y_shift})"

        # Add a low-level abstraction for each dial.
        dial_synthetic_dict[LOW_LEVEL] = dial_synthetic_dict[LOW_LEVEL] * int(
            peval(f"(* {n_dials} {n_dial_rows})")
        )
        dial_synthetic_dict[LOW_LEVEL_PARTS] = dial_synthetic_dict[
            LOW_LEVEL_PARTS
        ] * int(peval(f"(* {n_dials} {n_dial_rows})"))

        # Add a mid-level abstraction for the repetition and a parameter.
        dial_synthetic_dict[MID_LEVEL] = ["repeat_x", "repeat_y"] + dial_synthetic_dict[
            MID_LEVEL
        ]
        dial_synthetic_dict[MID_LEVEL_PARTS] = [
            "repeat_x",
            "repeat_y",
        ] + dial_synthetic_dict[MID_LEVEL_PARTS]
        dial_synthetic_dict[MID_LEVEL_PARAMS] = [
            str(peval(n_dials)),
            str(peval(n_dial_rows)),
        ] + dial_synthetic_dict[MID_LEVEL_PARAMS]

        dial_synthetic_dict[HIGH_LEVEL] = ["row_of_dials"]
        dial_synthetic_dict[HIGH_LEVEL_PARTS] = [row_of_rows_string]

        return peval(row_of_rows_string), row_of_rows_string, dial_synthetic_dict

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
        strokes, stroke_strings = (
            [],
            [],
        )

        synthetic_dict = copy.deepcopy(SYNTHETIC_DICT)

        if circle_size != STR_ZERO and not shape_specification:
            # Draw nested circles.
            scale_factor = f"(+ {circle_size} {SCALE_UNIT})"
            circle_strokes, circle_strings = nested_scaling_string(
                c_string[-1], n_circles, scale_factor
            )
            strokes += circle_strokes
            stroke_strings.append(circle_strings)

            # Add a low-level circle for each next.
            shape_abstraction = "base_dial_shape"
            synthetic_dict[LOW_LEVEL] += [shape_abstraction] * int(peval(n_circles))
            synthetic_dict[LOW_LEVEL_PARTS] += [c_string[-1]] * int(peval(n_circles))

            synthetic_dict[LOW_LEVEL_PARAMS].append(str(peval(scale_factor)))

            # Add a mid-level abstraction for just the nested dial.
            # Mid-level abstraction corresponding to the outer shape.
            outer_shape_abstraction = "outer_strokes"
            synthetic_dict[MID_LEVEL].append(outer_shape_abstraction)
            synthetic_dict[MID_LEVEL_PARTS].append(c_string[-1])
            synthetic_dict[MID_LEVEL_PARAMS].append(str(peval(scale_factor)))
            synthetic_dict[MID_LEVEL_PARAMS].append(str(peval(n_circles)))

        # Shape specification - we don't really do this one correctly.
        if shape_specification:
            for shape_idx, (shape, shape_string) in enumerate(shape_specification):
                scale_factor = f"(+ {circle_size} (* {shape_idx} {SCALE_UNIT}))"
                object_stroke, object_string = T_string(
                    shape, shape_string, s=scale_factor
                )
                strokes += object_stroke
                stroke_strings.append(object_string)

                # Low-level: one for each type.
                shape_abstraction = "base_dial_shape"
                synthetic_dict[LOW_LEVEL].append(shape_abstraction)
                synthetic_dict[LOW_LEVEL_PARTS].append(shape_string)
                synthetic_dict[LOW_LEVEL_PARAMS].append(str(peval(scale_factor)))
            # Mid-level: just choose the outer one.
            outer_shape_abstraction = "outer_strokes"
            synthetic_dict[MID_LEVEL].append(outer_shape_abstraction)
            synthetic_dict[MID_LEVEL_PARTS].append(shape_string)
            synthetic_dict[MID_LEVEL_PARAMS].append(
                str(peval(scale_factor))
            )  # Use the last scale factor.

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

            # Add a low abstraction corresponding to a dial direction
            shape_abstraction = "base_dial_hand"
            synthetic_dict[LOW_LEVEL].append(shape_abstraction)
            synthetic_dict[LOW_LEVEL_PARTS].append(dial_hand_string)
            # Mid-level: just choose the outer one.

            outer_shape_abstraction = "base_dial_hand"
            synthetic_dict[MID_LEVEL].append(outer_shape_abstraction)
            synthetic_dict[MID_LEVEL_PARTS].append(short_l_string[-1])
            synthetic_dict[MID_LEVEL_PARAMS].append(str(dial_angle))

        # Add a high-level abstraction corresponding to the dial type.
        object_string = connect_strokes(stroke_strings)
        shape_abstraction = "dial_strokes"
        synthetic_dict[HIGH_LEVEL].append(shape_abstraction)
        synthetic_dict[HIGH_LEVEL_PARTS].append(object_string)

        return [strokes], object_string, synthetic_dict

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

        synthetic_dict = copy.deepcopy(SYNTHETIC_DICT)

        margins = f"(* 4 {tier_scaling})"
        total_base_height = "0"
        total_base_width = "0"
        tier_offset = "0"

        # Place tiers. Note that we don't currently express the looped computation in a loop.
        first_tier_width, first_tier_height = None, None
        assert int(peval(n_tiers)) == peval(n_tiers)

        untransformed_rect_string = None
        for tier_idx in range(int(peval(n_tiers))):
            tier_width = (
                f"(+ (* {base_columns} (+ {base_width} {SCALE_UNIT})) {margins})"
            )
            tier_width = f"(- {tier_width} (* {tier_idx} {margins}))"

            tier_height = f"(+ (* {max_rows} (+ {base_height} {SCALE_UNIT})) {margins})"
            tier_height = f"(* {tier_height} (pow {tier_scaling} {tier_idx}))"

            # Hacky: only allows two tiers
            if tier_idx > 0:
                tier_offset = f"(* {SCALE_UNIT} (+ {tier_height} {first_tier_height}))"

            tier_y = f"(+ (* 0.5 {base_center}) {tier_offset})"
            tier_rect, tier_rect_string = scaled_rectangle_string(
                tier_width, tier_height
            )

            # Place a tier for each low-level abstraction.
            untransformed_rect_string = tier_rect_string
            shape_abstraction = "base_tier_shape"
            synthetic_dict[LOW_LEVEL].append(shape_abstraction)
            synthetic_dict[LOW_LEVEL_PARTS].append(tier_rect_string)
            synthetic_dict[LOW_LEVEL_PARAMS].append(str(peval(tier_y)))

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
        # Place tiers as a mid-level abstraction
        # Mid-level abstraction corresponding to the outer shape.
        outer_shape_abstraction = "base_tiers"
        synthetic_dict[MID_LEVEL].append(outer_shape_abstraction)
        synthetic_dict[MID_LEVEL_PARTS].append(untransformed_rect_string)
        synthetic_dict[MID_LEVEL_PARAMS].append(str(int(peval(n_tiers))))

        # Add decorative finials.
        if base_end_filials:
            filial_width = f"(* 2 {SCALE_UNIT})"
            filial_height = f"(* {first_tier_height} {SCALE_UNIT})"
            filial_rect, filial_rect_string = scaled_rectangle_string(
                w=filial_width, h=filial_height
            )

            shape_abstraction = "base_filial_shape"
            synthetic_dict[LOW_LEVEL].append(shape_abstraction)
            synthetic_dict[LOW_LEVEL_PARTS].append(filial_rect_string)

            outer_shape_abstraction = "base_filials"
            synthetic_dict[MID_LEVEL].append(outer_shape_abstraction)
            synthetic_dict[MID_LEVEL_PARTS].append(filial_rect_string)

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

            shape_abstraction = "base_filial_shape"
            synthetic_dict[LOW_LEVEL].append(shape_abstraction)
            synthetic_dict[LOW_LEVEL_PARTS].append(filial_rect_string)

            total_base_width = f"(+ {total_base_width} (* 2 {filial_width}))"

        # Add the whole base type as a high-level abstraction.
        # Add a high-level abstraction corresponding to the dial type.
        object_string = connect_strokes(stroke_strings)
        shape_abstraction = "all_base_strokes"
        synthetic_dict[HIGH_LEVEL].append(shape_abstraction)
        synthetic_dict[HIGH_LEVEL_PARTS].append(object_string)

        return (
            strokes,
            object_string,
            total_base_width,
            total_base_height,
            synthetic_dict,
        )

    def _generate_stacked_antenna_strings(
        self, n_wires=str(3), antenna_size=str(SMALL), scale_wires=True, end_shape=None
    ):
        """
        Generates stacked antenna. See SimpleAntennaTasksGenerator for original implementation.
        """
        strokes, stroke_strings = [], []

        synthetic_dict = copy.deepcopy(SYNTHETIC_DICT)

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

            shape_abstraction = "antenna_vertical_line"
            synthetic_dict[LOW_LEVEL].append(shape_abstraction)
            synthetic_dict[LOW_LEVEL_PARTS].append(long_vl_string[-1])

            strokes += base_line
            stroke_strings.append(base_line_string)

            assert int(peval(n_wires)) == peval(n_wires)
            largest_antenna_string = ""
            for a_idx in range(int(peval(n_wires))):
                antenna_length = antenna_size
                antenna_height = f"(* 0.5 {antenna_size})"
                if scale_wires:
                    s = f"(- (* {antenna_length} 2) {a_idx})"
                else:
                    s = f"(* {antenna_length} 2)"

                antenna_wire, antenna_wire_string = T_string(
                    short_l_string[0], short_l_string[-1], s=s
                )

                shape_abstraction = "antenna_horizontal_line"
                synthetic_dict[LOW_LEVEL].append(shape_abstraction)
                synthetic_dict[LOW_LEVEL_PARTS].append(antenna_wire_string)
                largest_antenna_string = antenna_wire_string

                antenna_wire, antenna_wire_string = T_string(
                    antenna_wire,
                    antenna_wire_string,
                    y=f"(- (* {antenna_height} 2) {a_idx})",
                )
                strokes += antenna_wire
                stroke_strings.append(antenna_wire_string)

            # Add one for the mid-level abstractions.
            shape_abstraction = "antenna_lines"
            synthetic_dict[MID_LEVEL].append(shape_abstraction)
            synthetic_dict[MID_LEVEL_PARTS].append(largest_antenna_string)
            synthetic_dict[MID_LEVEL_PARAMS].append(str(peval(n_wires)))

        if end_shape:
            # Add end finials
            x_shift = f"(+ {SCALE_UNIT} {antenna_length})"
            finial, finial_string = T_string(
                end_shape[0], end_shape[1], x=f"(- 0 {x_shift})", y=antenna_height
            )
            shape_abstraction = "antenna_finial"
            synthetic_dict[LOW_LEVEL].append(shape_abstraction)
            synthetic_dict[LOW_LEVEL_PARTS].append(finial_string)

            finial, finial_string = T_string(finial, finial_string, y=antenna_height)
            strokes += finial
            stroke_strings.append(finial_string)

            finial, finial_string = T_string(
                end_shape[0], end_shape[1], x=x_shift, y=antenna_height
            )
            shape_abstraction = "antenna_finial"
            synthetic_dict[LOW_LEVEL].append(shape_abstraction)
            synthetic_dict[LOW_LEVEL_PARTS].append(finial_string)

            shape_abstraction = "antenna_finial"
            synthetic_dict[MID_LEVEL].append(shape_abstraction)
            synthetic_dict[MID_LEVEL_PARTS].append(finial_string)

            finial, finial_string = T_string(finial, finial_string, y=antenna_height)
            strokes += finial
            stroke_strings.append(finial_string)

        strokes_string = connect_strokes(stroke_strings)
        synthetic_dict[HIGH_LEVEL].append("whole_antenna")
        synthetic_dict[HIGH_LEVEL_PARTS].append(strokes_string)

        return [strokes], strokes_string, synthetic_dict

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
        stimuli_synthetic_dict=None,
    ):
        if random.uniform(0, 1) > generation_probability:
            return None
        generation_probability *= antenna_generation_probability

        strokes, stroke_strings, synthetic_dicts = [], [], []
        antenna_strokes, antenna_strings, antenna_synthetic_dicts = [], [], []
        for n_wires in ["1", "2", "3"]:
            for scale_wires in [True, False]:
                for end_shape in antenna_end_shapes:
                    (
                        stroke,
                        stroke_string,
                        stroke_dict,
                    ) = self._generate_stacked_antenna_strings(
                        n_wires=n_wires, scale_wires=scale_wires, end_shape=end_shape
                    )
                    antenna_strokes += stroke
                    antenna_strings.append(stroke_string)
                    antenna_synthetic_dicts.append(stroke_dict)

        sideways_antenna_strokes, sideways_antenna_strings, sideways_antenna_dicts = (
            [],
            [],
            [],
        )
        for n_wires in ["2", "3"]:
            stroke, stroke_string, stroke_dict = self._generate_stacked_antenna_strings(
                n_wires=n_wires, scale_wires=False, end_shape=None
            )
            sideways_antenna_strokes += stroke
            sideways_antenna_strings.append(stroke_string)
            sideways_antenna_dicts.append(stroke_dict)

        for base_antenna_primitive, base_antenna_string, base_antenna_dict in zip(
            antenna_strokes, antenna_strings, antenna_synthetic_dicts
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
                new_base_dict = copy.deepcopy(stimuli_synthetic_dict)
                for k in new_base_dict:
                    new_base_dict[k] += base_antenna_dict[k]
                synthetic_dicts.append(new_base_dict)

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
                    new_base_dict = copy.deepcopy(stimuli_synthetic_dict)
                    for k in new_base_dict:
                        new_base_dict[k] += base_antenna_dict[k]
                        new_base_dict[k] += base_antenna_dict[k]
                    synthetic_dicts.append(new_base_dict)

            if random.uniform(0, 1) < generation_probability:
                if add_side_antenna:
                    for (
                        base_sideways,
                        base_sideways_string,
                        base_sideways_dict,
                    ) in zip(
                        sideways_antenna_strokes,
                        sideways_antenna_strings,
                        sideways_antenna_dicts,
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
                        new_base_dict = copy.deepcopy(stimuli_synthetic_dict)
                        for k in new_base_dict:
                            if "params" not in k:
                                new_base_dict[k] += base_antenna_dict[k] + ["rotate"]
                        synthetic_dicts.append(new_base_dict)

        if len(strokes) < 1:
            return None
        return strokes, stroke_strings, synthetic_dicts

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
        strokes, stroke_strings, stroke_dicts = [], [], []

        # Generate antenna.
        antenna_end_shapes = [None, c_string, r_string]
        for n_wires in ["1", "2", "3"]:
            for scale_wires in [True, False]:
                for end_shape in antenna_end_shapes:
                    (
                        antenna_stimuli,
                        antenna_string,
                        antenna_dict,
                    ) = self._generate_stacked_antenna_strings(
                        n_wires=n_wires, scale_wires=scale_wires, end_shape=end_shape
                    )
                    strokes += antenna_stimuli
                    stroke_strings.append(antenna_string)
                    stroke_dicts.append(antenna_dict)

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
                                        stimuli_dict,
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
                                    stroke_dicts.append(stimuli_dict)

        # Randomly sample them.
        return random_sample_ratio_ordered_array(
            strokes, train_ratio, strings_array=list(zip(stroke_strings, stroke_dicts))
        )

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
        strokes, stroke_strings, stroke_dicts = [], [], []

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
                                        stimuli_dict,
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
                                        stimuli_synthetic_dict=stimuli_dict,
                                    )
                                    if antenna_stimuli is not None:
                                        (
                                            stim_strokes,
                                            stim_strings,
                                            stim_dicts,
                                        ) = antenna_stimuli

                                        strokes += stim_strokes
                                        stroke_strings += stim_strings
                                        stroke_dicts += stim_dicts

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
                                                stimuli_dict,
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
                                                stroke_dicts.append(stimuli_dict)

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
                                                stimuli_synthetic_dict=stimuli_dict,
                                            )
                                            if antenna_stimuli is not None:
                                                (
                                                    stim_strokes,
                                                    stim_strings,
                                                    stim_dicts,
                                                ) = antenna_stimuli

                                                strokes += stim_strokes
                                                stroke_strings += stim_strings
                                                stroke_dicts += stim_dicts

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
            strokes, train_ratio, strings_array=list(zip(stroke_strings, stroke_dicts))
        )

        return (
            train_parts + train_main,
            test_parts + test_main,
            train_parts_strings + train_main_strings,
            test_parts_strings + test_main_strings,
        )

    def _generate_train_test_tasks(
        self,
        num_tasks_to_generate_per_condition=AbstractTasksGenerator.GENERATE_ALL,
        train_ratio=0.8,
        max_train=200,
        max_test=50,
    ):
        # Currently generates all tasks as single entities. Does not generate a curriculum.
        train_tasks, test_tasks = self._generate_drawing_tasks_from_strokes(
            num_tasks_to_generate_per_condition,
            request_type=object_primitives.tstroke,
            render_parsed_program_fn=object_primitives.render_parsed_program,
            task_generator_name=self.name,
            train_ratio=train_ratio,
        )
        max_train = len(train_tasks) if max_train == None else max_train
        max_test = len(test_tasks) if max_test == None else max_test
        return train_tasks[:max_train], test_tasks[:max_test]

    def generate_tasks_curriculum(
        self, num_tasks_to_generate_per_condition, train_ratio=0.8
    ):
        """:ret: a curriculum that randomly samples among the train ratio for the simple and complex stimuli."""
        (
            num_tasks_to_generate_per_condition,
            human_readable,
        ) = self._get_number_tasks_to_generate_per_condition(
            num_tasks_to_generate_per_condition, train_ratio
        )
        task_curriculum = TaskCurriculum(
            curriculum_id=human_readable,
            task_generator_name=self.name,
            grammar=self.grammar,
        )

        train_tasks, test_tasks = self._generate_train_test_tasks(
            num_tasks_to_generate_per_condition, train_ratio=train_ratio
        )

        # Add the train tasks.
        task_curriculum.add_tasks(
            split=TaskCurriculum.SPLIT_TRAIN,
            condition=self.name,
            curriculum_block=0,
            tasks=train_tasks,
        )

        # Add the train tasks.
        task_curriculum.add_tasks(
            split=TaskCurriculum.SPLIT_TEST,
            condition=self.name,
            curriculum_block=0,
            tasks=test_tasks,
        )
        return task_curriculum
