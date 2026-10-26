# Vue migration regression checklist

A family moves from the baseline to the Vue implementation only after all applicable checks pass.

## Offline fixture gate

- [ ] Replay every complete frozen capture for the family.
- [ ] Reject or preserve every partial capture without joining separate attempts.
- [ ] Produce the same identity state: identified, ambiguous, hidden or unknown.
- [ ] Produce the same physical winner where the capture exposes it.
- [ ] Preserve packet count, order, checksum validation and timeout semantics.
- [ ] Use the shared probability JSON without hardcoded duplicate tables.

## Browser gate

- [ ] WebUSB connects to the CH340 after a user gesture.
- [ ] Disconnect and reconnect leave no stale battle state.
- [ ] The critical battle decision runs locally without a server round trip.
- [ ] Serial output remains visible and the general reset clears it.
- [ ] GPS changes render live when permission is granted and fail gracefully otherwise.
- [ ] Direct loading and refreshing `/vpet/` works over HTTPS.

## Hardware gate

- [ ] Physical Digimon is detected without a manual selector.
- [ ] A full battle completes on the V-Pet.
- [ ] Web and physical winner agree.
- [ ] Both possible outcomes are exercised when the protocol allows control.
- [ ] Correct Reference Book name, image, level, attribute, type and attacks load.
- [ ] Winner highlight works when either the left or right fighter wins.
- [ ] Completed transcript is stored after the time-critical USB exchange.

## Cutover rule

Keep the current Python application available until every device currently marked verified in `DEVICE_MATRIX.md` passes this checklist. Pending and untested families remain visibly labeled experimental; they do not block the initial migration.
