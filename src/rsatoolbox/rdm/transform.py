#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" transforms, which can be applied to RDMs
"""
from __future__ import annotations
from copy import deepcopy
import numpy as np
import networkx as nx
from scipy.stats import rankdata
from scipy.spatial.distance import squareform
from .rdms import RDMs


def rank_transform(rdms: RDMs, method='average'):
    """ applies a rank_transform and generates a new RDMs object
    This assigns a rank to each dissimilarity estimate in the RDM,
    deals with rank ties and saves ranks as new dissimilarity estimates.
    As an effect, all non-diagonal entries of the RDM will
    range from 1 to (n_dim²-n_dim)/2, if the RDM has the dimensions
    n_dim x n_dim.

    Args:
        rdms(RDMs): RDMs object
        method(String):
            controls how ranks are assigned to equal values
            options are: ‘average’, ‘min’, ‘max’, ‘dense’, ‘ordinal’

    Returns:
        rdms_new(RDMs): RDMs object with rank transformed dissimilarities

    """
    dissimilarities = rdms.get_vectors()
    dissimilarities = np.array([rankdata(dissimilarities[i], method=method)
                                for i in range(rdms.n_rdm)])
    measure = rdms.dissimilarity_measure or ''
    if '(ranks)' not in measure:
        measure = (measure + ' (ranks)').strip()
    rdms_new = RDMs(dissimilarities,
                    dissimilarity_measure=measure,
                    descriptors=deepcopy(rdms.descriptors),
                    rdm_descriptors=deepcopy(rdms.rdm_descriptors),
                    pattern_descriptors=deepcopy(rdms.pattern_descriptors))
    return rdms_new


def sqrt_transform(rdms):
    """ applies a square root transform and generates a new RDMs object
    This sets values blow 0 to 0 and takes a square root of each entry.
    It also adds a sqrt to the dissimilarity_measure entry.

    Args:
        rdms(RDMs): RDMs object

    Returns:
        rdms_new(RDMs): RDMs object with sqrt transformed dissimilarities

    """
    dissimilarities = rdms.get_vectors()
    dissimilarities[dissimilarities < 0] = 0
    dissimilarities = np.sqrt(dissimilarities)
    if rdms.dissimilarity_measure == 'squared euclidean':
        dissimilarity_measure = 'euclidean'
    elif rdms.dissimilarity_measure == 'squared mahalanobis':
        dissimilarity_measure = 'mahalanobis'
    else:
        dissimilarity_measure = 'sqrt of' + rdms.dissimilarity_measure
    rdms_new = RDMs(dissimilarities,
                    dissimilarity_measure=dissimilarity_measure,
                    descriptors=deepcopy(rdms.descriptors),
                    rdm_descriptors=deepcopy(rdms.rdm_descriptors),
                    pattern_descriptors=deepcopy(rdms.pattern_descriptors))
    return rdms_new


def positive_transform(rdms):
    """ sets all negative entries in an RDM to zero and returns a new RDMs

    Args:
        rdms(RDMs): RDMs object

    Returns:
        rdms_new(RDMs): RDMs object with sqrt transformed dissimilarities

    """
    dissimilarities = rdms.get_vectors()
    dissimilarities[dissimilarities < 0] = 0
    rdms_new = RDMs(dissimilarities,
                    dissimilarity_measure=rdms.dissimilarity_measure,
                    descriptors=deepcopy(rdms.descriptors),
                    rdm_descriptors=deepcopy(rdms.rdm_descriptors),
                    pattern_descriptors=deepcopy(rdms.pattern_descriptors))
    return rdms_new


def transform(rdms, fun):
    """ applies an arbitray function ``fun`` to the dissimilarities and
    returns a new RDMs object.

    Args:
        rdms(RDMs): RDMs object

    Returns:
        rdms_new(RDMs): RDMs object with sqrt transformed dissimilarities

    """
    dissimilarities = rdms.get_vectors()
    dissimilarities = fun(dissimilarities)
    meas = 'transformed ' + rdms.dissimilarity_measure
    rdms_new = RDMs(dissimilarities,
                    dissimilarity_measure=meas,
                    descriptors=deepcopy(rdms.descriptors),
                    rdm_descriptors=deepcopy(rdms.rdm_descriptors),
                    pattern_descriptors=deepcopy(rdms.pattern_descriptors))
    return rdms_new


def minmax_transform(rdms):
    '''applies a minmax transform to the dissimilarities and returns a new 
    RDMs object.
    
    Args:
        rdms(RDMs): RDMs object
    
    Returns:    
        rdms_new(RDMs): RDMs object with minmax transformed dissimilarities
    '''
    dissimilarities = rdms.get_vectors()
    d_max = dissimilarities.max()
    d_min = dissimilarities.min()
    dissimilarities = (dissimilarities - d_min) / (d_max - d_min)
    meas = 'minmax transformed ' + rdms.dissimilarity_measure
    rdms_new = RDMs(dissimilarities,
                    dissimilarity_measure=meas,
                    descriptors=deepcopy(rdms.descriptors),
                    rdm_descriptors=deepcopy(rdms.rdm_descriptors),
                    pattern_descriptors=deepcopy(rdms.pattern_descriptors))
    return rdms_new


def geotopological_transform(rdms, l, u):
    '''applies a geo-topological transform to the dissimilarities and returns 
    a new RDMs object. 
    
    Reference: Lin, B., & Kriegeskorte, N. (2023). The Topology and Geometry 
    of Neural Representations. arXiv preprint arXiv:2309.11028.
    
    Args:
        rdms(RDMs): RDMs object
        l(float): lower quantile
        u(float): upper quantile
    
    Returns:    
        rdms_new(RDMs): RDMs object with geotopological transformed dissimilarities
    '''
    dissimilarities = rdms.get_vectors()
    gt_min = np.quantile(dissimilarities, l)
    gt_max = np.quantile(dissimilarities, u)
    dissimilarities[dissimilarities < gt_min] = 0
    dissimilarities[(dissimilarities >= gt_min) & (dissimilarities <= gt_max)] = (
        dissimilarities[(dissimilarities >= gt_min) & (dissimilarities <= gt_max)] - gt_min
    ) / (gt_max - gt_min)
    dissimilarities[dissimilarities > gt_max] = 1
    meas = 'geo-topological transformed ' + rdms.dissimilarity_measure
    rdms_new = RDMs(dissimilarities,
                    dissimilarity_measure=meas,
                    descriptors=deepcopy(rdms.descriptors),
                    rdm_descriptors=deepcopy(rdms.rdm_descriptors),
                    pattern_descriptors=deepcopy(rdms.pattern_descriptors))
    return rdms_new


def geodesic_transform(rdms):
    '''applies a geodesic transform to the dissimilarities and returns a 
    new RDMs object. 
    
    Reference: Lin, B., & Kriegeskorte, N. (2023). The Topology and Geometry 
    of Neural Representations. arXiv preprint arXiv:2309.11028.
    
    Args:
        rdms(RDMs): RDMs object
    
    Returns:    
        rdms_new(RDMs): RDMs object with geodesic transformed dissimilarities
    '''
    dissimilarities = minmax_transform(rdms).get_vectors()
    for i in range(rdms.n_rdm):
        G = nx.from_numpy_array(squareform(dissimilarities[i]))
        long_edges = []
        long_edges = list(
            filter(lambda e: e[2] == 1, (e for e in G.edges.data("weight"))))
        le_ids = list(e[:2] for e in long_edges)
        G.remove_edges_from(le_ids)
        dissimilarities[i] = squareform(np.array(nx.floyd_warshall_numpy(G)))
    meas = 'geodesic transformed ' + rdms.dissimilarity_measure
    rdms_new = RDMs(dissimilarities,
                    dissimilarity_measure=meas,
                    descriptors=deepcopy(rdms.descriptors),
                    rdm_descriptors=deepcopy(rdms.rdm_descriptors),
                    pattern_descriptors=deepcopy(rdms.pattern_descriptors))
    return rdms_new
