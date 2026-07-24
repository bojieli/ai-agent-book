"""Engine _parser annotation must not be overwritten by a payload key."""
from engine import LogParserEngine, builtin_json_parser


def test_payload_parser_key_does_not_override_engine_tag():
    engine = LogParserEngine()
    engine.register("json", builtin_json_parser)
    line = '{"timestamp": "t", "level": "INFO", "message": "hi", "_parser": "evil"}'
    out = engine.parse_line(line)
    assert out["_parser"] == "json"
    assert out["message"] == "hi"


def test_normal_json_still_tagged():
    engine = LogParserEngine()
    engine.register("json", builtin_json_parser)
    out = engine.parse_line('{"timestamp": "t", "level": "INFO", "message": "ok"}')
    assert out["_parser"] == "json"
    assert out["level"] == "INFO"
