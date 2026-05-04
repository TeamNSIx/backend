"""RBAC scope catalog and default role → permission maps for bootstrap."""

SUBJECTS = ('profile', 'conversation', 'roles')
ACTIONS = ('list', 'detail', 'create', 'update', 'delete')


def build_permission_descriptions() -> dict[str, str]:
    descriptions: dict[str, str] = {}
    for subject in SUBJECTS:
        for action in ACTIONS:
            scope = f'{subject}:{action}'
            descriptions[scope] = scope.replace(':', ' ')
    descriptions['roles:assign'] = 'Assign roles to users'
    return descriptions


PERMISSION_DESCRIPTIONS = build_permission_descriptions()

ALL_SCOPES = tuple(sorted(PERMISSION_DESCRIPTIONS))

# Default scopes for the public role (assigned on registration)
PUBLIC_ROLE_SCOPES: tuple[str, ...] = (
    'profile:detail',
    'conversation:list',
    'conversation:detail',
    'conversation:create',
    'conversation:update',
)
