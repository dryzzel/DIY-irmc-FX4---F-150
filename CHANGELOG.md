# Changelog

## Public repository preparation — 2026-11-27

- Documented several weeks of installed operation on my 2007 F-150 FX4.
- Established `pico_final/` as the permanent firmware source, with current English
  and Spanish guides. Firmware behavior and calibration values were preserved.
- Moved earlier firmware and tests to `legacy/`, historical documents to
  `docs/archive/`, and the isolated Monitor test to `examples/`.
- Added portable host test commands, CI, release packaging and local-data exclusions.
- Selected GPL-3.0-only for the project code and included the full license.
- Removed tracked Python caches from the current index; historical commits still
  require consideration before publishing their history (see `docs/RELEASING.md`).
- Unified the project voice, added a bilingual documentation index and recorded
  the repository review in `docs/en/project-review.md` and `docs/es/project-review.md`.

## final-1 — installed 2026-11-02

- Independent permanent controller, 40% to 70% PWM with a 20 ms ramp.
- Three-second motion budget reset by a new stable destination or settled arrival.
- Hall endpoint detection, hysteresis, 50 ms brake and settled Monitor feedback.
- Automatic recovery after 30 seconds plus valid/stable input qualification.
- Continuous operation without test-log files; built-in LED disabled.
- Initial local validation: 51 host tests across final and historical code, plus
  compilation and hash-verified installation on the development Pico.

Vehicle results describe my installation. Host simulations check software behavior;
neither establishes compatibility with every vehicle or automotive certification.
