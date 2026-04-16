# Config Schema — [Automation Name]

Fields the client module must supply to activate this template.

| Field | Type | Example | Required |
|---|---|---|---|
| `crm_system` | string | `ghl` | yes |
| `outbound_channel` | enum(email,sms,both) | `both` | yes |
|  |  |  |  |

## Optional overrides

| Field | Default | Override when |
|---|---|---|
|  |  |  |

## Secrets required

- `SECRET_NAME_1` — what it's for
