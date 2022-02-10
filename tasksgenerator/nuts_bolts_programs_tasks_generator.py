"""
nuts_bolts_programs_tasks_generator.py | Author : Catherine Wong
Defines TasksGenerators that produce gadget tasks that look like nuts and bolts.

Threads program string generating logic through the generation.
"""
import math, random, itertools, copy
from primitives.gadgets_primitives import *
from dreamcoder.grammar import Grammar
from tasksgenerator.tasks_generator import *
from tasksgenerator.bases_parts_tasks_generator import *
from tasksgenerator.s12_s13_tasks_generator import RANDOM_SEED


@TasksGeneratorRegistry.register
class NutsBoltsProgramsTasksGenerator(AbstractTasksGenerator):
    """Generates gadget tasks containing a base and a set of 'dials' placed at positions along the base."""

    name = "nuts_bolts_programs"

    def __init__(self):
        super().__init__(
            grammar=constants + math_operations + objects + transformations
        )

    def _generate_simple_nuts_stimuli_strings(self, train_ratio):
        """Generates simple nuts: up to two nested shapes on the outer edge, and no perforations. Generates train and test. Also generates strings. See: nuts_bolts_tasks_generator._generate_simple_nuts_stimuli for original implementation."""
        all_strokes = []
        all_strokes_strings = []
        all_synthetic = []
        base_size = LARGE
        for outer_shapes in [
            [cc_string],
            [cc_string, cc_string],
            [hexagon_string],
            [hexagon_string, hexagon_string],
            [octagon_string],
        ]:
            # Note: in theory we could thread these calculations through as strings. For now we do not.
            for outer_shapes_min_size in [base_size * n for n in [1, 2]]:
                for inner_shapes in [[cc_string], [hexagon_string], [r_string]]:
                    for inner_shapes_max_size in [
                        outer_shapes_min_size * scale
                        for scale in [SCALE_UNIT, QUARTER_SCALE]
                    ]:
                        (
                            object_strokes,
                            stroke_strings,
                            synthetic_dict,
                            height,
                            height_strings,
                        ) = self._generate_perforated_shapes_string(
                            outer_shapes=outer_shapes,
                            outer_shapes_min_size=f"{outer_shapes_min_size:g}",
                            inner_shapes=inner_shapes,
                            inner_shapes_max_size=f"{inner_shapes_max_size:g}",
                            n_decorators=str(0),
                        )
                        all_strokes += object_strokes
                        all_strokes_strings.append(stroke_strings)
                        all_synthetic.append(synthetic_dict)

        return random_sample_ratio_ordered_array(
            all_strokes,
            train_ratio,
            strings_array=list(zip(all_strokes_strings, all_synthetic)),
        )

    def _generate_perforated_nuts_stimuli_strings(self, train_ratio):
        """Generates nuts with perforated 'decorators' around the center. Also generates strings. See: nuts_bolts_tasks_generator._generate_perforated_nuts_stimuli for original implementation."""
        all_strokes = []
        all_strokes_strings = []
        all_synthetic = []
        base_size = LARGE
        for outer_shapes in [
            [cc_string],
            [hexagon_string],
            [octagon_string],
            [hexagon_string, hexagon_string],
        ]:
            for outer_shapes_min_size in [base_size * n for n in [2]]:
                for inner_shapes in [[cc_string], [hexagon_string], [r_string]]:
                    for inner_shapes_max_size in [
                        outer_shapes_min_size * scale
                        for scale in [SCALE_UNIT, QUARTER_SCALE]
                    ]:
                        for decorator_shape in [c_string, r_string]:
                            for decorator_size in [SCALE_UNIT]:
                                for n_decorators in [2, 4, 6, 8]:
                                    decorator_displacement = (
                                        f"(* {inner_shapes_max_size:g} {MEDIUM})"
                                    )
                                    (
                                        object_strokes,
                                        stroke_strings,
                                        synthetic_dict,
                                        height,
                                        height_strings,
                                    ) = self._generate_perforated_shapes_string(
                                        outer_shapes=outer_shapes,
                                        outer_shapes_min_size=f"{outer_shapes_min_size:g}",
                                        inner_shapes=inner_shapes,
                                        inner_shapes_max_size=f"{inner_shapes_max_size:g}",
                                        n_decorators=str(n_decorators),
                                        decorator_shape=decorator_shape,
                                        decorator_size=f"{decorator_size:g}",
                                        decorator_displacement=decorator_displacement,
                                    )
                                    all_strokes += object_strokes
                                    all_strokes_strings.append(stroke_strings)
                                    all_synthetic.append(synthetic_dict)

        return random_sample_ratio_ordered_array(
            all_strokes,
            train_ratio,
            strings_array=list(zip(all_strokes_strings, all_synthetic)),
        )

    def _generate_dsl_primitives(self, train_ratio):
        """Generates nuts with perforated 'decorators' around the center. Also generates strings. See: nuts_bolts_tasks_generator._generate_perforated_nuts_stimuli for original implementation."""
        all_strokes = []
        all_strokes_strings = []
        all_synthetic = []
        base_size = LARGE
        for outer_shapes in [[hexagon_string, hexagon_string], []]:
            for outer_shapes_min_size in [base_size * n for n in [2]]:
                for inner_shapes in [[]]:
                    for inner_shapes_max_size in [
                        outer_shapes_min_size * scale
                        for scale in [SCALE_UNIT, QUARTER_SCALE]
                    ]:
                        for decorator_shape in [c_string, r_string]:
                            for decorator_size in [SCALE_UNIT]:
                                for n_decorators in [0, 2, 4, 6, 8]:
                                    decorator_displacement = (
                                        f"(* {inner_shapes_max_size:g} {MEDIUM})"
                                    )
                                    try:
                                        (
                                            object_strokes,
                                            stroke_strings,
                                            synthetic_dict,
                                            height,
                                            height_strings,
                                        ) = self._generate_perforated_shapes_string(
                                            outer_shapes=outer_shapes,
                                            outer_shapes_min_size=f"{outer_shapes_min_size:g}",
                                            inner_shapes=inner_shapes,
                                            inner_shapes_max_size=f"{inner_shapes_max_size:g}",
                                            nesting_scale_unit=str(0.5),
                                            n_decorators=str(n_decorators),
                                            decorator_shape=decorator_shape,
                                            decorator_size=f"{decorator_size:g}",
                                            decorator_displacement=decorator_displacement,
                                        )
                                        all_strokes += object_strokes
                                        all_strokes_strings.append(stroke_strings)
                                        all_synthetic.append(synthetic_dict)
                                    except:
                                        continue
        return random_sample_ratio_ordered_array(
            all_strokes,
            train_ratio,
            strings_array=list(zip(all_strokes_strings, all_synthetic)),
        )

    def _generate_perforated_shapes_string(
        self,
        outer_shapes=[c_string],
        outer_shapes_min_size=str(LARGE),
        inner_shapes=[c_string],
        inner_shapes_max_size=str(SMALL),
        nesting_scale_unit=str(0.25),
        decorator_shape=c_string,
        n_decorators=str(4),
        decorator_size=str(0.25),
        decorator_displacement=str(0.75),
        decorator_start_angle="(/ pi 4)",
        n_spokes=STR_ZERO,
        spoke_angle="(/ pi 4)",
        spoke_length=STR_ZERO,
    ):
        """Generates perforated shapes and a string program that can be evaluated to generate the perforated shape. See dial_tasks_generator._generate_perforated_shapes for the original implementation.

        :ret: object_strokes, stroke_string, height, height_string.

        """
        object_strokes, object_strings, object_synthetic = [], [], []

        synthetic_dict = copy.deepcopy(SYNTHETIC_DICT)
        # Place outer shapes.
        outer_shape_size = peval(outer_shapes_min_size)
        # # Note: catwong: we don't currently express the looped computation in loop.
        if len(outer_shapes) > 0:
            outer_shape_size = peval(outer_shapes_min_size)
            outer_strings = []
            for i, (shape, shape_string) in enumerate(outer_shapes):
                object_stroke, object_string = T_string(
                    shape, shape_string, s=f"{outer_shape_size:g}"
                )

                object_strokes += object_stroke
                outer_strings.append(object_string)
                outer_shape_size += peval(nesting_scale_unit)

                # Add a low-level abstraction corresponding to the shape.
                shape_abstraction = "base_shape"
                synthetic_dict[LOW_LEVEL].append(shape_abstraction)
                synthetic_dict[LOW_LEVEL_PARTS].append(shape_string)
                synthetic_dict[LOW_LEVEL_PARAMS].append(str(peval(nesting_scale_unit)))

            # Mid-level abstraction corresponding to the outer shape.
            outer_shape_abstraction = "outer_strokes"
            synthetic_dict[MID_LEVEL].append(outer_shape_abstraction)
            synthetic_dict[MID_LEVEL_PARTS].append(shape_string)
            synthetic_dict[MID_LEVEL_PARAMS].append(str(outer_shape_size))

            outer_shape_string = connect_strokes(outer_strings)
            object_strings.append(outer_shape_string)

        # Place inner shapes
        if len(inner_shapes) > 0:
            inner_shape_size = peval(inner_shapes_max_size)
            inner_strings = []
            for i, (shape, shape_string) in enumerate(inner_shapes):
                object_stroke, object_string = T_string(
                    shape, shape_string, s=f"{inner_shape_size:g}"
                )
                object_strokes += object_stroke
                inner_shape_size -= peval(nesting_scale_unit)
                inner_strings.append(object_string)

                # Add a low-level abstraction corresponding to the shape.
                shape_abstraction = "base_shape"
                synthetic_dict[LOW_LEVEL].append(shape_abstraction)
                synthetic_dict[LOW_LEVEL_PARTS].append(shape_string)
                synthetic_dict[LOW_LEVEL_PARAMS].append(str(peval(nesting_scale_unit)))

            inner_shape_string = connect_strokes(inner_strings)
            object_strings.append(inner_shape_string)

            # Mid-level abstraction corresponding to the outer shape.
            shape_abstraction = "inner_strokes"
            synthetic_dict[MID_LEVEL].append(shape_abstraction)
            synthetic_dict[MID_LEVEL_PARTS].append(shape_string)
            synthetic_dict[MID_LEVEL_PARAMS].append(str(inner_shape_size))

        # Place decorators along evenly divided segments of a circle.
        # Note that this does not perfectly replicate the for-loop behavior in the original.
        if n_decorators != STR_ZERO:
            decorator_shape, decorator_string = T_string(
                decorator_shape[0], decorator_shape[-1], s=decorator_size
            )
            # Add the individual decorators.
            shape_abstraction = "decorator_strokes"
            synthetic_dict[LOW_LEVEL] += [shape_abstraction] * int(peval(n_decorators))
            synthetic_dict[LOW_LEVEL_PARTS] += [decorator_string] * int(
                peval(n_decorators)
            )

            # Add the whole decorator once as a mid-level abstraction.
            shape_abstraction = "decorator_strokes"
            synthetic_dict[MID_LEVEL].append(shape_abstraction)
            synthetic_dict[MID_LEVEL_PARTS].append(decorator_string)
            synthetic_dict[MID_LEVEL_PARAMS].append(str(peval(n_decorators)))

            decorator_strokes, decorator_string = rotation_string(
                decorator_shape,
                decorator_string,
                n_decorators,
                decorator_displacement,
                decorator_start_angle,
            )
            object_strokes += decorator_strokes
            object_strings.append(decorator_string)

        # Note: the original implementation provides the ability to generate spokes.
        # However, this functionality is actually never used.
        height, height_string = outer_shape_size, f"{outer_shape_size:g}"
        object_string = connect_strokes(object_strings)

        # Finally, add the whole thing as a high level abstraction.
        shape_abstraction = "nuts_bolts_strokes"
        synthetic_dict[HIGH_LEVEL].append(shape_abstraction)
        synthetic_dict[HIGH_LEVEL_PARTS].append(object_string)

        return (
            [object_strokes],
            object_string,
            synthetic_dict,
            height,
            height_string,
        )

    def _generate_strokes_strings_for_stimuli(self, train_ratio):
        (
            simple_train,
            simple_test,
            simple_train_strings,
            simple_test_strings,
        ) = self._generate_simple_nuts_stimuli_strings(train_ratio)
        import pdb

        pdb.set_trace()
        (
            perforated_train,
            perforated_test,
            perforated_train_strings,
            perforated_test_strings,
        ) = self._generate_perforated_nuts_stimuli_strings(train_ratio)

        return (
            simple_train + perforated_train,
            simple_test + perforated_test,
            simple_train_strings + perforated_train_strings,
            simple_test_strings + perforated_test_strings,
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
