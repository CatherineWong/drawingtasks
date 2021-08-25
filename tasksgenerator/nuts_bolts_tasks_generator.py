"""
nuts_bolts_tasks_generator.py | Author : Catherine Wong
Defines TasksGenerators that produce gadget tasks that look like nuts and bolts.
"""
import math, random, itertools, copy
import primitives.object_primitives as object_primitives
from dreamcoder.grammar import Grammar
from tasksgenerator.tasks_generator import (
    AbstractTasksGenerator,
    ManualCurriculumTasksGenerator,
    TasksGeneratorRegistry,
    TaskCurriculum,
    DrawingTask,
)
from tasksgenerator.bases_parts_tasks_generator import *
from tasksgenerator.dial_tasks_generator import *

# Graphics primitives.
from tasksgenerator.s12_s13_tasks_generator import (
    RANDOM_SEED,
    rand_choice,
    X_MIN,
    X_SHIFT,
    LONG_LINE_LENGTH,
    T,
    long_vline,
    short_hline,
    T_y,
    make_vertical_grating,
    make_x_grid,
    make_grating_with_objects,
    _make_grating_with_objects,
    DEFAULT_X_GRID,
    T_grid_idx,
    hl,
)

c = object_primitives._circle
cc = T(object_primitives._circle, s=2)  # Double scaled circle
r = object_primitives._rectangle
hexagon = object_primitives.polygon(n=6)


@TasksGeneratorRegistry.register
class NutsBoltsTasksGenerator(SimpleDialTasksGenerator):
    """Generates gadget tasks containing a base and a set of 'dials' placed at positions along the base."""

    name = "nuts_bolts"

    def _generate_simple_nuts_stimuli(self):
        """Generates simple nuts: up to two nested shapes on the outer edge, and no perforations."""
        all_strokes = []
        base_size = LARGE
        for outer_shapes in [[cc], [cc, cc], [hexagon], [hexagon, hexagon]]:
            for outer_shapes_min_size in [base_size * n for n in [1, 2]]:
                for inner_shapes in [[cc], [hexagon], [r]]:
                    for inner_shapes_max_size in [
                        outer_shapes_min_size * scale
                        for scale in [SCALE_UNIT, QUARTER_SCALE]
                    ]:
                        object_strokes, height = self._generate_perforated_shapes(
                            outer_shapes=outer_shapes,
                            outer_shapes_min_size=outer_shapes_min_size,
                            inner_shapes=inner_shapes,
                            inner_shapes_max_size=inner_shapes_max_size,
                            n_decorators=0,
                        )
                        all_strokes += object_strokes
        return all_strokes

    def _generate_perforated_nuts_stimuli(self):
        """Generates nuts with perforated 'decorators' around the center."""
        all_strokes = []
        base_size = LARGE
        for outer_shapes in [[cc], [hexagon], [hexagon, hexagon]]:
            for outer_shapes_min_size in [base_size * n for n in [2]]:
                for inner_shapes in [[cc], [hexagon], [r]]:
                    for inner_shapes_max_size in [
                        outer_shapes_min_size * scale
                        for scale in [SCALE_UNIT, QUARTER_SCALE]
                    ]:
                        for decorator_shape in [c, r]:
                            for decorator_size in [SCALE_UNIT]:
                                for n_decorators in [2, 4, 8]:
                                    decorator_displacement = (
                                        inner_shapes_max_size + outer_shapes_min_size
                                    ) * SCALE_UNIT
                                    (
                                        object_strokes,
                                        height,
                                    ) = self._generate_perforated_shapes(
                                        outer_shapes=outer_shapes,
                                        outer_shapes_min_size=outer_shapes_min_size,
                                        inner_shapes=inner_shapes,
                                        inner_shapes_max_size=inner_shapes_max_size,
                                        n_decorators=n_decorators,
                                        decorator_shape=decorator_shape,
                                        decorator_size=decorator_size,
                                        decorator_displacement=decorator_displacement,
                                    )
                                    all_strokes += object_strokes
        return all_strokes

    def _generate_strokes_for_stimuli(self):
        """Main generator function. Returns a list of all stimuli from this generative model as sets of strokes."""
        simple_stimuli = self._generate_simple_nuts_stimuli()
        perforated_stimuli = self._generate_perforated_nuts_stimuli()
        return simple_stimuli + perforated_stimuli
