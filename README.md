# undeniably-undoubtedly-universally-unique-identifier

Ever had a problem where you just *had* to be 100% sure that an identifier you generated was unique, beyond any shadow of a doubt, no matter how astronomically unlikely a collision might be?

YES?

Well, good for you! Cause I have a solution for the times where:

### 128 bits is just not *enough*

128 bits of randomness (UUIDv4) gives you about 5.3x10^36 possible values. That sounds like a lot, right? But in massive distributed systems, or over long periods of time, the probability of a collision can become non-negligible. And when the probability is non-neglibile, then that makes all the unmedicated people *very* nervous.

SO INDULGE YOUR NEED FOR ABSOLUTE CERTAINTY!
let your anxiety take over and use UUUUID (undeniably undoubtedly universally unique identifier) an algorithm that uses a globally accessible database of all the UUUUIDs ever created and has a system that when you create a new UUUUID the system checks if an UUUUID already exists before creating it, *recursively* to make sure that it is 100% certainly, undeniably, undoubtedly, universally unique!

![comparison between UUID and UUUUID](markdown/comparison.png)
> No generative AI used to create this image. It was raw-dogged in MS Paint like God intended. <br><br>
> Unrelated: We're looking for a graphic designer to make it less shit, please contribute T__T

<br>
The UUUUID Framework is a high-assurance, extreme-entropy identifier generation and registration system designed for environments where any risk of identifier collision (no matter how improbably small) is unacceptable.

Conventional identifiers such as UUIDv4 (122 bits of randomness) or even cryptographic hashes (256–512 bits) provide statistical uniqueness that is “practically sufficient.”
However, do you even know what practically sufficient means? Fuck no. Systems operating under strict determinism, multi-node conflict sensitivity, or regulated audit environments may require provable, enforced global uniqueness guarantees at runtime.

<br>

### The UUUUID Framework addresses this requirement by:

Generating identifiers of 8192 bits (1024 bytes) using SHAKE256.

Incorporating multiple entropy sources, reordered on every generation.

Maintaining a global registry (local or remote) to ensure strict non-duplication.

Enforcing iterative collision checks during creation.

Supporting inter-process and inter-host coordination via an HTTP registry API.

This framework is engineered with the expectation that collisions must not merely be unlikely—they must be impossible unless SHA-3 itself fails as a cryptographic primitive.

<br>
## Design Goals
### Unbounded Uniqueness

While 8192-bit identifiers already exceed collision-resistance thresholds by astronomical margins, the framework treats any non-zero probability as unacceptable.
Hence the mandatory registration step via local or remote registry ensures identifiers are never reissued.

### Entropy Source Unpredictability

Each UUID integrates:

64 bytes of OS-level cryptographic randomness (two 32-byte pulls).

16-byte monotonic counter.

16-byte nanosecond-precision timestamp.

32-byte machine fingerprint (sha256 over nodename + machine).

1024-byte evolving historical state.

Randomized ordering of all entropy components before hashing.

This prevents state-reuse attacks, predictable-pattern attacks, and correlation inference.

### Recursive / Iterative Collision Prevention

Identifier generation is not complete until:

The 8192-bit candidate is produced.

The system checks whether it exists in the registry.

If it does, a new candidate is generated.

Only once a candidate is guaranteed free of duplication is it accepted.

This approach reduces the collision probability to:

P(collision) = 0, assuming SHA-3 is collision-resistant and registry integrity is maintained and that the entropy sources are not fully compromised and that we don't live in a Matrix where it fails cause fuck knows why?

<br>

## System Architecture
### Local Generator

The generator constructs candidate identifiers with all sources of entropy described above and uses SHAKE256 to produce a 1024-byte value.

### Registry Integration

The generator supports two registry modes:

- Local In-Memory Registry (Default)

- Process-wide.

- Synchronized via internal locks.

- Suitable for development or single-node deployment.

- Remote HTTP Registry (Optional)

Activated through:

`REGISTRY_API_URL=http://host:port`


The generator will attempt:

```bash
POST /registry/register
{"id": "<8192-bit hex string>"}
```


The registry responds with:

`{"registered": true} ->` ID is globally unique and accepted.

`{"registered": false} ->` Collision detected; generation continues until success.

### Historical State Evolution

Each generated identifier updates the 1024-byte rolling _history_hash, ensuring that:

- No two generations share identical internal state.

- Even identical entropy inputs (counter, timestamp, environment) would diverge due to historical chaining.

### Threat Model and Guarantees
The system protects against:

= Accidental collisions across large-scale distributed deployments.

- Predictable identifier generation patterns.

- Replay of previous UUID states.

- Cross-process conflicts on multi-instance deployments.

- Partial or total entropy source failure (fallback sources are intertwined).

- Registry desynchronization (remote registry ensures single source of truth).

### The system does not protect against:

- SHA-3 (SHAKE256) being broken as a cryptographic primitive.

- Registry tampering by hostile operators.

- Malicious nodes intentionally bypassing registration.

- God-level adversaries controlling all entropy sources.

- Environmental conditions causing entropy degradation beyond recovery.

- Heat death of the universe scenarios.

Any such conditions are considered outside scope, and responsibility shifts to infrastructure governance.

<br>

## API Endpoints
### GET /uuuuid

Returns a newly generated, globally unique 8192-bit UUUUID.

### POST /registry/register

Registers a candidate ID.
Ensures no duplicates are issued.

Request:

