# -*- mode: Python -*-
# Builds and deploys the squint workers and UI to the kind dev cluster.
# The platform (Temporal, Milvus, ...) is deployed separately by `task create-dev-cluster`.
# Images are pushed to the registry advertised by the cluster's local-registry-hosting ConfigMap.

allow_k8s_contexts('kind-squint')
if k8s_context() != 'kind-squint':
    fail('expected kubectl context kind-squint, got %s' % k8s_context())

# `task preview` runs the production images, similar to `vite preview`
config.define_bool('preview')
PREVIEW = config.parse().get('preview', False)

# `task prune-images` removes old builds on demand
docker_prune_settings(disable=True)

NAMESPACE = 'squint'
PYTHON_SRC = 'squint/python'
JS_SRC = 'squint/javascript'
UI_SRC = JS_SRC + '/ui'
DB_SRC = JS_SRC + '/db'
WORKER_SRC = JS_SRC + '/worker'

# Workers run under debugpy on this port in the pod
DEBUG_PORT = 5678

WORKERS = {
    'ingest': {
        'debug_port': 5678,
    },
    'embed': {
        'values': [
            # Mounted at /mnt/models; `task download-models` fills it with the model and kernels
            'models.hostPath=/mnt/models',
            'env.MODEL_PATH=/mnt/models/NeoMME-260M-Retriever',
            # Read by the kernels library in place of a Hub download
            'env.LOCAL_KERNELS=kernels-community/flash-attn2=/mnt/models/kernels/flash-attn2',
        ],
        'debug_port': 5679,
    },
    'extract': {
        'debug_port': 5680,
    },
}

# Dependency changes need a full image rebuild rather than a live update
PACKAGE_MANIFESTS = [
    path + '/pyproject.toml'
    for path in listdir(PYTHON_SRC + '/packages')
    if os.path.exists(path + '/pyproject.toml')
]

# The same helmfile release that `task deploy` installs; services start once it has run
local_resource(
    'migrate',
    cmd='task migrate',
    deps=[DB_SRC + '/drizzle'],
    labels=['db'],
)

# temporal-worker-controller turns each WorkerDeployment into one Deployment per worker version.
# Each image rebuild is a new version; live updates keep the running one.
k8s_kind(
    'WorkerDeployment',
    image_json_path=[
        '{.spec.deployment.template.spec.containers[*].image}',
        '{.spec.deployment.template.spec.volumes[?(@.name=="devtools")].image.reference}',
    ],
    pod_readiness='wait',
)

# Mounted on the workers' PYTHONPATH in debug mode
if not PREVIEW:
    docker_build(
        'squint-devtools',
        PYTHON_SRC + '/devtools',
        only=['pyproject.toml', 'uv.lock', 'debug_worker.py'],
    )

def deploy_worker(app, deploy_dir, set_values=[], port_forwards=[]):
    """Deploys a worker image built as squint-<app> with the squint-worker chart."""
    values_file = deploy_dir + '/values.yaml'
    values = read_yaml(values_file, default={})
    k8s_yaml(helm(
        'infrastructure/squint-worker',
        name=app,
        namespace=NAMESPACE,
        values=[values_file] if os.path.exists(values_file) else [],
        set=[
            'image=squint-' + app,
            # Promote each rebuild straight away, and free a drained version's pods (and GPU)
            # as soon as its workflows finish
            'rollout.strategy=AllAtOnce',
            'sunset.scaledownDelay=0s',
            'sunset.deleteDelay=5m',
        ] + set_values,
    ))

    objects = [app + ':podmonitor']
    if values.get('autoscaling', {}).get('enabled'):
        objects.append(app + '-hpa:workerresourcetemplate')

    k8s_resource(
        app,
        objects=objects,
        port_forwards=port_forwards,
        resource_deps=['migrate'],
        labels=['workers'],
    )

