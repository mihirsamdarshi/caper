"""Functions for caper init subcommand

Author:
    Jin Lee (leepc12@gmail.com) at ENCODE-DCC
"""

import os
import sys
from autouri import AutoURI, AbsPath
from .caper_backend import BACKENDS, BACKENDS_WITH_ALIASES
from .caper_backend import BACKEND_GCP, BACKEND_AWS, BACKEND_LOCAL
from .caper_backend import BACKEND_SLURM, BACKEND_SGE, BACKEND_PBS
from .caper_backend import BACKEND_ALIAS_LOCAL
from .caper_backend import BACKEND_ALIAS_GOOGLE, BACKEND_ALIAS_AMAZON
from .caper_backend import BACKEND_ALIAS_SHERLOCK, BACKEND_ALIAS_SCG


DEFAULT_CROMWELL_JAR = 'https://github.com/broadinstitute/cromwell/releases/download/47/cromwell-47.jar'
DEFAULT_WOMTOOL_JAR = 'https://github.com/broadinstitute/cromwell/releases/download/47/womtool-47.jar'
DEFAULT_CROMWELL_JAR_INSTALL_DIR = '~/.caper/cromwell_jar'
DEFAULT_WOMTOOL_JAR_INSTALL_DIR = '~/.caper/womtool_jar'

CONF_CONTENTS_LOCAL_HASH_STRAT = """
# Hashing strategy for call-caching (3 choices)
# This parameter is for local (local/slurm/sge/pbs) backend only.
# This is important for re-using outputs from previous/failed workflows.
# "file" method has been default for Caper <= 0.8.2, which is slow.
# Cache will miss if different strategy is used.
# So we will keep "file" as default to be compatible with
# old metadata DB generated with Caper <= 0.8.2.
# But "path" is recommended for new users.
# So we will make "path" default here.
#   file: md5sum hash (slow).
#   path: path.
#   path+modtime: path + mtime.
local-hash-strat=path
"""

CONF_CONTENTS_TMP_DIR = """
# Temporary cache directory.
# DO NOT USE /tmp. Use local absolute path here.
# Caper stores important temporary/cached files here.
# If not defined, Caper will make .caper_tmp/ on CWD
# or your local output directory (--out-dir).
tmp-dir=
"""

DEFAULT_CONF_CONTENTS_LOCAL = """
backend=local
""" + CONF_CONTENTS_LOCAL_HASH_STRAT + CONF_CONTENTS_TMP_DIR

DEFAULT_CONF_CONTENTS_SHERLOCK = """
backend=slurm
slurm-partition=

# IMPORTANT warning for Stanford Sherlock cluster
# ====================================================================
# DO NOT install any codes/executables
# (java, conda, python, caper, pipeline's WDL, pipeline's Conda env, ...) on $SCRATCH or $OAK.
# You will see Segmentation Fault errors.
# Install all executables on $HOME or $PI_HOME instead.
# It's STILL OKAY to read input data from and write outputs to $SCRATCH or $OAK.
# ====================================================================
""" + CONF_CONTENTS_LOCAL_HASH_STRAT + CONF_CONTENTS_TMP_DIR

DEFAULT_CONF_CONTENTS_SCG = """
backend=slurm
slurm-account=

""" + CONF_CONTENTS_LOCAL_HASH_STRAT + CONF_CONTENTS_TMP_DIR

DEFAULT_CONF_CONTENTS_SLURM = """
backend=slurm

# define one of the followings (or both) according to your
# cluster's SLURM configuration.
slurm-partition=
slurm-account=
""" + CONF_CONTENTS_LOCAL_HASH_STRAT + CONF_CONTENTS_TMP_DIR

DEFAULT_CONF_CONTENTS_SGE = """
backend=sge
sge-pe=
""" + CONF_CONTENTS_LOCAL_HASH_STRAT + CONF_CONTENTS_TMP_DIR

DEFAULT_CONF_CONTENTS_PBS = """
backend=pbs
""" + CONF_CONTENTS_LOCAL_HASH_STRAT + CONF_CONTENTS_TMP_DIR

DEFAULT_CONF_CONTENTS_AWS = """
backend=aws
aws-batch-arn=
aws-region=
out-s3-bucket=
""" + CONF_CONTENTS_TMP_DIR

DEFAULT_CONF_CONTENTS_GCP = """
backend=gcp
gcp-prj=
out-gcs-bucket=

# Call-cached outputs will be duplicated by making a copy or reference
#   reference: refer to old output file in metadata.json file.
#   copy: make a copy.
gcp-call-caching-dup-strat=
""" + CONF_CONTENTS_TMP_DIR


def install_cromwell_jar(uri):
    """Download cromwell-X.jar
    """
    u = AutoURI(uri)
    if isinstance(u, AbsPath):
        return u.uri
    print('Downloading Cromwell JAR... {f}'.format(f=uri), file=sys.stderr)
    path = os.path.join(
        os.path.expanduser(DEFAULT_CROMWELL_JAR_INSTALL_DIR),
        os.path.basename(uri))
    return u.cp(path)


def install_womtool_jar(uri):
    """Download womtool-X.jar
    """
    u = AutoURI(uri)
    if isinstance(u, AbsPath):
        return u.uri
    print('Downloading Womtool JAR... {f}'.format(f=uri), file=sys.stderr)
    path = os.path.join(
        os.path.expanduser(DEFAULT_WOMTOOL_JAR_INSTALL_DIR),
        os.path.basename(uri))
    return u.cp(path)


def init_caper_conf(args):
    """Initialize conf file for a given platform.
    Also, download/install Cromwell/Womtool JARs.
    """
    backend = args.get('platform')
    assert(backend in BACKENDS_WITH_ALIASES)
    if backend in (BACKEND_LOCAL, BACKEND_ALIAS_LOCAL):
        contents = DEFAULT_CONF_CONTENTS_LOCAL
    elif backend == BACKEND_ALIAS_SHERLOCK:
        contents = DEFAULT_CONF_CONTENTS_SHERLOCK
    elif backend == BACKEND_ALIAS_SCG:
        contents = DEFAULT_CONF_CONTENTS_SCG
    elif backend == BACKEND_SLURM:
        contents = DEFAULT_CONF_CONTENTS_SLURM
    elif backend == BACKEND_SGE:
        contents = DEFAULT_CONF_CONTENTS_SGE
    elif backend == BACKEND_PBS:
        contents = DEFAULT_CONF_CONTENTS_PBS
    elif backend in (BACKEND_GCP, BACKEND_ALIAS_GOOGLE):
        contents = DEFAULT_CONF_CONTENTS_GCP
    elif backend in (BACKEND_AWS, BACKEND_ALIAS_AMAZON):
        contents = DEFAULT_CONF_CONTENTS_AWS
    else:
        raise Exception('Unsupported platform/backend/alias.')

    conf_file = os.path.expanduser(args.get('conf'))
    with open(conf_file, 'w') as fp:
        fp.write(contents + '\n')
        fp.write('{key}={val}\n'.format(
            key='cromwell',
            val=install_cromwell_jar(DEFAULT_CROMWELL_JAR)))
        fp.write('{key}={val}\n'.format(
            key='womtool',
            val=install_womtool_jar(DEFAULT_WOMTOOL_JAR)))
