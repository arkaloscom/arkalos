import pytest
from arkalos.utils import strx

@pytest.mark.parametrize(
    "input_str, expected", 
    [
        ('Mnt Wines', 'mnt_wines'),
        ('mnt wines', 'mnt_wines'),
        (' mnt  wines ', 'mnt_wines'),
        ('MntWines', 'mnt_wines'),
        ('Year_Birth', 'year_birth'),
        ('yearBirth', 'year_birth'),
        ('year_Birth', 'year_birth'),
        ('HTTPRequest', 'http_request'),
        ('HTTP_Request', 'http_request'),
        ('HTTP__Request', 'http_request'),
        ('_ProductId', '_product_id'),
        ('__ProductId', '__product_id'),
        ('__id', '__id')
    ]
)
def test_str_snake_case(input_str, expected):
    assert strx.snake(input_str) == expected



@pytest.mark.parametrize(
    "string, max_length, expected",
    [
        ('The quick brown fox jumps over the lazy dog', 20, 'The quick brown fox'),
        ('http_request_property', 12, 'http_request'),
        ('http_request_property', 13, 'http_request')
    ]
)
def test_str_truncate(string, max_length, expected):
    assert strx.truncate(string, max_length) == expected



@pytest.mark.parametrize(
    "text, max_length, suffix, preserve_words, expected",
    [
        ('The quick brown fox jumps over the lazy dog', 20, '...', False, 'The quick brown fox...'),
        ('The quick brown fox jumps over the lazy dog', 20, ' (...)', False, 'The quick brown fox (...)'),
        ('The quick brown fox', 12, '...', True, 'The quick...'),
        ('Short text', 20, '...', False, 'Short text'),
        ('Hi', 2, '***', False, 'Hi'),
        ('NoSpacesHere', 5, '...', False, 'NoSpa...'),
        ('OneTwoThreeFour', 5, '...', True, 'OneTw...'),
        ('', 10, '...', False, ''),
    ]
)
def test_str_limit(text, max_length, suffix, preserve_words, expected):
    assert strx.limit(text, max_length, suffix, preserve_words) == expected
