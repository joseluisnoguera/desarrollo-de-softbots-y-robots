"""Tests for UI components module."""

from unittest.mock import Mock, patch

from src.ui_components import UIComponents


class TestUIComponents:
    """Test UI component functions."""

    @patch('src.ui_components.st')
    @patch('src.utils.validate_conversation_requirements')
    def test_render_sidebar_configuration(self, mock_validate, mock_st):
        """Test rendering sidebar configuration."""
        # Mock validation to return True
        mock_validate.return_value = (True, None)

        # Mock session state to return valid values
        mock_session_state = {
            "discussion_topic": "Test topic",
            "message_count": 1,
            "agent1_personality": "Test personality",
            "agent1_stance": "Test stance",
            "agent1_model": "gemini-1.5-flash",
            "agent1_temperature": 0.7,
            "agent2_personality": "Test personality",
            "agent2_stance": "Test stance",
            "agent2_model": "gemini-1.5-flash",
            "agent2_temperature": 0.7,
        }
        mock_st.session_state.get.side_effect = lambda key, default=None: mock_session_state.get(key, default)

        # Mock streamlit components
        mock_st.sidebar.__enter__ = Mock(return_value=None)
        mock_st.sidebar.__exit__ = Mock(return_value=None)
        mock_st.header = Mock()
        mock_st.text_area = Mock()
        mock_st.slider = Mock()
        mock_st.text_input = Mock()
        mock_st.selectbox = Mock()
        mock_st.markdown = Mock()
        mock_st.warning = Mock()
        mock_st.button.return_value = True

        # Mock st.columns to return mock column objects
        mock_col1 = Mock()
        mock_col2 = Mock()
        mock_col1.__enter__ = Mock(return_value=mock_col1)
        mock_col1.__exit__ = Mock(return_value=None)
        mock_col2.__enter__ = Mock(return_value=mock_col2)
        mock_col2.__exit__ = Mock(return_value=None)
        mock_st.columns.return_value = [mock_col1, mock_col2]

        result = UIComponents.render_sidebar_configuration()

        assert result is True
        mock_st.button.assert_called()
