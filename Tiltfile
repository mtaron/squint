# -*- mode: Python -*-
# Builds and deploys the squint workers and UI to the kind dev cluster.
# The platform (Temporal, Milvus, ...) is deployed separately by `task create-dev-cluster`.
# Images are pushed to the registry advertised by the cluster's local-registry-hosting ConfigMap.

allow_k8s_contexts('kind-squint')
if k8s_context() != 'kind-squint':
    fail('expected kubectl context kind-squint, got %s' % k8s_context())

NAMESPACE = 'squint'
PYTHON_SRC = 'squint/python'
UI_SRC = 'squint/javascript/ui'

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

RESTART_FILE = '/tmp/.restart-proc'

def docker_build_with_restart(ref, context, entrypoint, live_update, **kwargs):
    """Like ext://restart_process's docker_build_with_restart, but sets the restart wrapper as the
    image's ENTRYPOINT instead of overriding the container command, which Tilt can't do in CRDs."""
    base_ref = ref + '-base'
    docker_build(base_ref, context, **kwargs)
    docker_build(
        ref,
        context,
        dockerfile_contents='''
FROM tiltdev/restart-helper:2025-02-17 AS restart-helper
FROM {base}
RUN ["touch", "{file}"]
RUN ["chmod", "666", "{file}"]
COPY --from=restart-helper /tilt-restart-wrapper /
COPY --from=restart-helper /entr /
ENTRYPOINT {entrypoint}
'''.format(base=base_ref, file=RESTART_FILE, entrypoint=['/tilt-restart-wrapper', '--watch_file=' + RESTART_FILE] + entrypoint),
        only=kwargs.get('only', []),
        ignore=kwargs.get('ignore', []),
        # entr only reacts to writes, not timestamp changes
        live_update=live_update + [run('date > ' + RESTART_FILE)],
    )

# temporal-worker-controller turns each WorkerDeployment into one Deployment per worker version.
# Each image rebuild is a new version; live updates keep the running one.
k8s_kind(
    'WorkerDeployment',
    image_json_path=[
        '{.spec.deployment.template.spec.containers[*].image}',
        '{.spec.deployment.template.spec.volumes[?(@.name=="debugpy")].image.reference}',
    ],
    pod_readiness='wait',
)

docker_build(
    'squint-debugpy',
    PYTHON_SRC,
    ignore=['*'],
    dockerfile_contents='''
FROM ghcr.io/astral-sh/uv:python3.14-trixie-slim AS build
RUN uv pip install --target /debugpy --compile-bytecode debugpy
FROM scratch
COPY --from=build /debugpy /
''',
)

for app, worker in WORKERS.items():
    image = 'squint-' + app
    app_src = PYTHON_SRC + '/apps/' + app
    deploy_dir = app_src + '/deploy'
    values_file = deploy_dir + '/values.yaml'
    build_args = read_yaml(deploy_dir + '/build-args.yaml', default={})

    # The local packages are installed editable from /app/packages, so syncing
    # source and restarting the process picks up edits without a rebuild
    docker_build_with_restart(
        image,
        PYTHON_SRC,
        dockerfile=PYTHON_SRC + '/Dockerfile',
        build_args=dict({'APP': app}, **build_args),
        only=['apps/' + app, 'packages'],
        ignore=['apps/' + app + '/deploy'],
        # Frozen stdlib modules can make debugpy miss breakpoints
        entrypoint=['python', '-Xfrozen_modules=off', '-m', 'debugpy', '--listen', '0.0.0.0:%d' % DEBUG_PORT, 'main.py'],
        live_update=[
            fall_back_on([app_src + '/pyproject.toml', app_src + '/uv.lock'] + PACKAGE_MANIFESTS),
            sync(app_src, '/app/apps/' + app),
            sync(PYTHON_SRC + '/packages', '/app/packages'),
        ],
    )

    values = read_yaml(values_file, default={})
    k8s_yaml(helm(
        'infrastructure/squint-worker',
        name=app,
        namespace=NAMESPACE,
        values=[values_file] if os.path.exists(values_file) else [],
        set=[
            'image=' + image,
            'debug=true',
            # Promote each rebuild straight away, and free a drained version's pods (and GPU)
            # as soon as its workflows finish
            'rollout.strategy=AllAtOnce',
            'sunset.scaledownDelay=0s',
            'sunset.deleteDelay=5m',
        ] + worker.get('values', []),
    ))

    objects = [app + ':podmonitor']
    if values.get('autoscaling', {}).get('enabled'):
        objects.append(app + '-hpa:workerresourcetemplate')

    # Attach with the "<app> (kind)" VS Code launch config
    k8s_resource(
        app,
        objects=objects,
        port_forwards=[port_forward(worker['debug_port'], DEBUG_PORT, name='debugpy')],
        labels=['workers'],
    )

# `task dev-hosts` points squint.loc at the gateway's load balancer IP
UI_ORIGIN = 'https://squint.loc'

local_resource('gateway-cert', cmd='task gateway-cert', labels=['ui'])

# Vite's dev server watches the synced source and hot reloads it. Changes outside src/ and
# static/ (dependencies, config, migrations) rebuild the image, and the new pod migrates on start.
docker_build(
    'squint-ui',
    UI_SRC,
    target='dev',
    live_update=[
        sync(UI_SRC + '/src', '/app/src'),
        sync(UI_SRC + '/static', '/app/static'),
    ],
)

k8s_yaml(helm(
    'infrastructure/squint-ui',
    name='ui',
    namespace=NAMESPACE,
    set=['image=squint-ui', 'route.enabled=true', 'env.ORIGIN=' + UI_ORIGIN],
))

# Attach with the "ui" VS Code launch config
k8s_resource(
    'ui',
    objects=['ui:httproute'],
    resource_deps=['gateway-cert'],
    links=[link(UI_ORIGIN, 'squint')],
    port_forwards=[port_forward(9229, 9229, name='inspector')],
    labels=['ui'],
)
