# stackdiff

> CLI tool to compare and diff infrastructure stack outputs across environments

---

## Installation

```bash
pip install stackdiff
```

Or install from source:

```bash
pip install git+https://github.com/yourorg/stackdiff.git
```

---

## Usage

Compare stack outputs between two environments:

```bash
stackdiff --stack my-app --env staging --env production
```

Diff a specific output key:

```bash
stackdiff --stack my-app --env dev --env prod --key DatabaseEndpoint
```

Output as JSON:

```bash
stackdiff --stack my-app --env staging --env production --format json
```

### Example Output

```
Stack: my-app
─────────────────────────────────────────
Key                  staging         production
─────────────────────────────────────────
DatabaseEndpoint     db.staging.local  db.prod.internal
InstanceCount        2               10
AppVersion           1.4.2           1.3.8
─────────────────────────────────────────
3 differences found
```

---

## Configuration

stackdiff reads credentials and provider settings from your existing infrastructure configuration (e.g., AWS CLI profiles, environment variables).

---

## License

MIT © [Your Name](https://github.com/yourorg)