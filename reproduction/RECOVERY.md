# October 31 recovery

The first full baseline exited at 02:58:40 UTC with an invalid JSON response
from the API. The progress log reached 227/500 validation cases; the upstream
script writes its final table only after the loop. This is an incomplete
attempt, not a 500-case result. No stage completion marker was present.

Recovered budget: 762 attempts, 761 settled responses;
`successful_usage_nanodollars=37215300` ($0.0372153 estimated successful usage),
`reserved_nanodollars=47278050` ($0.04727805 including unsettled reservations).
These figures are not an account billing statement. The original campaign
limit remains $5 total, including this attempt and every retry.

`metered_guard.py` now converts malformed successful API JSON into an HTTP
protocol error so the SDK can apply its bounded connection-error retry policy.
The failed attempt keeps its full reservation; every retry reserves separately.
Seven mocked guard tests pass, including malformed synchronous/asynchronous
responses. Upstream experiment source is unchanged.

Jupyter's later restart could not obtain GPU resources and timed out after
300 seconds. The saved experiment lives in the **course workspace**, rather
than the login server's personal home:

- Login host: `/dsmlp/workspaces-fs05/DSC180A_FA26_001/home/x4gong/d2r-reproduction`
- Compute container: `/home/x4gong/d2r-reproduction`
- Course: `DSC180A_FA26_001`

The original campaign status, logs, plans, environment and ledger were backed
up locally before recovery. Retain the original log and ledger. Restarting the
baseline uses its cached indices but repeats the evaluation because upstream
does not save individual completed rows. Do not reset the ledger or present
the interrupted baseline as a completed experiment.
