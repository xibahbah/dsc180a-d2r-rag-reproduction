# Saved policy artifacts

`smoke-linucb-policy.pkl.gz` is the compressed policy from the two-question, two-epoch integration test. It is not a full-size trained policy. The original checkpoint is 54,436,145 bytes; its training audit is stored with the smoke results.

Unpack it with `gzip -dk artifacts/smoke-linucb-policy.pkl.gz` and use the pinned upstream code plus the recorded Python environment to load it. This trusted project checkpoint uses cloudpickle; loading it executes Python serialization code.

Full-campaign artifacts will be added after the run completes or stops at its approved spending cap.
