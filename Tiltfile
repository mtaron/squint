# -*- mode: Python -*-
# Builds and deploys the squint workers to the kind dev cluster.
# The platform (Temporal, Milvus, ...) is deployed separately by `task create-dev-cluster`.
# Images are pushed to the registry advertised by the cluster's local-registry-hosting ConfigMap.

load('ext://restart_process', 'docker_build_with_restart')

allow_k8s_contexts('kind-squint')
if k8s_context() != 'kind-squint':
    fail('expected kubectl context kind-squint, got %s' % k8s_context())

NAMESPACE = 'squint'
PYTHON_SRC = 'src/python'

# Workers run under debugpy on this port in the pod
DEBUG_PORT = 5678

WORKERS = {
    'ingest': {
        'debug_port': 5678,
    },
    'embed': {
        'build_args': {
            'BASE_IMAGE': 'nvidia/cuda:13.4.2-base-ubuntu26.04',
            # torch.compile's Triton kernels are built with a C compiler against the Python headers
            'EXTRA_PACKAGES': 'gcc libc6-dev python3.14-dev',
        },
        'values': [
            'milvus.enabled=true',
            'gpu=1',
            # Mounted at /mnt/models; `task download-models` fills it with the model and kernels
            'models.hostPath=/mnt/models',
            'env.MODEL_PATH=/mnt/models/NeoMME-260M-Retriever',
            # Read by the kernels library in place of a Hub download
            'env.LOCAL_KERNELS=kernels-community/flash-attn2=/mnt/models/kernels/flash-attn2',
        ],
        'debug_port': 5679,
    },
    'extract': {
        'values': ['milvus.enabled=true'],
        'debug_port': 5680,
    },
}

# Dependency changes need a full image rebuild rather than a live update
PACKAGE_MANIFESTS = [
    path + '/pyproject.toml'
    for path in listdir(PYTHON_SRC + '/packages')
    if os.path.exists(path + '/pyproject.toml')
]

for app, worker in WORKERS.items():
    image = 'squint-' + app
    app_src = PYTHON_SRC + '/apps/' + app

    # The debug target installs the local packages editable from /app/packages, so
    # syncing source and restarting the process picks up edits without a rebuild
    docker_build_with_restart(
        image,
        PYTHON_SRC,
        dockerfile=PYTHON_SRC + '/Dockerfile',
        target='debug',
        build_args=dict({'APP': app}, **worker.get('build_args', {})),
        only=['apps/' + app, 'packages'],
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
        set=['image=' + image] + worker.get('values', []),
    ))

    # Attach with the "<app> (kind)" VS Code launch config
    k8s_resource(
        app,
        port_forwards=[port_forward(worker['debug_port'], DEBUG_PORT, name='debugpy')],
        labels=['workers'],
    )
