#  MIT License
#
#  Copyright (c) 2023 Ian Buttimer
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to
#  deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM,OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#  DEALINGS IN THE SOFTWARE.
from decimal import Decimal
from unittest import skip

from django.test import TestCase

from recipes.models import Measure
from recipes.conversion import Measures, Quantity


class TestMeasureModel(TestCase):
    """
    Test measure model
    https://docs.djangoproject.com/en/4.1/topics/testing/tools/
    """

    def test_address_defaults(self):
        """ Test measure model defaults """

        measure = Measure.objects.create()
        self.assertIsNotNone(measure)
        self.assertEqual(
            measure.get_field(Measure.TYPE_FIELD), Measure.DRY_FLUID)
        self.assertEqual(
            measure.get_field(Measure.SYSTEM_FIELD), Measure.SYSTEM_US)
        self.assertFalse(
            measure.get_field(Measure.IS_DEFAULT_FIELD))

        for field in [
            Measure.NAME_FIELD, Measure.ABBREV_FIELD
        ]:
            with self.subTest(field=field):
                self.assertEqual(measure.get_field(field), '')

        for field in [
            Measure.BASE_US_FIELD, Measure.BASE_METRIC_FIELD
        ]:
            with self.subTest(field=field):
                self.assertEqual(measure.get_field(field), 1.0)


