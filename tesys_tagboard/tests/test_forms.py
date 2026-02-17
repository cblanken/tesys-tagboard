import pytest
from django.core.exceptions import ValidationError

from tesys_tagboard.forms import tagset_to_array


class TestTagSetForm:
    def test_tagset_to_array_conversion(self):
        with pytest.raises(ValidationError):
            assert tagset_to_array("abcd")

        with pytest.raises(ValidationError):
            assert tagset_to_array(["a", "b", "c", "d"])

        with pytest.raises(TypeError):
            assert tagset_to_array(123)

        assert tagset_to_array([1, 2, 3]) == {1, 2, 3}
        assert tagset_to_array([111111111111, 2098081798719871, 398198010871981]) == {
            111111111111,
            2098081798719871,
            398198010871981,
        }
