## Configuration

Most explicit first:

1. **A config file tracked in the repo**, parsed into a frozen dataclass. This is the default for
   any deployment setting. Infrastructure becomes code-defined and diffable. (R3a-02)

2. **CLI arguments** for the inputs of a batch tool invoked by hand. `argparse`.

3. **Environment** for secrets and DB URLs, via `python-decouple`, not `os.environ`. (R2-06)

4. **`ALL_CAPS` constants** for tuning knobs that do not vary by deployment.

