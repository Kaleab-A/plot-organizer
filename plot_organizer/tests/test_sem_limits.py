"""Tests for SEM-aware shared limits calculation."""

import pandas as pd
from plot_organizer.services.plot_service import shared_limits_with_sem, shared_limits


def test_sem_limits_vs_raw_limits():
    """Test that SEM-aware limits are tighter than raw data limits."""
    # Create data with outliers that will be smoothed by SEM aggregation
    data = {
        'x': [1, 1, 1, 2, 2, 2] * 3,
        'y': [5, 10, 95, 15, 20, 90] * 3,  # Two outliers: 95 and 90
        'subject': ['s1', 's2', 's3'] * 6,
        'group': ['A'] * 9 + ['B'] * 9
    }
    df = pd.DataFrame(data)
    
    # Filter queries for groups
    filter_queries = [
        {'group': 'A'},
        {'group': 'B'}
    ]
    
    # Compute raw limits (old method)
    subsets = []
    for fq in filter_queries:
        subset = df
        for col, val in fq.items():
            subset = subset[subset[col] == val]
        subsets.append(subset)
    _, raw_ylim = shared_limits(subsets, 'x', 'y')
    
    # Compute SEM-aware limits (new method)
    _, sem_ylim = shared_limits_with_sem(df, filter_queries, 'x', 'y', 'subject')
    
    # Raw limits should see the outliers
    assert raw_ylim[0] == 5.0
    assert raw_ylim[1] == 95.0
    
    # SEM-aware limits should be tighter (means are closer together)
    assert sem_ylim[0] > raw_ylim[0]  # Lower bound is higher
    assert sem_ylim[1] < raw_ylim[1]  # Upper bound is lower
    
    # Verify the limits are reasonable (roughly around the means)
    # With subjects averaging: s1=[5,15], s2=[10,20], s3=[95,90]
    # Group A: x=1 mean of [5,10,95]~37, x=2 mean of [15,20,90]~42
    # These will be averaged across subjects first, so final should be tighter
    assert 0 < sem_ylim[0] < 50
    assert 20 < sem_ylim[1] < 100


def test_sem_limits_with_hue():
    """Test SEM-aware limits with hue grouping."""
    data = {
        'x': [1, 1, 1, 2, 2, 2] * 4,
        'y': [10, 12, 14, 20, 22, 24] * 2 + [30, 32, 34, 40, 42, 44] * 2,
        'subject': ['s1', 's2', 's3'] * 8,
        'condition': ['A'] * 6 + ['B'] * 6 + ['A'] * 6 + ['B'] * 6,
        'group': ['G1'] * 12 + ['G2'] * 12
    }
    df = pd.DataFrame(data)
    
    filter_queries = [{'group': 'G1'}, {'group': 'G2'}]
    
    _, ylim = shared_limits_with_sem(df, filter_queries, 'x', 'y', 'subject', hue='condition')
    
    # Should encompass both conditions across both groups
    # G1: condition A ~[10-24], condition B ~[30-44]
    # G2: condition A ~[10-24], condition B ~[30-44]
    assert ylim[0] < 15  # Should capture lower end with SEM
    assert ylim[1] > 40  # Should capture upper end with SEM


def test_sem_limits_no_sem_column():
    """Test that function works correctly when sem_column is None."""
    data = {
        'x': [1, 1, 2, 2] * 2,
        'y': [10, 12, 20, 22] * 2,
        'group': ['A'] * 4 + ['B'] * 4
    }
    df = pd.DataFrame(data)
    
    filter_queries = [{'group': 'A'}, {'group': 'B'}]
    
    _, ylim = shared_limits_with_sem(df, filter_queries, 'x', 'y', None)
    
    # Without SEM, should use aggregated means
    # A: x=1 mean=11, x=2 mean=21
    # B: x=1 mean=11, x=2 mean=21
    assert ylim[0] == 11.0
    assert ylim[1] == 21.0


def test_sem_limits_empty_subset():
    """Test that function handles empty subsets gracefully."""
    data = {
        'x': [1, 1, 2, 2],
        'y': [10, 12, 20, 22],
        'subject': ['s1', 's2', 's1', 's2'],
        'group': ['A', 'A', 'A', 'A']
    }
    df = pd.DataFrame(data)
    
    # One filter will produce empty results
    filter_queries = [{'group': 'A'}, {'group': 'B'}]
    
    _, ylim = shared_limits_with_sem(df, filter_queries, 'x', 'y', 'subject')
    
    # Should only use the non-empty subset
    assert ylim[0] < ylim[1]  # Valid range
    assert ylim[0] >= 0  # Reasonable values


def test_sem_limits_single_group():
    """Test that limits work correctly with a single group (no shared limits needed)."""
    data = {
        'x': [1, 1, 2, 2],
        'y': [10, 12, 20, 22],
        'subject': ['s1', 's2', 's1', 's2']
    }
    df = pd.DataFrame(data)
    
    # Single filter query
    filter_queries = [{}]
    
    _, ylim = shared_limits_with_sem(df, filter_queries, 'x', 'y', 'subject')
    
    # Should compute limits for this one group
    # After SEM aggregation: x=1 mean=11, x=2 mean=21
    # With SEM: roughly 11±0.7, 21±0.7
    assert 9 < ylim[0] < 12
    assert 20 < ylim[1] < 23

