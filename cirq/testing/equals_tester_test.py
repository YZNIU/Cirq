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

import fractions
import pytest

from cirq.testing.equals_tester import EqualsTester


def test_add_equality_group_correct():
    eq = EqualsTester()

    eq.add_equality_group(fractions.Fraction(1, 1))

    eq.add_equality_group(fractions.Fraction(1, 2), fractions.Fraction(2, 4))

    eq.add_equality_group(
        fractions.Fraction(2, 3),
        fractions.Fraction(12, 18), fractions.Fraction(14, 21))

    eq.add_equality_group(2, 2.0, fractions.Fraction(2, 1))

    eq.add_equality_group([1, 2, 3], [1, 2, 3])

    eq.add_equality_group({'b': 3, 'a': 2}, {'a': 2, 'b': 3})

    eq.add_equality_group('unrelated')


def test_assert_add_equality_pair():
    eq = EqualsTester()

    with pytest.raises(AssertionError):
        eq.make_equality_pair(object)

    eq.make_equality_pair(lambda: 1)
    eq.make_equality_pair(lambda: 2)
    eq.add_equality_group(3)

    with pytest.raises(AssertionError):
        eq.add_equality_group(1)
    with pytest.raises(AssertionError):
        eq.make_equality_pair(lambda: 1)
    with pytest.raises(AssertionError):
        eq.make_equality_pair(lambda: 3)


def test_add_equality_group_not_equivalent():
    eq = EqualsTester()
    with pytest.raises(AssertionError):
        eq.add_equality_group(1, 2)


def test_add_equality_group_not_disjoint():
    eq = EqualsTester()
    eq.add_equality_group(1)
    with pytest.raises(AssertionError):
        eq.add_equality_group(1)


def test_add_equality_group_bad_hash():
    class KeyHash:
        def __init__(self, k, h):
            self._k = k
            self._h = h

        def __eq__(self, other):
            return isinstance(other, KeyHash) and self._k == other._k

        def __ne__(self, other):
            return not self == other

        def __hash__(self):
            return self._h

    eq = EqualsTester()
    eq.add_equality_group(KeyHash('a', 5), KeyHash('a', 5))
    eq.add_equality_group(KeyHash('b', 5))
    with pytest.raises(AssertionError):
        eq.add_equality_group(KeyHash('c', 2), KeyHash('c', 3))


def test_add_equality_group_exception_hash():
    class FailHash:
        def __hash__(self):
            raise ValueError('injected failure')

    eq = EqualsTester()
    with pytest.raises(ValueError):
        eq.add_equality_group(FailHash())


def test_can_fail_when_forgot_type_check():
    eq = EqualsTester()

    class NoTypeCheckEqualImplementation:
        def __init__(self):
            self.x = 1

        def __eq__(self, other):
            return self.x == other.x

        def __ne__(self, other):
            return not self == other

        def __hash__(self):
            return hash(self.x)

    with pytest.raises(AttributeError):
        eq.add_equality_group(NoTypeCheckEqualImplementation())


def test_fails_hash_is_default_and_inconsistent():
    eq = EqualsTester()

    class DefaultHashImplementation:
        __hash__ = object.__hash__

        def __init__(self):
            self.x = 1

        def __eq__(self, other):
            if not isinstance(other, type(self)):
                return NotImplemented
            return self.x == other.x

        def __ne__(self, other):
            return not self == other

    with pytest.raises(AssertionError):
        eq.make_equality_pair(DefaultHashImplementation)


def test_fails_when_ne_is_inconsistent():
    eq = EqualsTester()

    class InconsistentNeImplementation:
        def __init__(self):
            self.x = 1

        def __eq__(self, other):
            if not isinstance(other, type(self)):
                return NotImplemented
            return self.x == other.x

        def __ne__(self, other):
            return NotImplemented

        def __hash__(self):
            return hash(self.x)

    with pytest.raises(AssertionError):
        eq.make_equality_pair(InconsistentNeImplementation)


def test_fails_when_not_reflexive():
    eq = EqualsTester()

    class NotReflexiveImplementation:
        def __init__(self):
            self.x = 1

        def __eq__(self, other):
            if other is not self:
                return NotImplemented
            return False

        def __ne__(self, other):
            return not self == other

    with pytest.raises(AssertionError):
        eq.add_equality_group(NotReflexiveImplementation())


def test_fails_when_not_commutative():
    eq = EqualsTester()

    class NotCommutativeImplementation:
        def __init__(self, x):
            self.x = x

        def __eq__(self, other):
            if not isinstance(other, type(self)):
                return NotImplemented
            return self.x <= other.x

        def __ne__(self, other):
            return not self == other

    with pytest.raises(AssertionError):
        eq.add_equality_group(NotCommutativeImplementation(0),
                              NotCommutativeImplementation(1))

    with pytest.raises(AssertionError):
        eq.add_equality_group(NotCommutativeImplementation(1),
                              NotCommutativeImplementation(0))
