# Verification record

Verified on 12 October 2026 UTC (13 October in India), using Python 3.12 and headless Chromium on Linux.

## Passed

- Five Python tests: schema validation, full parking and departure, duplicate/old report rejection, stale-report rejection and expiry, broker-disconnect state, and camera session validation.
- Pure image-comparison checks: unchanged empty frame, occupied region and four-frame state stabilization.
- Browser integration: a vehicle arrived automatically, with a real sensor process sending raw TCP to the gateway, publication through the actual local AMQTT broker, and receipt by the MQTT subscriber/dashboard.
- Browser buttons: transmission pause, expiry to eight unknown slots, resume and recovery.
- Browser camera flow with a synthetic video stream: enable camera, capture empty reference, start detection, detect an inserted visual object, transmit the result through TCP and MQTT, update the dashboard, then detect departure.
- Stopping camera detection eventually changed every slot to unknown.
- Dashboard layout at a 390-pixel viewport had no horizontal page overflow.
- No browser JavaScript exceptions occurred during the tested flow.

## Limits

Camera tests used controlled synthetic video frames, not a physical webcam. Real lighting, camera permissions and device behaviour need testing on the presentation laptop. The camera algorithm detects visual obstruction, not semantic vehicle identity.

Windows BAT launchers and physical two-laptop Wi-Fi were not executed in this Linux environment. No fuel-saving, outdoor accuracy or end-to-end latency measurements are claimed.
