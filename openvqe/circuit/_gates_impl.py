from abc import ABC

import numpy
import copy


class QGateImpl:

    @staticmethod
    def list_assignement(o):
        """
        Helper function to make initialization with lists and single elements possible
        :param o: iterable object or single element
        :return: Gives back a list if a single element was given
        """
        if o is None:
            return None
        elif hasattr(o, "__get_item__"):
            return o
        elif hasattr(o, "__iter__"):
            return o
        else:
            return [o]

    def __init__(self, name, target: list, control: list = None, phase=1.0):
        self.name = name
        self.phase = phase
        self.target = self.list_assignement(target)
        self.control = self.list_assignement(control)
        self.verify()

    def is_frozen(self):
        raise Exception(
            'unparametrized gates cannot be frozen because there is nothing to freeze. \n If you want to iterate over all your gates, use is_differentiable as a criterion before or in addition to is_frozen')

    def dagger(self):
        """
        :return: return the hermitian conjugate of the gate.
        """

        return QGateImpl(name=copy.copy(self.name), target=copy.deepcopy(self.target),
                         control=copy.deepcopy(self.control), phase=numpy.conj(self.phase))

    def is_controlled(self) -> bool:
        """
        :return: True if the gate is controlled
        """
        return self.control is not None

    def is_parametrized(self) -> bool:
        """
        :return: True if the gate is parametrized
        """
        return False

    def is_single_qubit_gate(self) -> bool:
        """
        Convenience and easier to interpret
        :return: True if the Gate only acts on one qubit (not controlled)
        """
        return (self.control is None or len(self.control) == 0) and len(self.target) == 1

    def is_differentiable(self) -> bool:
        '''
        defaults to False, overwridden by ParametrizedGate
        '''
        return False

    def verify(self):
        if self.target is None:
            raise Exception('Recieved no targets upon initialization')
        if len(self.list_assignement(self.target)) < 1:
            raise Exception('Recieved no targets upon initialization')
        if self.is_controlled():
            for c in self.target:
                if c in self.control:
                    raise Exception("control and target are the same qubit: " + self.__str__())
        if not numpy.isclose(numpy.abs(self.phase), 1.0):
            raise Exception('Phase must lie on the complex unit circle (I.E, have modulus of 1)')

    def __str__(self):
        result = str(self.name) + "(target=" + str(self.target)
        if not self.is_single_qubit_gate():
            result += ", control=" + str(self.control)
        result += ")"
        return result

    def __repr__(self):
        """
        Todo: Add Nice stringification
        """
        return self.__str__()

    def max_qubit(self):
        """
        :return: highest number qubit in this gate
        """
        result = max(self.target)
        if self.control is not None:
            result = max(result, max(self.control))
        return result + 1

    def decomp(self):
        '''
        returns a restructured version of the gate, such that all supported backends have some implementation thereof.
        This may decompose poly-controlled gates into a cascade of CNOT and basis shifters, or may convert swap to a chain of cnot.
        All pre-defined gates overwrite this method to return something other than an error.
        '''
        raise NotImplementedError()

    def is_phased(self):
        '''
        TODO: make sure this is functional.
        '''
        return self.phase not in [1.0, 1.0 + 0.j]


class ParametrizedGateImpl(QGateImpl, ABC):
    '''
    the base class from which all parametrized gates inherit. User defined gates, when implemented, are liable to be members of this class directly.
    Has su
    '''

    def __init__(self, name, parameter, target: list, control: list = None, frozen: bool = False, phase=1.0):
        super().__init__(name, target, control, phase=phase)
        self.parameter = parameter
        if self.parameter is None:
            raise Exception('Parametrized gates require a parameter!')
        self.frozen = frozen

    def is_frozen(self):
        '''
        :return: return wether this gate is frozen or not.
        '''
        return self.frozen

    def is_parametrized(self) -> bool:
        """
        :return: True if the gate is parametrized
        """
        return True

    def is_differentiable(self) -> bool:
        """
        :return: True if the gate is differentiable
        """
        return True

    def __str__(self):
        result = str(self.name) + "(target=" + str(self.target)
        if not self.is_single_qubit_gate():
            result += ", control=" + str(self.control)

        result += ", parameter=" + str(self.parameter)
        result += ")"
        return result

    def max_qubit(self):
        """
        :return: Determine maximum qubit index needed
        """
        result = max(self.target)
        if self.control is not None:
            result = max(result, max(self.control))
        return result + 1


class RotationGateImpl(ParametrizedGateImpl):

    @staticmethod
    def get_name(axis):
        if axis == 0:
            return "Rx"
        elif axis == 1:
            return "Ry"
        elif axis == 2:
            return "Rz"

    @property
    def angle(self):
        return self.parameter

    @angle.setter
    def angle(self, power):
        self.parameter = power

    def __init__(self, axis, angle, target: list, control: list = None, frozen: bool = False, phase=1.0):
        super().__init__(name=self.get_name(axis=axis), parameter=angle, target=target, control=control, frozen=frozen,
                         phase=phase)
        self.axis = axis


class PowerGateImpl(ParametrizedGateImpl):

    @property
    def power(self):
        return self.parameter

    @power.setter
    def power(self, power):
        self.parameter = power

    def __init__(self, name, target: list, power=1.0, control: list = None, frozen: bool = False, phase=1.0):
        super().__init__(name=name, parameter=power, target=target, control=control, frozen=frozen,
                         phase=phase)