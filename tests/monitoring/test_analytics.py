"""
Tests for analytics module.
"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from src.monitoring.analytics import (
    OfferAnalytics,
    PerformanceAnalytics,
    CustomerAnalytics,
    generate_analytics_report
)


def test_offer_analytics_initialization():
    """Test offer analytics initialization."""
    analytics = OfferAnalytics(lookback_days=30)
    assert analytics.lookback_days == 30


def test_analyze_offer_performance(sample_offer_events, sample_customer_segments):
    """Test offer performance analysis."""
    analytics = OfferAnalytics()
    performance = analytics.analyze_offer_performance(
        sample_offer_events,
        sample_customer_segments
    )
    
    # Check structure
    assert 'conversion_rates' in performance
    assert 'segment_performance' in performance
    assert 'offer_type_performance' in performance
    assert 'time_period' in performance
    
    # Check conversion rates
    rates = performance['conversion_rates']
    assert 'view_rate' in rates
    assert 'click_rate' in rates
    assert 'redemption_rate' in rates
    assert all(0 <= rate <= 1 for rate in rates.values())
    
    # Check time period
    assert 'start' in performance['time_period']
    assert 'end' in performance['time_period']
    assert 'days' in performance['time_period']


def test_analyze_segment_performance(sample_offer_events, sample_customer_segments):
    """Test segment performance analysis."""
    analytics = OfferAnalytics()
    performance = analytics._analyze_segment_performance(
        sample_offer_events,
        sample_customer_segments
    )
    
    assert len(performance) > 0
    
    # Check metrics for first segment
    first_segment = list(performance.keys())[0]
    segment_metrics = performance[first_segment]
    
    assert 'offer_count' in segment_metrics
    assert 'view_rate' in segment_metrics
    assert 'redemption_rate' in segment_metrics
    assert 'average_value' in segment_metrics


def test_analyze_offer_types(sample_offer_events):
    """Test offer type performance analysis."""
    analytics = OfferAnalytics()
    performance = analytics._analyze_offer_types(sample_offer_events)
    
    assert len(performance) > 0
    
    # Check metrics for first offer type
    first_type = list(performance.keys())[0]
    type_metrics = performance[first_type]
    
    assert 'count' in type_metrics
    assert 'view_rate' in type_metrics
    assert 'redemption_rate' in type_metrics
    assert 'average_value' in type_metrics


def test_api_performance_analysis(sample_api_metrics):
    """Test API performance analysis."""
    analytics = PerformanceAnalytics()
    performance = analytics.analyze_api_performance(sample_api_metrics)
    
    assert 'request_count' in performance
    assert 'error_rate' in performance
    assert 'latency' in performance
    assert 'endpoints' in performance
    
    # Check latency metrics
    latency = performance['latency']
    assert 'p50' in latency
    assert 'p90' in latency
    assert 'p99' in latency
    
    # Check endpoint metrics
    assert len(performance['endpoints']) > 0
    first_endpoint = list(performance['endpoints'].keys())[0]
    endpoint_metrics = performance['endpoints'][first_endpoint]
    
    assert 'request_count' in endpoint_metrics
    assert 'error_rate' in endpoint_metrics
    assert 'average_latency' in endpoint_metrics
    assert 'slow_requests' in endpoint_metrics


def test_model_performance_analysis(sample_model_metrics):
    """Test model performance analysis."""
    analytics = PerformanceAnalytics()
    performance = analytics.analyze_model_performance(sample_model_metrics)
    
    assert len(performance) > 0
    
    # Check metrics for first model
    first_model = list(performance.keys())[0]
    model_metrics = performance[first_model]
    
    assert 'prediction_count' in model_metrics
    assert 'average_latency' in model_metrics
    assert 'p95_latency' in model_metrics
    assert 'max_latency' in model_metrics


def test_customer_engagement_analysis(sample_offer_events, sample_customer_segments):
    """Test customer engagement analysis."""
    analytics = CustomerAnalytics()
    engagement = analytics.analyze_customer_engagement(
        sample_offer_events,
        sample_customer_segments
    )
    
    assert 'active_customers' in engagement
    assert 'events_per_customer' in engagement
    assert 'segment_engagement' in engagement
    assert 'time_series' in engagement
    
    # Check time series data
    time_series = engagement['time_series']
    assert 'dates' in time_series
    assert 'active_customers' in time_series
    assert 'event_count' in time_series
    assert 'average_points' in time_series


def test_segment_engagement_analysis(sample_offer_events):
    """Test segment engagement analysis."""
    analytics = CustomerAnalytics()
    engagement = analytics._analyze_segment_engagement(sample_offer_events)
    
    assert len(engagement) > 0
    
    # Check metrics for first segment
    first_segment = list(engagement.keys())[0]
    segment_metrics = engagement[first_segment]
    
    assert 'customer_count' in segment_metrics
    assert 'events_per_customer' in segment_metrics
    assert 'average_points_balance' in segment_metrics
    assert 'active_percentage' in segment_metrics


def test_engagement_timeseries(sample_offer_events):
    """Test engagement time series creation."""
    analytics = CustomerAnalytics()
    time_series = analytics._create_engagement_timeseries(sample_offer_events)
    
    assert 'dates' in time_series
    assert 'active_customers' in time_series
    assert 'event_count' in time_series
    assert 'average_points' in time_series
    
    assert len(time_series['dates']) == len(time_series['active_customers'])
    assert len(time_series['dates']) == len(time_series['event_count'])
    assert len(time_series['dates']) == len(time_series['average_points'])


def test_generate_analytics_report(
    sample_offer_events,
    sample_customer_segments,
    sample_api_metrics,
    tmp_path
):
    """Test analytics report generation."""
    # Generate component analytics
    offer_analytics = OfferAnalytics().analyze_offer_performance(
        sample_offer_events,
        sample_customer_segments
    )
    
    performance_analytics = PerformanceAnalytics().analyze_api_performance(
        sample_api_metrics
    )
    
    customer_analytics = CustomerAnalytics().analyze_customer_engagement(
        sample_offer_events,
        sample_customer_segments
    )
    
    # Generate report
    output_file = tmp_path / "analytics_report.json"
    report = generate_analytics_report(
        offer_analytics,
        performance_analytics,
        customer_analytics,
        str(output_file)
    )
    
    # Check report structure
    assert 'generated_at' in report
    assert 'offer_performance' in report
    assert 'system_performance' in report
    assert 'customer_engagement' in report
    assert 'summary' in report
    
    # Check summary metrics
    summary = report['summary']
    assert 'total_offers' in summary
    assert 'active_customers' in summary
    assert 'overall_redemption_rate' in summary
    assert 'system_error_rate' in summary
    
    # Check file was created
    assert output_file.exists()


def test_analytics_with_empty_data():
    """Test analytics with empty data."""
    empty_data = pd.DataFrame()
    
    # Test offer analytics
    offer_analytics = OfferAnalytics()
    performance = offer_analytics.analyze_offer_performance(empty_data, empty_data)
    assert performance['conversion_rates'] == {}
    
    # Test performance analytics
    performance_analytics = PerformanceAnalytics()
    with pytest.raises(Exception):
        performance_analytics.analyze_api_performance(empty_data)
    
    # Test customer analytics
    customer_analytics = CustomerAnalytics()
    engagement = customer_analytics.analyze_customer_engagement(empty_data, empty_data)
    assert engagement['active_customers'] == 0 