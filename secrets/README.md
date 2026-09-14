# secrets/

Empty on purpose, and denied on purpose.

`.claude/settings.json` denies reads of this directory and of `.env`. The
deny list is evaluated first, from any settings scope, and it cannot carry an
exception — which is the property that makes it worth using for exactly this
and not much else.

Ask the agent to read `.env` after lever 4 is applied and watch what comes
back. Then ask it to read this file.
