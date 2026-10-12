# -*- mode: Python -*-
# Builds and deploys the squint workers to the kind dev cluster.
# The platform (Temporal, Milvus, ...) is deployed separately by `task create-dev-cluster`.
# Images are pushed to the registry advertised by the cluster's local-registry-hosting ConfigMap.

load('ext://restart_process', 'docker_build_with_restart')

allow_k8s_contexts('kind-squint')
if k8s_context() != 'kind-squint':
    fail('expected kubectl context kind-squint, got %s' % k8s_context())

NAMESPACE = 'squint'
PYTHON_SRC = 'squint/python'

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

    k8s_yaml(helm(
        'infrastructure/squint-worker',
        name=app,
        namespace=NAMESPACE,
        values=[values_file] if os.path.exists(values_file) else [],
        set=['image=' + image, 'debug=true'] + worker.get('values', []),
    ))

    # Attach with the "<app> (kind)" VS Code launch config
    k8s_resource(
        app,
        port_forwards=[port_forward(worker['debug_port'], DEBUG_PORT, name='debugpy')],
        labels=['workers'],
    )
