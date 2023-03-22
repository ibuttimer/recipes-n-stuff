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
from collections import namedtuple
from unittest import TestCase, skip

import pytest

from base.entity_conv import init_entity_conv, escape_entities, \
    unescape_entities

EntityPair = namedtuple(
    'EntityPair', ['unicode', 'escaped'], defaults=['', ''])


class TestEscapeEntities(TestCase):

    DATA = [
        EntityPair(unicode="¿porque No? Mexican Pesto",
                   escaped="&iquest;porque No&quest; Mexican Pesto"),
        EntityPair(unicode="DOLE® Banana",
                   escaped="DOLE&reg; Banana"),
        EntityPair(unicode="Gebhardt\u00AE Chili powder",
                   escaped="Gebhardt&reg; Chili powder"),
        EntityPair(unicode='Soy "Buttermilk"',
                   escaped="Soy &quot;Buttermilk&quot;"),
        EntityPair(unicode="Reeses Squares - "
                           "5 Ingredients & No Bake (Reese's)",
                   escaped="Reeses Squares - "
                           "5 Ingredients &amp; "
                           "No Bake &lpar;Reese&apos;s&rpar;"),
        EntityPair(unicode='" Perfect" Chocolate Frosting',
                   escaped="&quot; Perfect&quot; Chocolate Frosting"),
        EntityPair(unicode="Roasted Garlic & Pearl Onions With Herbs",
                   escaped="Roasted Garlic &amp; Pearl Onions With Herbs"),
        EntityPair(unicode="Mango Chutney  & Pork Medallions",
                   escaped="Mango Chutney  &amp; Pork Medallions"),
        EntityPair(unicode='Basil Pesto - "Lighter Version"',
                   escaped="Basil Pesto - &quot;Lighter Version&quot;"),
        EntityPair(unicode="Crystallized Ginger , Ginger Syrup & Ginger Sugar",
                   escaped="Crystallized Ginger &comma; Ginger Syrup &amp; "
                           "Ginger Sugar"),
        EntityPair(unicode="Chipotle & Lime Marinated Mushrooms",
                   escaped="Chipotle &amp; Lime Marinated Mushrooms"),
        EntityPair(unicode='Gramma\'s Spaghetti Sauce (Cheater "from '
                           'Scratch")',
                   escaped="Gramma&apos;s Spaghetti Sauce &lpar;Cheater "
                           "&quot;from Scratch&quot;&rpar;"),
        EntityPair(unicode='South Beach " Mashed Potatoes/Cauliflower"',
                   escaped="South Beach &quot; Mashed "
                           "Potatoes&sol;Cauliflower&quot;"),
        EntityPair(unicode="Garlic Bread Croûtes",
                   escaped="Garlic Bread Cro&ucirc;tes"),
        EntityPair(unicode='" Tastes Like"  V-8 Juice',
                   escaped="&quot; Tastes Like&quot;  V-8 Juice"),
        EntityPair(unicode='Gluten-Free "canned" Cream of Celery Soup  T-R-L',
                   escaped="Gluten-Free &quot;canned&quot; Cream of Celery "
                           "Soup  T-R-L"),
        EntityPair(unicode="Cheese, Cheese & Onion, Beef & Cheese Enchilada "
                           "Fillings",
                   escaped="Cheese&comma; Cheese &amp; Onion&comma; Beef "
                           "&amp; Cheese Enchilada Fillings"),
        EntityPair(unicode='Baking Mix Aka "bisquick"',
                   escaped="Baking Mix Aka &quot;bisquick&quot;"),
        EntityPair(unicode="Rock & Roll BBQ Salsa Loco (Similar to Baja "
                           "Fresh)",
                   escaped="Rock &amp; Roll BBQ Salsa Loco &lpar;Similar to "
                           "Baja Fresh&rpar;"),
        EntityPair(unicode="Cherries Poached in Vanilla - Cerises Pochées",
                   escaped="Cherries Poached in Vanilla - Cerises "
                           "Poch&eacute;es"),
        EntityPair(unicode="Rock & Roll BBQ Pit Style Beans for the Crock Pot",
                   escaped="Rock &amp; Roll BBQ Pit Style Beans for the Crock "
                           "Pot"),
        EntityPair(unicode="Apple Pie Filling With Vanilla & "
                           "Buttershots! Canning",
                   escaped="Apple Pie Filling With Vanilla &amp; "
                           "Buttershots&excl; Canning"),
        EntityPair(unicode="Died & Went to Pimento Cheese Heaven (Pimiento)",
                   escaped="Died &amp; Went to Pimento Cheese Heaven "
                           "&lpar;Pimiento&rpar;"),
        EntityPair(unicode="Bran & Cranberry Muesli (21 Day Wonder "
                           "Diet: Day 4)",
                   escaped="Bran &amp; Cranberry Muesli &lpar;21 Day Wonder "
                           "Diet&colon; Day 4&rpar;"),
        EntityPair(unicode='Spicy Smoking Hot Chili "no Beans Here!"',
                   escaped="Spicy Smoking Hot Chili &quot;no Beans "
                           "Here&excl;&quot;"),
        EntityPair(unicode="Pâté De Foie Gras",
                   escaped="P&acirc;t&eacute; De Foie Gras"),
        EntityPair(unicode="B H & G Challah Bread",
                   escaped="B H &amp; G Challah Bread"),
        EntityPair(unicode="Quick & Easy Pork Sausage",
                   escaped="Quick &amp; Easy Pork Sausage"),
        EntityPair(unicode='Attar " Syrup" Middle East, Palestine',
                   escaped="Attar &quot; Syrup&quot; Middle East&comma; "
                           "Palestine"),
        EntityPair(unicode="Wondra\u00AE Instant Flour Substitute",
                   escaped="Wondra&reg; Instant Flour Substitute"),
        EntityPair(unicode="Quick & Easy Tahini Sauce",
                   escaped="Quick &amp; Easy Tahini Sauce"),
        EntityPair(unicode="Cheater’s Mexican Chocolate Almond Milk",
                   escaped="Cheater&rsquor;s Mexican Chocolate Almond Milk"),
        EntityPair(unicode="Ct's Baked Egg Patties - Easy & Lean",
                   escaped="Ct&apos;s Baked Egg Patties - Easy &amp; Lean"),
        EntityPair(unicode="Ct's Salsa - Pantry Friendly & Easy",
                   escaped="Ct&apos;s Salsa - Pantry Friendly &amp; Easy"),
        EntityPair(unicode="Basic Béchamel Sauce With Lots of Flavour",
                   escaped="Basic B&eacute;chamel Sauce With Lots of Flavour"),
        EntityPair(unicode='" All In" Meatless Mincemeat',
                   escaped="&quot; All In&quot; Meatless Mincemeat"),
        EntityPair(unicode='Vegan Smoked " Salmon" Spread',
                   escaped="Vegan Smoked &quot; Salmon&quot; Spread"),
        EntityPair(unicode="Citrus & Sweet Wine Marmalade",
                   escaped="Citrus &amp; Sweet Wine Marmalade"),
        EntityPair(unicode="Kamut\u00AE Cookies for Creme",
                   escaped="Kamut&reg; Cookies for Creme"),
        EntityPair(unicode="The Ultimate Creamy Blue Cheese Dressing & Dip",
                   escaped="The Ultimate Creamy Blue Cheese Dressing &amp; "
                           "Dip"),
        EntityPair(unicode='"sun-Dried" Tomatoes',
                   escaped="&quot;sun-Dried&quot; Tomatoes"),
        EntityPair(unicode="Mondo's Hot & Spicy Pickles",
                   escaped="Mondo&apos;s Hot &amp; Spicy Pickles"),
        EntityPair(unicode="Dark Chocolate & Bourbon Bonbons",
                   escaped="Dark Chocolate &amp; Bourbon Bonbons"),
    ]

    @classmethod
    def setUpClass(cls):
        """ Setup test """
        init_entity_conv()

    def test_escape_entities(self):
        """ Test escaping chars with html entity """
        for pair in self.DATA:
            result = escape_entities(pair.unicode, do_ascii=True)
            self.assertEqual(pair.escaped, result)

    def test_unescape_entities(self):
        """ Test escaping chars with html entity """
        for pair in self.DATA:
            result = unescape_entities(pair.escaped)
            self.assertEqual(pair.unicode, result)
