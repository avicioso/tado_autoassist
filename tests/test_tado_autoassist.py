# tests/test_tado_autoassist.py
import pytest
from unittest.mock import patch, MagicMock
import tado_autoassist as ta  # Adjust module name if different

@patch("tado_autoassist.Path.exists", return_value=True)
@patch("tado_autoassist.Tado")
def test_authenticate_success(mock_tado_class, mock_path_exists):
    # Setup mock Tado object
    mock_tado = MagicMock()
    mock_tado.device_activation_status.return_value = "COMPLETED"
    mock_tado_class.return_value = mock_tado

    # Run the function under test
    ta.authenticate()

    # Assert Tado was instantiated
    mock_tado_class.assert_called_once()

    # Assert device_activation_status was called
    mock_tado.device_activation_status.assert_called()

    # If it reaches here, function completed successfully

@patch("tado_autoassist.Path.exists", return_value=False)
@patch("tado_autoassist.Tado")
def test_authenticate_pending_then_completed(mock_tado_class, mock_path_exists):
    # Mock device activation status: first PENDING, then COMPLETED
    mock_tado = MagicMock()
    mock_tado.device_activation_status.side_effect = ["PENDING", "COMPLETED"]
    mock_tado.device_verification_url.return_value = "http://fakeurl"
    mock_tado_class.return_value = mock_tado

    # Prevent device_activation from doing anything unusual
    mock_tado.device_activation.return_value = None

    # Run the function under test
    ta.authenticate()

    # device_activation_status should be called at least twice, device_activation once
    assert mock_tado.device_activation_status.call_count >= 2
    mock_tado.device_activation.assert_called_once()

# You can add more tests following this pattern for the other functions.