for app, worker in WORKERS.items():
    app_src = PYTHON_SRC + '/apps/' + app
    deploy_dir = app_src + '/deploy'
    build_args = read_yaml(deploy_dir + '/build-args.yaml', default={})

    # The local packages are installed editable from /app/packages, so syncing source is enough
    # for the chart's debug mode to restart the worker with the edits, without a rebuild
    docker_build(
        'squint-' + app,
        PYTHON_SRC,
        dockerfile=PYTHON_SRC + '/Dockerfile',
        build_args=dict({'APP': app}, **build_args),
        only=['apps/' + app, 'packages'],
        ignore=['apps/' + app + '/deploy'],
        live_update=[] if PREVIEW else [
            fall_back_on([app_src + '/pyproject.toml', app_src + '/uv.lock'] + PACKAGE_MANIFESTS),
            sync(app_src, '/app/apps/' + app),
            sync(PYTHON_SRC + '/packages', '/app/packages'),
        ],
    )

    set_values = list(worker.get('values', []))
    port_forwards = []
    if not PREVIEW:
        set_values += ['debug=true', 'debugPort=%d' % DEBUG_PORT]
        port_forwards.append(port_forward(worker['debug_port'], DEBUG_PORT, name='debugpy'))

    # Attach with the "<app> (kind)" VS Code launch config
    deploy_worker(app, deploy_dir, set_values, port_forwards)

# The TypeScript worker restarts itself on synced source changes in its dev image, and serves the
# Node inspector on 9229 rather than using the chart's debugpy mode
docker_build(
    'squint-worker',
    JS_SRC,
    dockerfile=WORKER_SRC + '/Dockerfile',
    target='' if PREVIEW else 'dev',
    only=['worker', 'db', 'package.json', 'pnpm-lock.yaml', 'pnpm-workspace.yaml', '.npmrc'],
    ignore=['worker/deploy', 'db/drizzle'],
    live_update=[] if PREVIEW else [
        sync(WORKER_SRC + '/src', '/app/worker/src'),
        sync(DB_SRC + '/src', '/app/db/src'),
    ],
)

deploy_worker(
    'worker',
    WORKER_SRC + '/deploy',
    port_forwards=[] if PREVIEW else [port_forward(9230, 9229, name='inspector')],
)

# `task dev-hosts` points squint.loc at the gateway's load balancer IP
UI_ORIGIN = 'https://squint.loc'

local_resource('gateway-cert', cmd='task gateway-cert', labels=['ui'])

# Gives the gateway its external IP; runs for as long as Tilt does.
# The Gateway API CRDs are installed manually, so its gateway controller stays off.
local_resource(
    'load-balancer',
    serve_cmd='cloud-provider-kind --gateway-channel disabled',
    labels=['ui'],
)

# Vite's dev server watches the synced source, including the db package's schema, and hot reloads
# it. Other changes (dependencies, config) rebuild the image.
# In preview mode the Dockerfile's final stage runs the production build, and every change rebuilds.
docker_build(
    'squint-ui',
    JS_SRC,
    dockerfile=UI_SRC + '/Dockerfile',
    target='' if PREVIEW else 'dev',
    only=['ui', 'db', 'package.json', 'pnpm-lock.yaml', 'pnpm-workspace.yaml', '.npmrc'],
    ignore=['db/drizzle'],
    live_update=[] if PREVIEW else [
        sync(UI_SRC + '/src', '/app/ui/src'),
        sync(UI_SRC + '/static', '/app/ui/static'),
        sync(UI_SRC + '/scripts', '/app/ui/scripts'),
        sync(DB_SRC + '/src', '/app/db/src'),
    ],
)

k8s_yaml(helm(
    'infrastructure/squint-ui',
    name='ui',
    namespace=NAMESPACE,
    set=[
        'image=squint-ui',
        'route.enabled=true',
        'env.ORIGIN=' + UI_ORIGIN,
        # The dev admin account for `task create-admin` and `task remove-user`; the password Secret
        # comes from infrastructure/hooks/dev-squint-secrets.sh
        'env.ADMIN_EMAIL=admin@squint-docs.com',
        'envFromSecrets={admin}',
    ],
))

# Attach with the "ui" VS Code launch config
k8s_resource(
    'ui',
    objects=['ui:httproute'],
    resource_deps=['gateway-cert', 'load-balancer', 'migrate'],
    links=[link(UI_ORIGIN, 'squint')],
    port_forwards=[] if PREVIEW else [port_forward(9229, 9229, name='inspector')],
    labels=['ui'],
)

# Once per cluster; `task admin-credentials` prints the sign-in
local_resource(
    'create-admin',
    cmd='task create-admin',
    resource_deps=['ui'],
    auto_init=False,
    trigger_mode=TRIGGER_MODE_MANUAL,
    labels=['ui'],
)