`{"id": "<hex-string>"}`


Responses:

`{"registered": true}`

`{"registered": false, "reason": "exists"}`

`{"registered": false, "reason": "missing id"}`

`GET /registry/<hex>`

Check whether a UUID exists.

### GET /registry

Returns registry statistics:

`{"entries": <int>}`

### Operational Deployment Mode

Start the server:

```bash
python uuuuid.py --serve --host 0.0.0.0 --port 5000
```


Non-server generation:

```bash
python uuuuid.py --count 5
```

## Performance Expectations

Despite using SHAKE256 on 1–2 kB payloads and emitting 1024-byte digests, performance remains suitable for most applications, subject to:

- CPU availability

- Registry latency (if remote)

- Expected volume of identifier operations

If registry latency is high, throughput degrades proportionally because no identifier is valid until global uniqueness is confirmed.

**This is intentional**: the design prioritizes correctness over performance.

## Security Considerations

Side-channel resistance
Entropy components and random ordering prevent pattern inference.

State disclosure hazard
Historical state must remain private.
If it leaks, partial prediction attacks are theoretically possible.

Registry integrity
The registry must be secured.
If a node inserts fraudulent entries, it can deny future UUUUIDs.

Entropy exhaustion
The system intentionally uses multiple entropy sources to mitigate degradation risks.

## Conclusion

The UUUUID Framework is designed for developers who cannot tolerate collision probabilities that, while mathematically negligible, still exist in conventional identifier systems.
It is suitable for:

- Distributed ledgers
    
- Security enforcement layers

- High-stakes audit trails

- Any workload where accidental duplication is unacceptable even once

> PLEASE DO NOT USE THIS FOR ANYTHING IMPORTANT, IF YOU WERE NOT ABLE TO DECIPHER THIRTY LAYERS OF SARCASM, YOU PROBABLY SHOULT NOT BE USING THE INTERNET

Its extreme entropy budget, global registry enforcement, and state-binding architecture make it one of the most collision-averse identifier generation systems available.

If an identifier conflict ever occurs under this system, the recommended response is to immediately pause all operations, initiate full forensic analysis, and reassess the integrity of the underlying cryptographic primitives and registry infrastructure.

<br><br><br>

# Existential crisis I endured during the creation of this project

During creation of this monstrosity I was curious what would be the probability of this actually causing a conflict given the astronomical size of the identifier space.

While no collision should appear, like ever, it is not foolproof. We could have ran out UUUUIDs and what if two machines generated the same random data at the exact same nanosecond and had the same counter and machine fingerprint and history hash? **THAT WOULD BE BAD**

<br>

## Liminality of Life

Once you put the numbers into perspective, the sheer scale and improbability of a collision becomes kind of unsettling. The uncanny valley of knowing nothing is certain, versus the overwhelming odds stacked against you that it will never happen in your human life. Though if ran for infinity, it would eventually happen.

In the end, living your life is just being stuck in the liminal place between vastness of nothing and the hopeful idea that something will happen.

<br>

## Perfect conditions: heat death of the universe

Under birthday attack someone would need to generate `10^1234` UUUUIDs to have a 50% chance of collision.

Two independently generated UUUUIDs collide with probability `1/(2^8192)`, which is about `1/(10^2466)`.

To put into perspective how small `10^-2466` is, consider that the observable universe contains approximately `10^80` atoms. Even if each atom generated a UUUUID every Planck time (approximately `10^-43` seconds) for the entire age of the universe (about `10^17` seconds), the total number of UUUUIDs generated would be around `10^(80 + 17 + 43) = 10^140`, which is still astronomically smaller than `10^2466`.

<br>

## If Gods existed, UUUUIDs would outlive them all

Or for more humanised version. If you were to shuffle a deck of cards and only once you hit a perfectly shuffled deck of cards that it matches the factory order. Once that happens, remove one singular atom from the top of Mount Everest. Once you have flattened Mount Everest atom by atom till it reaches the sea level, remove one atom from all of the worlds oceans and put back all the atoms in their original position on Mount Everest.

You should have dismountled Mount Everest, and taken one atom out of the ocean (all while waiting for the perfect shuffle to happen)

Once the oceans are gone, take one atom away from the entire planet Earth. Put the Oceans and Mount Everest and keep iterating this process till the entire planet is gone.

Then move onto the solar system.

Then the galaxy.

Then the galaxy cluster.

Then the supercluster.

Then the observable universe.

Then the entire universe.

All while waiting for the perfect shuffle to happen and restoring all the atoms back to their original position once you advance to the next step.

You wouldn't have even hit the 10^2000 mark *yet.*

<br>

## Go hug your family

The odds of collision are so vastly low that they are way past the incomprehensible mark for the human brain to understand. I am staring at the numbers and grasping their meaning is hard. You only have so much time to live your life and worrying about something like this is definitely an entertaining thing, but ultimately pointless.

<br>
So go hug your family, go outside, enjoy the little things in life. Pet that cute dog, have icream, watch the sunset.

<br>

# Final note

This project is a satire and should not be used in any production environment. The absurdity of its design highlights the impracticality of striving for absolute uniqueness in identifier generation. In real-world applications, standard UUIDs or other established methods are sufficient and recommended.

Howver, if you do want to make sure your IDs are undeniably, undoubtedly, universally unique, well...

Your odds of a collision are lower than the odds of your crush liking you back.

But sadly,<br>
*not undeniably, undoubtedly, universally uniquely zero.*
