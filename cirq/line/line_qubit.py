# Copyright 2018 The Cirq Developers
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import List

from cirq import ops


class LineQubit(ops.QubitId):
    """A qubit on a 1d lattice with nearest-neighbor connectivity."""

    def __init__(self, x: int) -> None:
        """Initializes a line qubit at the given x coordinate."""
        self.x = x

    def is_adjacent(self, other: ops.QubitId) -> bool:
        """Determines if two qubits are adjacent line qubits."""
        return isinstance(other, LineQubit) and abs(self.x - other.x) == 1

    @staticmethod
    def range(*range_args) -> List['LineQubit']:
        """Returns a range of line qubits.

        Args:
            *range_args: Same arguments as python's built-in range method.

        Returns:
            A list of line qubits.
        """
        return [LineQubit(i) for i in range(*range_args)]

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.x == other.x

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash((LineQubit, self.x))

    def __repr__(self):
        return 'LineQubit({})'.format(self.x)

    def __str__(self):
        return '{}'.format(self.x)
