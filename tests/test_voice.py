"""Tests for voice message handling"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from pland.services.voice_handler import VoiceHandler

@pytest.fixture
def voice_handler():
    """Create VoiceHandler instance for tests"""
    return VoiceHandler()

@pytest.mark.asyncio
async def test_transcribe_voice_disabled(voice_handler, tmp_path):
    """Test that voice transcription is properly disabled"""
    test_file = tmp_path / "test_voice.ogg"
    test_file.write_bytes(b"test audio content")
    
    result = await voice_handler.transcribe_voice(str(test_file))
    assert result is None

@pytest.mark.asyncio
async def test_save_voice_message_disabled(voice_handler):
    """Test that voice message saving is properly disabled"""
    result = await voice_handler.save_voice_message(b"test audio content", 123)
    assert result is None