class TestMeasureModelFixtures(TestCase):
    """
    Test measure model
    https://docs.djangoproject.com/en/4.1/topics/testing/tools/
    """
    fixtures = ['measure.json']

    def test_default_instances(self):
        """ Test default instances """

        # default unit
        default_unit = Measure.get_default_unit()
        self.assert_instance(default_unit, self.value_dict(
            Measure.UNIT, Measure.SYSTEM_ONE, True, 'unit', '', 1.0, 1.0
        ))
        self.assertEqual(Measure.objects.filter(**self.default_filter(
            Measure.UNIT, Measure.SYSTEM_ONE
        )).count(), 1)

        # default us weight
        default_us_weight = Measure.get_default_us_weight()
        self.assert_instance(default_us_weight, self.value_dict(
            Measure.WEIGHT, Measure.SYSTEM_US, True, 'ounce', 'oz.',
            1.0, Decimal('28.349523125')
        ))
        self.assertEqual(Measure.objects.filter(**self.default_filter(
            Measure.WEIGHT, Measure.SYSTEM_US
        )).count(), 1)

        # default us dry/fluid
        default_us_dry_fluid = Measure.get_default_us_dry_fluid()
        self.assert_instance(default_us_dry_fluid, self.value_dict(
            Measure.DRY_FLUID, Measure.SYSTEM_US, True, 'fluid ounce',
            'fl. oz.', 1.0, Decimal('0.2957352968')
        ))
        self.assertEqual(Measure.objects.filter(**self.default_filter(
            Measure.DRY_FLUID, Measure.SYSTEM_US
        )).count(), 1)

        # default metric weight
        default_metric_weight = Measure.get_default_metric_weight()
        self.assert_instance(default_metric_weight, self.value_dict(
            Measure.WEIGHT, Measure.SYSTEM_METRIC, True, 'gram', 'g',
            Decimal('0.0352739619'), 1.0
        ))
        self.assertEqual(Measure.objects.filter(**self.default_filter(
            Measure.WEIGHT, Measure.SYSTEM_METRIC
        )).count(), 1)

        # default metric dry/fluid
        default_metric_dry_fluid = Measure.get_default_metric_dry_fluid()
        self.assert_instance(default_metric_dry_fluid, self.value_dict(
            Measure.DRY_FLUID, Measure.SYSTEM_METRIC, True, 'decilitre',
            'dl', Decimal('3.3814022558'), 1.0
        ))
        self.assertEqual(Measure.objects.filter(**self.default_filter(
            Measure.DRY_FLUID, Measure.SYSTEM_US
        )).count(), 1)


    # @skip
    def test_in_system_conversions(self):
        """ Test defined conversion within the same systems """
        amt = 2
        for q_1, q_2, places in [
            # metric fluid
            (Quantity(Measures.DECILITRE, amt),
             Quantity(Measures.DECILITRE, amt), None),
            (Quantity(Measures.MILLILITRE, amt),
             Quantity.quantised_of(Measures.LITRE, amt/1000), None),
            (Quantity(Measures.CENTILITRE, amt),
             Quantity.quantised_of(Measures.LITRE, amt/100), None),
            (Quantity(Measures.DECILITRE, amt),
             Quantity.quantised_of(Measures.LITRE, amt/10), None),
            # metric weight
            (Quantity(Measures.GRAM, amt),
             Quantity(Measures.GRAM, amt), None),
            (Quantity(Measures.MILLIGRAM, amt),
             Quantity.quantised_of(Measures.GRAM, amt/1000), None),
            (Quantity(Measures.MILLIGRAM, amt),
             Quantity.quantised_of(Measures.KILOGRAM, amt/1e6, places=6), 6),
            (Quantity(Measures.GRAM, amt),
             Quantity.quantised_of(Measures.KILOGRAM, amt/1000), None),
            # us fluid
            (Quantity(Measures.FLUID_OUNCE, amt),
             Quantity(Measures.FLUID_OUNCE, amt), None),
            (Quantity(Measures.FLUID_OUNCE, amt), # 1 gal. == 128 fl. oz.
             Quantity.quantised_of(Measures.GALLON, (1/128)*amt, places=7), 7),
            (Quantity(Measures.FLUID_OUNCE, amt), # 1 qt. == 32 fl. oz.
             Quantity.quantised_of(Measures.QUART, (1/32)*amt, places=5), 5),
            (Quantity(Measures.FLUID_OUNCE, amt), # 1 pt. == 16 fl. oz.
             Quantity.quantised_of(Measures.PINT, (1/16)*amt, places=4), 4),
            (Quantity(Measures.FLUID_OUNCE, amt), # 1 C == 8 fl. oz.
             Quantity.quantised_of(Measures.CUP, (1/8)*amt), None),
            (Quantity(Measures.FLUID_OUNCE, amt), # 1 gi. == 4 fl. oz.
             Quantity.quantised_of(Measures.GILL, (1/4)*amt), None),
            (Quantity(Measures.FLUID_OUNCE, amt), # 1 tcf. == 4 fl. oz.
             Quantity.quantised_of(Measures.TEACUP, (1/4)*amt), None),
            (Quantity(Measures.FLUID_OUNCE, amt), # 1 wgf. == 2 fl. oz.
             Quantity.quantised_of(Measures.WINEGLASS, (1/2)*amt), None),
            (Quantity(Measures.FLUID_OUNCE, amt), # 1 tbsp. == 1/2 fl. oz.
             Quantity.quantised_of(Measures.TABLESPOON, 2*amt), None),
            (Quantity(Measures.FLUID_OUNCE, amt), # 1 dsp. == 1/3 fl. oz.
             Quantity.quantised_of(Measures.DESSERTSPOON, 3*amt), None),
            (Quantity(Measures.FLUID_OUNCE, amt), # 1 tsp. == 1/6 fl. oz.
             Quantity.quantised_of(Measures.TEASPOON, 6*amt), None),
            (Quantity(Measures.FLUID_OUNCE, amt), # 1 fl. dr. == 1/8 fl. oz.
             Quantity.quantised_of(Measures.FLUID_DRAM, 8*amt), None),
            (Quantity(Measures.FLUID_OUNCE, amt), # 1 csp. == 1/16 fl. oz.
             Quantity.quantised_of(Measures.COFFEESPOON, 16*amt), None),
            (Quantity(Measures.FLUID_OUNCE, amt), # 1 ssp. == 1/32 fl. oz.
             Quantity.quantised_of(Measures.SALTSPOON, 32*amt), None),
            (Quantity(Measures.FLUID_OUNCE, amt), # 1 ds. == 1/64 fl. oz.
             Quantity.quantised_of(Measures.DASH, 64*amt), None),
            (Quantity(Measures.FLUID_OUNCE, amt), # 1 pn. == 1/128 fl. oz.
             Quantity.quantised_of(Measures.PINCH, 128*amt), None),
            (Quantity(Measures.FLUID_OUNCE, amt), # 1 smdg. == 1/256 fl. oz.
             Quantity.quantised_of(Measures.SMIDGEN, 256*amt), None),
            (Quantity(Measures.FLUID_OUNCE, amt), # 1 dr. == 1/576 fl. oz.
             Quantity.quantised_of(Measures.DROP, 576*amt), None),
            # us weight
            (Quantity(Measures.OUNCE, amt),
             Quantity(Measures.OUNCE, amt), None),
            (Quantity(Measures.OUNCE, amt), # 1 dr. == 1/16 oz.
             Quantity.quantised_of(Measures.DRAM, 16*amt), None),
            (Quantity(Measures.OUNCE, amt), # 1 lb. == 16 oz.
             Quantity.quantised_of(Measures.POUND, (1/16)*amt, places=4), 4),
            (Quantity(Measures.OUNCE, amt), # 1 st. == 224 oz.
             Quantity.quantised_of(Measures.STONE, Decimal(1/224)*amt, places=10), 10),
        ]:
            for idx in range(2):
                if idx == 0:
                    from_q = q_1
                    to_q = q_2
                else:
                    from_q = q_2
                    to_q = q_1
                with self.subTest(from_q=from_q, to_q=to_q):
                    converted = from_q.convert_to(
                        to_q.measure, quantised=True,
                        places=places or Quantity.STD_PLACES)
                    self.assertEqual(converted.measure, to_q.measure)
                    self.assertEqual(converted.amount,
                                     Quantity.standardise(to_q.amount))

    def test_inter_system_conversions(self):
        """ Test defined conversion between different systems """
        amt = 2
        for q_1, q_2, places in [
            # fluid
            (Quantity(Measures.DECILITRE, amt),
             Quantity.quantised_of(Measures.FLUID_OUNCE, 3.3814*amt), None),
            (Quantity(Measures.MILLILITRE, amt),
             Quantity.quantised_of(Measures.FLUID_OUNCE, 0.033814*amt, places=6), 6),
            (Quantity(Measures.CENTILITRE, amt),
             Quantity.quantised_of(Measures.FLUID_OUNCE, 0.33814*amt, places=6), 6),
            (Quantity(Measures.LITRE, amt),
             Quantity.quantised_of(Measures.FLUID_OUNCE, 33.814*amt), None),
            (Quantity(Measures.DECILITRE, amt),
             Quantity.quantised_of(Measures.GALLON, 0.0264172*amt, places=6), 6),
            (Quantity(Measures.DECILITRE, amt),
             Quantity.quantised_of(Measures.QUART, 0.105669*amt, places=4), 4),
            (Quantity(Measures.DECILITRE, amt),
             Quantity.quantised_of(Measures.PINT, 0.211338*amt, places=4), 4),
            (Quantity(Measures.DECILITRE, amt),
             Quantity.quantised_of(Measures.CUP, 0.422675*amt, places=4), 4),
            (Quantity(Measures.DECILITRE, amt),
             Quantity.quantised_of(Measures.GILL, 0.845351*amt), None),
            (Quantity(Measures.DECILITRE, amt),
             Quantity.quantised_of(Measures.TEACUP, 0.845351*amt), None),
            # weight
            (Quantity(Measures.OUNCE, amt),
             Quantity.quantised_of(Measures.GRAM, 28.3495*amt), None),
            (Quantity(Measures.OUNCE, amt),
             Quantity.quantised_of(Measures.KILOGRAM, 0.0283495*amt, places=4), 4),
        ]:
            for idx in range(2):
                if idx == 0:
                    from_q = q_1
                    to_q = q_2
                else:
                    from_q = q_2
                    to_q = q_1
                with self.subTest(from_q=from_q, to_q=to_q):
                    converted = from_q.convert_to(
                        to_q.measure, quantised=True,
                        places=places or Quantity.STD_PLACES)
                    self.assertEqual(converted.measure, to_q.measure)
                    self.assertEqual(converted.amount,
                                     Quantity.standardise(to_q.amount))

    def assert_instance(self, measure: Measure, values: dict):
        """ Check the values of an instance """

        self.assertIsNotNone(measure)

        for field in [
            Measure.TYPE_FIELD, Measure.SYSTEM_FIELD,
            Measure.IS_DEFAULT_FIELD, Measure.NAME_FIELD,
            Measure.ABBREV_FIELD, Measure.BASE_US_FIELD,
            Measure.BASE_METRIC_FIELD
        ]:
            with self.subTest(field=field):
                self.assertEqual(
                    measure.get_field(field), values[field])

    @staticmethod
    def value_dict(
            measure_type: str, system: str, is_default: bool,
            name: str, abbrev: str, base_us: Decimal, base_metric: Decimal
    ):
        """ Dict for checking instance values """
        return {
            Measure.TYPE_FIELD: measure_type,
            Measure.SYSTEM_FIELD: system,
            Measure.IS_DEFAULT_FIELD: is_default,
            Measure.NAME_FIELD: name,
            Measure.ABBREV_FIELD: abbrev,
            Measure.BASE_US_FIELD: base_us,
            Measure.BASE_METRIC_FIELD: base_metric
        }

    @staticmethod
    def default_filter(measure_type: str, system: str):
        """ Filter query for a default instance """
        return {
            Measure.TYPE_FIELD: measure_type,
            Measure.SYSTEM_FIELD: system,
            Measure.IS_DEFAULT_FIELD: True,
        }
