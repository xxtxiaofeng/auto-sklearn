# -*- encoding: utf-8 -*-
from __future__ import print_function
import os
import shlex
import subprocess

import lockfile

import autosklearn
from autosklearn.constants import *
from autosklearn.util import logging_ as logging


def submit_call(call, seed, logger, log_dir=None):
    logger.info('Calling: ' + call)
    call = shlex.split(call)

    if log_dir is None:
        proc = subprocess.Popen(call, stdout=open(os.devnull, 'w'))
    else:
        proc = subprocess.Popen(
            call,
            stdout=open(
                os.path.join(log_dir, 'ensemble_out_%d.log' % seed), 'w'),
            stderr=open(
                os.path.join(log_dir, 'ensemble_err_%d.log' % seed), 'w'))

    return proc


def run_ensemble_builder(tmp_dir, dataset_name, task_type, metric, limit,
                         output_dir, ensemble_size, ensemble_nbest, seed,
                         shared_mode):
    logger = logging.get_logger(__name__)

    if limit <= 0:
        # It makes no sense to start building ensembles_statistics
        return
    ensemble_script = 'python -m autosklearn.ensemble_selection_script'
    runsolver_exec = 'runsolver'
    delay = 5

    task_type = TASK_TYPES_TO_STRING[task_type]
    metric = METRIC_TO_STRING[metric]

    call = [ensemble_script,
         '--auto-sklearn-tmp-directory', tmp_dir,
         '--basename', dataset_name,
         '--task', task_type,
         '--metric', metric,
         '--limit', str(limit - 5),
         '--output-directory', output_dir,
         '--ensemble-size', str(ensemble_size),
         '--auto-sklearn-seed', str(seed)]
    if shared_mode:
        call.append('--shared-mode')

    call = ' '.join(call)

    # Runsolver does strange things if the time limit is negative. Set it to
    # be at least one (0 means infinity)
    limit = max(1, limit)

    # Now add runsolver command
    # runsolver_cmd = "%s --watcher-data /dev/null -W %d" % \
    #                (runsolver_exec, limit)
    runsolver_cmd = '%s --watcher-data /dev/null -W %d -d %d' % \
                    (runsolver_exec, limit, delay)
    call = runsolver_cmd + ' ' + call

    proc = submit_call(call, seed, logger, log_dir=tmp_dir)
    return proc
