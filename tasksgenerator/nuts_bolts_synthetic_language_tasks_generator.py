"""
nuts_bolts_synthetic_language_tasks_generator.py | Author : Catherine Wong
Defines TasksGenerators that produce gadget tasks that look like nuts and bolts.

Threads a simple synthetic language generator through the tasks.
"""
import math, random, itertools, copy
from primitives.gadgets_primitives import *
from dreamcoder_programs.grammar import Grammar
from tasksgenerator.tasks_generator import *
from tasksgenerator.bases_parts_tasks_generator import *
from tasksgenerator.s12_s13_tasks_generator import RANDOM_SEED


@TasksGeneratorRegistry.register
class NutsBoltsSyntheticLanguageTasksGenerator(AbstractTasksGenerator):
    """Generates gadget tasks containing a base and a set of 'dials' placed at positions along the base."""

    name = "nuts_bolts_synthetic"

    def __init__(self, stochastic_language=False):
        super().__init__(
            grammar=constants + math_operations + objects + transformations
        )

    def _generate_simple_nuts_stimuli_shapes(
        self, train_ratio, stochastic_language=False
    ):
        """Generates simple nuts: up to two nested shapes on the outer edge, and no perforations. Generates train and test. Also generates strings. See: nuts_bolts_tasks_generator._generate_simple_nuts_stimuli for original implementation."""
        all_strokes = []
        all_shapes = []
        base_size = LARGE
        for outer_shapes in [
            [cc_shape],
            [cc_shape, cc_shape],
            [polygon_shape(6)],
            [polygon_shape(6), polygon_shape(6)],
            [polygon_shape(8)],
        ]:
            # Note: in theory we could thread these calculations through as strings. For now we do not.
            for outer_shapes_min_size in [base_size * n for n in [1, 2]]:
                for inner_shapes in [[cc_shape], [polygon_shape(6)], [r_shape]]:
                    for inner_shapes_max_size in [
                        outer_shapes_min_size * scale
                        for scale in [SCALE_UNIT, QUARTER_SCALE]
                    ]:
                        (
                            object_shape,
                            height,
                            height_strings,
                        ) = self._generate_perforated_shapes_shape(
                            outer_shapes=outer_shapes,
                            outer_shapes_min_size=f"{outer_shapes_min_size:g}",
                            inner_shapes=inner_shapes,
                            inner_shapes_max_size=f"{inner_shapes_max_size:g}",
                            n_decorators=str(0),
                        )
                        all_strokes += object_shape.strokes

                        all_shapes.append(object_shape)
        return random_sample_ratio_ordered_array(
            all_strokes, train_ratio, strings_array=all_shapes,
        )

    def _generate_perforated_nuts_stimuli_shapes(
        self, train_ratio, stochastic_language=False
    ):
        """Generates nuts with perforated 'decorators' around the center. Also generates strings. See: nuts_bolts_tasks_generator._generate_perforated_nuts_stimuli for original implementation."""
        all_strokes = []
        all_shapes = []
        base_size = LARGE
        for outer_shapes in [
            [cc_shape],
            [polygon_shape(6)],
            [polygon_shape(8)],
            [polygon_shape(6), polygon_shape(6)],
        ]:
            for outer_shapes_min_size in [base_size * n for n in [2]]:
                for inner_shapes in [[cc_shape], [polygon_shape(6)], [r_shape]]:
                    for inner_shapes_max_size in [
                        outer_shapes_min_size * scale
                        for scale in [SCALE_UNIT, QUARTER_SCALE]
                    ]:
                        for decorator_shape in [c_shape, r_shape]:
                            for decorator_size in [SCALE_UNIT]:
                                for n_decorators in [2, 4, 6, 8]:
                                    decorator_displacement = (
                                        f"(* {inner_shapes_max_size:g} {MEDIUM})"
                                    )
                                    (
                                        object_shape,
                                        height,
                                        height_strings,
                                    ) = self._generate_perforated_shapes_shape(
                                        outer_shapes=outer_shapes,
                                        outer_shapes_min_size=f"{outer_shapes_min_size:g}",
                                        inner_shapes=inner_shapes,
                                        inner_shapes_max_size=f"{inner_shapes_max_size:g}",
                                        n_decorators=str(n_decorators),
                                        decorator_shape=decorator_shape,
                                        decorator_size=f"{decorator_size:g}",
                                        decorator_displacement=decorator_displacement,
                                    )
                                    all_strokes += object_shape.strokes
                                    all_shapes.append(object_shape)

        return random_sample_ratio_ordered_array(
            all_strokes, train_ratio, strings_array=all_shapes,
        )

    def _get_inner_shape_size(self, float_size):
        INNER_SIZING = {0.5: LANG_TINY, 1: LANG_SMALL, 2: LANG_MEDIUM}
        return INNER_SIZING[float_size]

    def _get_outer_shape_size(self, float_size):
        if float_size <= 2:
            return LANG_MEDIUM
        elif float_size > 2 and float_size < 4:
            return LANG_LARGE
        else:
            return LANG_VERY_LARGE

    def _generate_perforated_shapes_shape(
        self,
        outer_shapes=[c_shape],
        outer_shapes_min_size=str(LARGE),
        inner_shapes=[c_shape],
        inner_shapes_max_size=str(SMALL),
        nesting_scale_unit=str(0.25),
        decorator_shape=c_shape,
        n_decorators=str(4),
        decorator_size=str(0.25),
        decorator_displacement=str(0.75),
        decorator_start_angle="(/ pi 4)",
        n_spokes=STR_ZERO,
        spoke_angle="(/ pi 4)",
        spoke_length=STR_ZERO,
        stochastic_langugage=False,
    ):
        """Generates perforated shapes and a string program that can be evaluated to generate the perforated shape. See dial_tasks_generator._generate_perforated_shapes for the original implementation.

        :ret: object_shape, height, height_string.

        """
        full_object_shape = Shape(strokes=[])

        # Place outer shapes.
        outer_shape_size = peval(outer_shapes_min_size)
        # # Note: catwong: we don't currently express the looped computation in loop.

        if len(outer_shapes) > 0:
            outer_shape_size = peval(outer_shapes_min_size)
            outer_shape_objects = []
            for i, shape in enumerate(outer_shapes):
                object_shape = T_shape(shape, s=f"{outer_shape_size:g}")

                object_shape._replace_size_language(
                    new_size=self._get_outer_shape_size(outer_shape_size)
                )
                outer_shape_size += peval(nesting_scale_unit)

                # Add a low-level abstraction corresponding to the shape.
                shape_abstraction = "base_shape"
                object_shape.synthetic_abstractions[LOW_LEVEL].append(shape_abstraction)
                object_shape.synthetic_abstractions[LOW_LEVEL_PARTS].append(
                    shape.base_program
                )
                object_shape.synthetic_abstractions[LOW_LEVEL_PARAMS].append(
                    str(peval(nesting_scale_unit))
                )

                # Add a low-level abstraction corresponding to each object in the outer loop.
                outer_shape_objects.append(object_shape)

            # Mid-level abstraction corresponding to the outer shape.
            outer_shape_abstraction = "outer_strokes"
            full_object_shape.synthetic_abstractions[MID_LEVEL].append(
                outer_shape_abstraction
            )
            full_object_shape.synthetic_abstractions[MID_LEVEL_PARTS].append(
                shape.base_program
            )
            full_object_shape.synthetic_abstractions[MID_LEVEL_PARAMS].append(
                str(outer_shape_size)
            )

            full_object_shape.add_shapes(outer_shape_objects)

        # Place inner shapes
        if len(inner_shapes) > 0:
            inner_shape_size = peval(inner_shapes_max_size)
            inner_shape_objects = []
            for i, shape in enumerate(inner_shapes):
                object_shape = T_shape(shape, s=f"{inner_shape_size:g}")
                new_inner_shape_size = self._get_inner_shape_size(
                    float_size=inner_shape_size
                )
                object_shape._replace_size_language(new_size=new_inner_shape_size)

                inner_shape_size -= peval(nesting_scale_unit)

                # Add a low-level abstraction corresponding to the shape.
                shape_abstraction = "base_shape"
                object_shape.synthetic_abstractions[LOW_LEVEL].append(shape_abstraction)
                object_shape.synthetic_abstractions[LOW_LEVEL_PARTS].append(
                    shape.base_program
                )
                object_shape.synthetic_abstractions[LOW_LEVEL_PARAMS].append(
                    str(peval(nesting_scale_unit))
                )
                inner_shape_objects.append(object_shape)

            # Mid-level abstraction corresponding to the outer shape.
            shape_abstraction = "inner_strokes"
            full_object_shape.synthetic_abstractions[MID_LEVEL].append(
                shape_abstraction
            )
            full_object_shape.synthetic_abstractions[MID_LEVEL_PARTS].append(
                shape.base_program
            )
            full_object_shape.synthetic_abstractions[MID_LEVEL_PARAMS].append(
                str(inner_shape_size)
            )
            full_object_shape.add_shapes(inner_shape_objects)

        # Place decorators along evenly divided segments of a circle.
        # Note that this does not perfectly replicate the for-loop behavior in the original.
        if n_decorators != STR_ZERO:
            decorator_shape = T_shape(decorator_shape, s=decorator_size)

            # Add the individual decorators.
            shape_abstraction = "decorator_strokes"
            full_object_shape.synthetic_abstractions[LOW_LEVEL] += [
                shape_abstraction
            ] * int(peval(n_decorators))
            full_object_shape.synthetic_abstractions[LOW_LEVEL_PARTS] += [
                decorator_shape.base_program
            ] * int(peval(n_decorators))

            # Add the whole decorator once as a mid-level abstraction.
            shape_abstraction = "decorator_strokes"
            full_object_shape.synthetic_abstractions[MID_LEVEL].append(
                shape_abstraction
            )
            full_object_shape.synthetic_abstractions[MID_LEVEL_PARTS].append(
                decorator_shape.base_program
            )
            full_object_shape.synthetic_abstractions[MID_LEVEL_PARAMS].append(
                str(peval(n_decorators))
            )

            decorator_shape = rotation_shape(
                decorator_shape,
                prefix="a ring of",
                n=n_decorators,
                displacement=decorator_displacement,
                decorator_start_angle=decorator_start_angle,
            )

            full_object_shape.add_shapes([decorator_shape])

        # Note: the original implementation provides the ability to generate spokes.
        # However, this functionality is actually never used.
        height, height_string = outer_shape_size, f"{outer_shape_size:g}"

        # Finally, add the whole thing as a high level abstraction.
        shape_abstraction = "nuts_bolts_strokes"
        full_object_shape.synthetic_abstractions[HIGH_LEVEL].append(shape_abstraction)
        full_object_shape.synthetic_abstractions[HIGH_LEVEL_PARTS].append(
            full_object_shape.base_program
        )
        # Remove the empty first language
        full_object_shape.synthetic_language = full_object_shape.synthetic_language[1:]
        full_object_shape.strokes = [full_object_shape.strokes]
        full_object_shape._connect_language()

        return (
            full_object_shape,
            height,
            height_string,
        )

    def _generate_strokes_strings_for_stimuli(
        self, train_ratio, stochastic_language=False
    ):
        (
            simple_train,
            simple_test,
            simple_train_shapes,
            simple_test_shapes,
        ) = self._generate_simple_nuts_stimuli_shapes(train_ratio)

        (
            perforated_train,
            perforated_test,
            perforated_train_shapes,
            perforated_test_shapes,
        ) = self._generate_perforated_nuts_stimuli_shapes(train_ratio)

        return (
            simple_train + perforated_train,
            simple_test + perforated_test,
            simple_train_shapes + perforated_train_shapes,
            simple_test_shapes + perforated_test_shapes,
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
            use_object_shapes=True,
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
