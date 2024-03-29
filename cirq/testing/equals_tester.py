# Copyright 2018 The Cirq Developers
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""A utility class for testing equality methods.

To test an equality method, create an EqualityTester and add several groups
of items to it. The equality tester will check that the items within each
group are all equal to each other, but that items between each group are never
equal to each other. It will also check that a==b implies hash(a)==hash(b).
"""

import collections

from typing import Any, Callable

import itertools


class EqualsTester:
    """Tests equality against user-provided disjoint equivalence groups."""

    def __init__(self):
        self.groups = [(_ClassUnknownToSubjects(),)]

    def add_equality_group(self, *group_items: Any):
        """Tries to add a disjoint equivalence group to the equality tester.

        This methods asserts that items within the group must all be equal to
        each other, but not equal to any items in other groups that have been
        or will be added.

        Args:
          *group_items: The items making up the equivalence group.

        Raises:
            AssertionError: Items within the group are not equal to each other,
                or items in another group are equal to items within the new
                group, or the items violate the equals-implies-same-hash rule.
        """

        assert group_items

        # Check that group items are equivalent to each other.
        for v1, v2 in itertools.product(group_items, group_items):
            # Binary operators should always work.
            assert v1 == v2
            assert not v1 != v2

            # __eq__ and __neq__ should both be correct or not implemented.
            assert hasattr(v1, '__eq__') == hasattr(v1, '__ne__')
            # Careful: python2 int doesn't have __eq__ or __ne__.
            if hasattr(v1, '__eq__'):
                eq = v1.__eq__(v2)
                ne = v1.__ne__(v2)
                assert (eq, ne) in [(True, False),
                                    (NotImplemented, False),
                                    (NotImplemented, NotImplemented)]

        # Check that this group's items don't overlap with other groups.
        for other_group in self.groups:
            for v1, v2 in itertools.product(group_items, other_group):
                # Binary operators should always work.
                assert not v1 == v2
                assert v1 != v2

                # __eq__ and __neq__ should both be correct or not implemented.
                assert hasattr(v1, '__eq__') == hasattr(v1, '__ne__')
                # Careful: python2 int doesn't have __eq__ or __ne__.
                if hasattr(v1, '__eq__'):
                    eq = v1.__eq__(v2)
                    ne = v1.__ne__(v2)
                    assert (eq, ne) in [(False, True),
                                        (NotImplemented, True),
                                        (NotImplemented, NotImplemented)]

        # Check that group items hash to the same thing, or are all unhashable.
        hashes = [hash(v) if isinstance(v, collections.Hashable) else None
                  for v in group_items]
        if len(set(hashes)) > 1:
            examples = ((v1, h1, v2, h2)
                        for v1, h1 in zip(group_items, hashes)
                        for v2, h2 in zip(group_items, hashes)
                        if h1 != h2)
            example = next(examples)
            raise AssertionError(
                'Items in the same group produced different hashes. '
                'Example: hash({}) is {} but hash({}) is {}.'.format(*example))

        # Remember this group, to enable disjoint checks vs later groups.
        self.groups.append(group_items)

    def make_equality_pair(self, factory: Callable[[], Any]):
        """Tries to add a disjoint (item, item) group to the equality tester.

        Uses the factory method to produce two different objects containing
        equal items. Asserts that the two object are equal, but not equal to
        any items in other groups that have been or will be added. Adds the
        pair as a group.

        Args:
            factory: A method for producing independent copies of an item.

        Raises:
            AssertionError: The factory produces items not equal to each other,
                or items in another group are equal to items from the factory,
                or the items violate the equal-implies-same-hash rule.
        """
        self.add_equality_group(factory(), factory())


class _ClassUnknownToSubjects:
    """Equality methods should be able to deal with the unexpected."""

    def __eq__(self, other):
        return isinstance(other, _ClassUnknownToSubjects)

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash(_ClassUnknownToSubjects)
